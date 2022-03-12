# raspberry_pi_libraries

This is a collection of wrapper classes designed around convenience and reducing boilerplate code in applications designed for, but not limited to, the [Raspberry Pi](https://www.raspberrypi.com/). More information on the individual classes can be found in the docstring underneath their class declaration.

## Library Structure

The following structure includes all the classes this library encompasses:

+ Packages
    + `camera_wrapper.py`
        + Frame
    + `multi_wrapper.py`
        + DirectoryManagement
            + WriteDir
            + ReadDir
        + Fps
        + Keyboard
        + Timer
        + InitBashArgs
        + Dataset
        + Xml
        + ColorTracker
+ `model_wrapper.py`
    + ModelWrapper
+ `serial_wrapper.py`
    + SerialWrapper

## Getting Started

To set up this repository as an importable package in your python environment clone it into the directory that matches your platform. The right directory for you will depend on how you originally installed python.

+ **Unix** (includes Linux and macOS, which are Unix-based)**:**
    + **Pyenv:** `~/.local/lib/python3.X/site-packages/`
    + **Built from source:** `/usr/local/lib/python3.X/site-packages/`
    + **System builtin:** `/usr/lib/python3.X/site-packages/`
+ **Windows:**
    + **Standard path:** `C:\Python3.X\Lib\site-packages\`

Replace `3.X` with the python version of your environment.

## Example Code

[This repository](https://gitlab.com/rohand2412/opencv-capture-data-for-ml) is a collection of scripts that uses this package to manipulate data.