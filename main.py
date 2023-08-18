import configparser
import os
import re
import struct
import time
import logging
import vdf
import requests
import sys

# logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Version: 5.0")
logger.info(f"OS: {sys.platform}")

# constants
DOTA_APP_ID = "570"
DOTA_URL = f"steam://rungameid/{DOTA_APP_ID}"

LIBRARY_FOLDERS_PATH = os.path.join("steamapps", "libraryfolders.vdf")
APP_MANIFEST_PATH = os.path.join("steamapps", f"appmanifest_{DOTA_APP_ID}.acf")
BIN_PATH = os.path.join("steamapps", "common", "dota 2 beta", "game", "dota", "bin")

DEFAULT_DISTANCE = "1200"
SERVER_LINK = "https://raw.githubusercontent.com/searayeah/dota-camera-distance/main/"

if sys.platform.startswith("win32"):
    import winreg

    DEFAULT_HEX_STRING = "00 00 AE 42 00 00 96 44 00 00 C8 44 00 40 9C 45"
    SERVER_HEX_STRING_LINK = SERVER_LINK + "current_hex_string"

    STEAM_REGISTRY_KEY = os.path.join("SOFTWARE", "WOW6432Node", "Valve", "Steam")
    SHARED_LIBRARY_PATH = os.path.join(BIN_PATH, "win64", "client.dll")

    def get_steam_path():
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, STEAM_REGISTRY_KEY)
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
        winreg.CloseKey(hkey)
        logger.debug(
            f"Retrieved Steam path: {steam_path} from winreg: {STEAM_REGISTRY_KEY}"
        )
        return steam_path

    def start_game():
        os.startfile(DOTA_URL)

elif sys.platform.startswith("linux"):
    DEFAULT_HEX_STRING = "00 00 AF 43 00 80 3B 44 00 00 96 44 33 33 33 3F"

    SERVER_HEX_STRING_LINK = SERVER_LINK + "current_hex_string_linux"
    SHARED_LIBRARY_PATH = os.path.join(BIN_PATH, "linuxsteamrt64", "libclient.so")

    def get_steam_path():
        steam_path = os.path.expanduser(os.path.join("~", ".steam", "steam"))
        logger.debug(f"Retrieved Steam path: {steam_path}")
        return steam_path

    def start_game():
        os.system(f"steam {DOTA_URL}")

elif sys.platform.startswith("darwin"):
    DEFAULT_HEX_STRING = "00 00 7A 43 00 80 09 44 00 96 44 00 00 C8 44"

    SERVER_HEX_STRING_LINK = SERVER_LINK + "current_hex_string_macos"
    SHARED_LIBRARY_PATH = os.path.join(BIN_PATH, "osx64", "libclient.dylib")

    def get_steam_path():
        steam_path = os.path.expanduser(
            os.path.join("~", "Library", "Application Support", "Steam")
        )
        logger.debug(f"Retrieved Steam path: {steam_path}")
        return steam_path

    def start_game():
        os.system(f"steam {DOTA_URL}")

else:
    raise Exception("OS not supported")


def set_distance(hex_string, distance, shared_library_path):
    hex_string = hex_string.lower().replace(" ", "")
    hex_string_length = len(hex_string)

    if hex_string_length <= 8:
        raise Exception(
            f"Hex string {hex_string} is only {hex_string_length} symbols long,"
            " which makes search inaccurate, as there is certainly"
            " more than one occurences of that string in shared library file."
            " Please update hex code to have at least 24 symbols."
        )
    elif hex_string_length <= 16:
        logger.critical(
            f"Hex string {hex_string} is only {hex_string_length} symbols long"
            " which makes search inaccurate, as there might be"
            " more than one occurences of that string in shared library file."
            " Please update hex code to have at least 24 symbols."
        )

    default_distance_hex = struct.pack("f", float(DEFAULT_DISTANCE)).hex()
    distance_hex = struct.pack("f", float(distance)).hex()
    distance_hex_length = len(distance_hex)
    distance_index = hex_string.find(default_distance_hex)

    if distance_index == -1:
        raise Exception(
            f"Default hex distance {default_distance_hex}"
            f" is not found in the hex string {hex_string}"
        )
    elif distance_index == 0:
        logger.warning(
            f"Hex string {hex_string} starting with default distance"
            f" code {default_distance_hex} makes search a lot slower."
            " Please shift the code, so it starts with other symbols"
        )

    hex_string_regex = re.compile(
        hex_string[:distance_index]
        + f"\w{{{distance_hex_length}}}"  # regex \w{8} means any 8 characters [a-zA-Z0-9_]
        + hex_string[distance_index + distance_hex_length :]
    )
    logger.debug(f"Regex code: {hex_string_regex}")

    distance_hex_string = (
        hex_string[:distance_index]
        + distance_hex
        + hex_string[distance_index + distance_hex_length :]
    )
    logger.debug(f"Replacement string: {distance_hex_string}")

    with open(shared_library_path, "rb") as f:
        shared_library_hex = f.read().hex()
    logger.debug(f"Read: {shared_library_path}")

    matches = re.findall(hex_string_regex, shared_library_hex)
    matches_count = len(matches)
    logger.debug(f"Matches count: {matches_count}. Matches: {matches}")

    if matches_count == 0:
        raise Exception(
            "Couldn't find the hex value in shared library file."
            " Valve might have changed it."
        )
    elif matches_count > 1:
        raise Exception(
            f"Hex string {hex_string} is not precise enough to clearly find"
            f" it's location in shared library file. Currently found {matches_count}"
            " matches. Please, update the string's length to be more precise."
        )

    shared_library_hex_new, changes_count = re.subn(
        hex_string_regex, distance_hex_string, shared_library_hex, 1
    )
    logger.debug(f"Replaced string, changes count: {changes_count}")

    new_matches = re.findall(hex_string_regex, shared_library_hex_new)
    logger.debug(f"Old: {matches}")
    logger.debug(f"New: {new_matches}")

    try:
        with open(shared_library_path, "wb") as f:
            f.write(bytes.fromhex(shared_library_hex_new))
        logger.debug(f"Written: {shared_library_path}")
    except PermissionError as e:
        raise Exception(
            "Couldn't open shared library file, close Dota 2 before launching the app",
        )


def get_steam_library_path(steam_path):
    # Dota and Steam can have different install locations/drives.
    library_folders_path = os.path.join(steam_path, LIBRARY_FOLDERS_PATH)
    library_folders = vdf.load(open(library_folders_path))["libraryfolders"]
    logger.debug(f"Read {library_folders_path}")
    for key in library_folders:
        if DOTA_APP_ID in library_folders[key]["apps"]:
            dota_path = library_folders[key]["path"]
            logger.debug(f"Found Dota path: {dota_path} in libraryfolders")
            return dota_path
    raise Exception(
        "Dota 2 path was not found in libraryfolders.vdf file."
        " This usually happens when Dota 2 is not installed on the system."
        " If you have just installed Dota 2 you need to restart Steam"
        " for it to apply the changes to specific files."
    )


def dota_was_updating(steam_library_path):
    # If "StateFlags" is '4' that means that Dota is updated/installed
    app_manifest_path = os.path.join(steam_library_path, APP_MANIFEST_PATH)
    app_manifest = vdf.load(open(app_manifest_path))
    app_status = app_manifest["AppState"]["StateFlags"]
    logger.debug(f"Read app manifest: {app_manifest_path}, status: {app_status}")
    if app_status != "4":
        while app_status != "4":
            logger.info(f"Waiting for Dota 2 to get updates, status: {app_status}")
            time.sleep(3)
            app_manifest = vdf.load(open(app_manifest_path))
            app_status = app_manifest["AppState"]["StateFlags"]
        return True
    else:
        return False


def get_current_hex_string():
    # This is done to avoid hardcoding
    # this value and enable updating it through Github.
    try:
        response = requests.get(SERVER_HEX_STRING_LINK)
        response.raise_for_status()
        response_text_repr = repr(response.text)
        logger.debug(f"String {response_text_repr} received from GitHub")
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        logger.error("Couldn't receive string from GitHub, using the default one")
        return DEFAULT_HEX_STRING


def set_config():
    config_path = os.path.join(os.getcwd(), "config.ini")
    config_file = configparser.ConfigParser()

    try:
        config_file.read(config_path)
    except Exception as e:
        logger.error(
            "Something wrong with the config, creating new one...", exc_info=True
        )

    if config_file.has_section("DOTA-CAMERA-DISTANCE"):
        config_file.clear()
        logger.info("Detected old config style, rewriting...")

    if not config_file.has_section("CAMERA-DISTANCE"):
        config_file["CAMERA-DISTANCE"] = {}
    if not config_file.has_section("PATHS"):
        config_file["PATHS"] = {}
    camera_config = config_file["CAMERA-DISTANCE"]
    path_config = config_file["PATHS"]

    if not camera_config.get("logging_level"):
        camera_config["logging_level"] = "INFO"
    logger.setLevel(camera_config["logging_level"].upper())
    logger.info(f"Logging level: {logging.getLevelName(logger.getEffectiveLevel())}")

    if not camera_config.get("distance"):
        distance_message = "Enter distance[default 1200, recommended 1400]: "
        camera_config["distance"] = input(distance_message) or DEFAULT_DISTANCE
    logger.info(f"Distance: {camera_config['distance']}")

    if not camera_config.get("receive_hex_from_git"):
        camera_config["receive_hex_from_git"] = "yes"
    logger.info(f"Receive hex from git: {camera_config['receive_hex_from_git']}")

    # set this config variable to False, set your manual string, and the program won't update it
    # automatically every time you launch it.
    if camera_config.getboolean("receive_hex_from_git") or not camera_config.get(
        "hex_string"
    ):
        camera_config["hex_string"] = get_current_hex_string()
    logger.info(f"Hex string: {camera_config['hex_string']}")

    if not camera_config.get("autostart_game"):
        camera_config["autostart_game"] = "yes"
    logger.info(f"Autostart game: {camera_config['autostart_game']}")

    if not path_config.get("steam_path"):
        path_config["steam_path"] = get_steam_path()
    logger.info(f"Steam path: {path_config['steam_path']}")

    if not path_config.get("steam_library_path"):
        path_config["steam_library_path"] = get_steam_library_path(
            path_config["steam_path"]
        )
    logger.info(f"Steam library path: {path_config['steam_library_path']}")

    if not path_config.get("shared_library_path"):
        path_config["shared_library_path"] = os.path.join(
            path_config["steam_library_path"], SHARED_LIBRARY_PATH
        )
    logger.info(f"Shared library path: {path_config['shared_library_path']}")

    with open(config_path, "w") as configfile:
        config_file.write(configfile)
    logger.info(f"Updated config: {config_path}")

    return camera_config, path_config


def main():
    camera_config, path_config = set_config()

    set_distance(
        camera_config["hex_string"],
        camera_config["distance"],
        path_config["shared_library_path"],
    )
    if camera_config.getboolean("autostart_game"):
        start_game()
        logger.info("Launching Dota 2 ...")

        # When launching Dota for the first time it might get updates,
        # so shared library file needs to be rewritten again.
        if dota_was_updating(path_config["steam_library_path"]):
            set_distance(
                camera_config["hex_string"],
                camera_config["distance"],
                path_config["shared_library_path"],
            )
            logger.info('Press "Play game"')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Program crashed", exc_info=True)
        logger.error(
            "If nothing helps or there's a bug, send me a screenshot via"
            " https://github.com/searayeah/dota-camera-distance/issues",
        )
    finally:
        for i in range(5, 0, -1):
            logger.info(f"Exit in: {i}")
            time.sleep(1)
