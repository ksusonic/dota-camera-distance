import configparser
import os
import re
import struct
import time
import traceback
import winreg
import vdf
import requests

DOTA_APP_ID = "570"
DEFAULT_HEX_STRING = "00 00 00 00 00 00 2E 40 00 00 96 44 00 00 E1 44"
SERVER_HEX_STRING_LINK = "https://raw.githubusercontent.com/searayeah/dota-camera-distance/main/current_hex_string"
DEFAULT_DISTANCE = "1200"
STEAM_REGISTRY_KEY = os.path.join("SOFTWARE", "WOW6432Node", "Valve", "Steam")
CLIENT_DLL_PATH = os.path.join(
    "steamapps", "common", "dota 2 beta", "game", "dota", "bin", "win64", "client.dll"
)
LIBRARY_FOLDERS_PATH = os.path.join("steamapps", "libraryfolders.vdf")
APP_MANIFEST_PATH = os.path.join("steamapps", f"appmanifest_{DOTA_APP_ID}.acf")


def set_distance(hex_string, distance, client_dll_path):
    # First of all, it is important to notice that distance value is only
    # 8 numbers long, but 8 numbers is not enough to determine its exact location,
    # as there can be more than one occurence of its sequence.
    # Therefore, we use big strings e.g 00 00 00 00 00 00 2E 40 00 00 96 44 00 00 E1 44.

    hex_string = hex_string.lower().replace(" ", "")

    # Converting DEFAULT_DISTANCE of 1200 to hex format.
    default_distance_hex = struct.pack("f", float(DEFAULT_DISTANCE)).hex()

    # Converting desired distance to hex format.
    distance_hex = struct.pack("f", float(distance)).hex()
    distance_hex_length = len(distance_hex)  # this might be unnecessary, always 8

    # Find the location of default distance (00 00 96 44 = 1200)
    # in hex_string (e.g 0000000000002E40 00 00 96 44 0000E144).
    # hex_string is not hardcoded as it is changed from patch to patch.
    # This 8 numbers can be at various positions (start, middle, end, etc.).
    # By doing this, the position of this 8 numbers is remembered by index
    # and this allows to find and change distance regardless of its current value.
    distance_index = hex_string.find(default_distance_hex)

    # Constructing regular expression to find the position in client.dll file.
    hex_string_regex = re.compile(
        hex_string[:distance_index]
        + f"\w{{{distance_hex_length}}}"  # regex \w{8} means any 8 characters [a-zA-Z0-9_]
        + hex_string[distance_index + distance_hex_length :]
    )

    # Constructing string that would be used for replacement.
    distance_hex_string = (
        hex_string[:distance_index]
        + distance_hex
        + hex_string[distance_index + distance_hex_length :]
    )

    with open(client_dll_path, "rb") as f:
        client_dll_hex = f.read().hex()

    # Replacing
    client_dll_hex_new, changes_count = re.subn(
        hex_string_regex, distance_hex_string, client_dll_hex, 1
    )

    # If there are no changes, that means that current hex string is not present in
    # client.dll file and needs to be updated.
    # This usually happens when Valve release big updates to the game.
    if changes_count == 0:
        raise Exception(
            "Couldn't find the hex value in client.dll file. Valve might have changed it."
        )

    print(f"Old: {re.search(hex_string_regex, client_dll_hex).group()}")
    print(f"New: {re.search(hex_string_regex, client_dll_hex_new).group()}")

    with open(client_dll_path, "wb") as f:
        f.write(bytes.fromhex(client_dll_hex_new))


def get_steam_path():
    # Getting Steam path from Windows Registry.
    # This does not guarantee finding Dota 2 folder.
    hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, STEAM_REGISTRY_KEY)
    steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
    winreg.CloseKey(hkey)
    return steam_path


def get_steam_library_path(steam_path):
    # Dota 2 install path is stored in libraryfolders.vdf file.
    # Its "path" variable needs to be checked as
    # Dota and Steam can have different install locations.
    library_folders_path = os.path.join(steam_path, LIBRARY_FOLDERS_PATH)
    library_folders = vdf.load(open(library_folders_path))["libraryfolders"]
    for key in library_folders:
        if DOTA_APP_ID in library_folders[key]["apps"]:
            return library_folders[key]["path"]


def dota_was_updating(steam_library_path):
    # Dota 2 status is stored in app_manifest.acf file under the variable "StateFlags".
    # If "StateFlags" is '4' that means that Dota is updated/installed
    # and ready to launch.
    app_manifest_path = os.path.join(steam_library_path, APP_MANIFEST_PATH)
    app_manifest = vdf.load(open(app_manifest_path))
    app_status = app_manifest["AppState"]["StateFlags"]
    if app_status != "4":
        while app_status != "4":
            print(f"Waiting for Dota 2 to get updates, status: {app_status}", end="\r")
            time.sleep(1)
            app_manifest = vdf.load(open(app_manifest_path))
            app_status = app_manifest["AppState"]["StateFlags"]
        print()
        return True
    else:
        return False


def get_current_hex_string():
    # Retrieve current hex string. This is done to avoid hardcoding
    # this value and enable updating it through Github.
    try:
        response = requests.get(SERVER_HEX_STRING_LINK)
        response.raise_for_status()
        print("String received from GitHub")
        return response.text
    except requests.exceptions.RequestException as e:
        print(e)
        print("Couldn't receive string from GitHub, using the default one")
        return DEFAULT_HEX_STRING


def set_config():
    config_path = os.path.join(os.getcwd(), "config.ini")
    config_file = configparser.ConfigParser()
    config_file.read(config_path)

    if "DOTA-CAMERA-DISTANCE" not in config_file:
        config_file["DOTA-CAMERA-DISTANCE"] = {}

    config = config_file["DOTA-CAMERA-DISTANCE"]

    if "receive_type" not in config or not config["receive_type"]:
        config[
            '# "auto"'
        ] = 'automatically get string, "manual" = set the string manually'
        config["receive_type"] = "auto"
    print(f"Receive type: {config['receive_type']}")

    # I will update the string through github current_hex_string file
    # but if you obtained the new string faster than me, you can
    # set this config variable to "manual", set your manual string, and the program won't update it
    # automatically every time you launch it.
    if (
        config["receive_type"].lower() == "auto"
        or "hex_string" not in config
        or not config["hex_string"]
    ):
        config["hex_string"] = get_current_hex_string()
    print(f"Search hex string: {config['hex_string']}")

    if "distance" not in config or not config["distance"]:
        config["distance"] = (
            input("Enter distance[default 1200, recommended 1400]: ")
            or DEFAULT_DISTANCE
        )
    print(f"Distance: {config['distance']}")

    if "steam_path" not in config or not config["steam_path"]:
        config["steam_path"] = get_steam_path()
    print(f"Steam path: {config['steam_path']}")

    if "steam_library_path" not in config or not config["steam_library_path"]:
        config["steam_library_path"] = get_steam_library_path(config["steam_path"])
    print(f"Steam library path: {config['steam_library_path']}")

    if "client_dll_path" not in config or not config["client_dll_path"]:
        config["client_dll_path"] = os.path.join(
            config["steam_library_path"], CLIENT_DLL_PATH
        )
    print(f"Client.dll path: {config['client_dll_path']}")

    with open(config_path, "w") as configfile:
        config_file.write(configfile)
    print(f"Updated {config_path}")

    return (
        config["receive_type"],
        config["hex_string"],
        config["distance"],
        config["steam_path"],
        config["steam_library_path"],
        config["client_dll_path"],
    )


def main():
    (
        receive_type,
        hex_string,
        distance,
        steam_path,
        steam_library_path,
        client_dll_path,
    ) = set_config()

    set_distance(hex_string, distance, client_dll_path)
    os.startfile(f"steam://rungameid/{DOTA_APP_ID}")  # windows only
    print("Launching Dota 2 ...")

    # When launching Dota for the first time it might get updates,
    # so client.dll needs to be rewritten again
    if dota_was_updating(steam_library_path):
        set_distance(hex_string, distance, client_dll_path)
        print('Press "Play game"')


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print(
            "Program crashed, send me a screenshot via "
            + "https://github.com/searayeah/dota-camera-distance/issues"
        )
    finally:
        for i in range(5, 0, -1):
            print(f"Exit in: {i}", end="\r")
            time.sleep(1)
