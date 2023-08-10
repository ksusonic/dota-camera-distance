# dota-camera-distance

> Replace your Dota 2 icon by this app to completely forget about manually changing camera distance.

## About

DCD is a small app that automatically changes camera distance (camera-zoom) in Dota 2. Using hex-editors (like [HxD](https://mh-nexus.de/en/hxd/)) to increase camera distance manually might be frustrating as camera distance gets reset every time the game gets an update. So, I've built this app to provide an automatic solution. You should launch it every time you want to play Dota.

## Quickstart

[Download and run latest version](https://github.com/searayeah/dota-camera-distance/releases/latest/download/dota-camera-distance.exe), game version supported: 7.34

> If you have Python 3.8+ you can just install requirements and run `python main.py`.

## Screenshots

Default distance: 1200             |  Modified distance: 1600
:-------------------------:|:-------------------------:
![1200](https://github.com/searayeah/dota-camera-distance/assets/57370975/ea535c4b-4d03-47d1-8389-5eeb54d4f09f) | ![1600](https://github.com/searayeah/dota-camera-distance/assets/57370975/9388bb04-f149-49d8-9bad-9b4977a9ad52)

## How does it work

The app automatically does the steps shown in this [video](https://www.youtube.com/watch?v=GNOkvm5MrB0):

1. Locates your Dota 2 folder and ```client.dll``` file.
2. Finds the specific code in the file and changes camera distance to desired value.
3. Launches Dota 2 and closes itself.

### Features

- The settings are saved at the location of the script as `config.ini` file. **You can change distance value and other stuff using this file**.
- The hex code will be updated, if there are any changes (usually when big updates happen)

## Is it bannable? Is it a cheat?

First of all, the app does not interfere in the Dota process. The game is launched as if you launched if from a shortcut. Players have been using this method for more than five years and so far there have been no bans.

Secondly, I wound not consider changing distance as cheating. I do not know why the devs have not added this feature to the game settings. I think that it is not very fair when players with [ultrawide screens](https://www.youtube.com/watch?v=ALCneiFSvIY) get a huge advantage over normal players. ![image](https://github.com/searayeah/dota-camera-distance/assets/57370975/51bcce78-963d-4b43-a912-b0c60460de50)

## What if I do not want to use it? How do I change distance manually?

You just need to download [HxD](https://mh-nexus.de/en/hxd/) and perform the steps from the [video](https://www.youtube.com/watch?v=GNOkvm5MrB0) I mentioned earlier. I will be updating the codes for you. Remember that you will have to do this steps manually every time Dota receives an update, even a small one.

Current codes:
- For manual search in HxD: ```00 00 96 44 00 00 C8 44```
- The code used in app for more precision: ```00 00 AE 42 00 00 96 44 00 00 C8 44 00 40 9C 45```

## What systems are currently supported?

Currently only Windows is supported. I do not have Mac, so if anyone wants to help me make the app crossplatform - PRs are welcome. Currently, I am slowly researching how to make it work on Linux.

## How to build it?

1. Install [Python](https://www.python.org/downloads/) and [requirements.txt](https://stackoverflow.com/a/15593865)
2. Build ```.exe``` file using command ```pyinstaller --noconfirm --onefile --console --clean --icon game-icon.ico --name dota-camera-distance main.py```

> The ```.exe``` file will be usable on systems without Python installed.
