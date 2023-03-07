# [7.32e]dota-camera-distance

## Current string: ```00 00 96 44 00 00 61 45```

*Replace your Dota 2 icon by this app to completely forget about manually changing camera distance.*

[Download latest version](https://github.com/searayeah/dota-camera-distance/releases/latest/download/dota-camera-distance.exe)

## Abstract

Using hex-editors (like [HxD](https://mh-nexus.de/en/hxd/)) to increase camera distance might be frustrating as camera distance gets reset every time the game gets an update. This app provides an automatic solution.

## App Description

This application:

1. Locates your Dota 2 folder and ```client.dll``` file
2. Changes camera distance to desired value
3. Launches Dota 2

> At first launch you will be prompted to enter the required camera distance. With further launches this app will run Dota with this initial value. You can always change it by deleting or editing config.ini generated at the location of the script.

## Executing

1. [Download exe](https://github.com/searayeah/dota-camera-distance/releases/latest/download/dota-camera-distance.exe) and run  ```dota-camera-distance.exe```
2. [Python](https://www.python.org/): ```python main.py```

## Building

1. Install [Python](https://www.python.org/downloads/) and [requirements.txt](https://stackoverflow.com/a/15593865)
2. Build ```.exe``` file using command ```pyinstaller --noconfirm --onefile --console --clean --icon game-icon.ico --name dota-camera-distance main.py```

> The ```.exe``` file will be usable on systems without Python installed.
