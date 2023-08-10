# dota-camera-distance

> Replace your Dota 2 icon by this app to completely forget about manually changing camera distance.

## About

DCD is a small app that automatically changes camera distance (camera-zoom) in Dota 2. Using hex-editors (like [HxD](https://mh-nexus.de/en/hxd/)) to increase camera distance might be frustrating as camera distance gets reset every time the game gets an update. So I've built this app to provide an automatic solution.

## Quickstart

[Download and run latest version](https://github.com/searayeah/dota-camera-distance/releases/latest/download/dota-camera-distance.exe), game version supported: 7.34

> Additionally, you can just install requirements and run `python main.py` if you have Python installed on your system.

## Screenshots

## How does it work

1. Locates your Dota 2 folder and ```client.dll``` file
2. Changes camera distance to desired value
3. Launches Dota 2

> At first launch you will be prompted to enter the required camera distance. With further launches this app will run Dota with this initial value. You can always change it by deleting or editing config.ini generated at the location of the script.

## Is it bannable?

## Is it a cheat?

## What if I do not want to use it? How do I change distance manually?

Current codes:

For manual search in HxD: ```00 00 96 44 00 00 C8 44```

The code used in app for more precision: ```00 00 AE 42 00 00 96 44 00 00 C8 44 00 40 9C 45```

## How to build it?

1. Install [Python](https://www.python.org/downloads/) and [requirements.txt](https://stackoverflow.com/a/15593865)
2. Build ```.exe``` file using command ```pyinstaller --noconfirm --onefile --console --clean --icon game-icon.ico --name dota-camera-distance main.py```

> The ```.exe``` file will be usable on systems without Python installed.

## What systems are currently supported?

- Windows

This application:



## Executing

1. [Download exe](https://github.com/searayeah/dota-camera-distance/releases/latest/download/dota-camera-distance.exe) and run  ```dota-camera-distance.exe```
2. [Python](https://www.python.org/): ```python main.py```

## Building

