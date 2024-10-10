> [!WARNING]  
> 🚧 This project is incomplete and WIP. 🚧

# SPT - Song Practice Tool

<p align="center">
<img src="https://raw.githubusercontent.com/AnicJov/SPT/main/res/preview.png"/>
</p>


This is a cross-platform tool that aims to help musicians practice songs with features that make repeating sections easy and playing along fun.

Written in Python and PyQt6, using [demucs](https://github.com/facebookresearch/demucs) for instrument separation.

### Features:
- Music player functions
- Playback speed control
- Save/Load section markers
- Automatic instrument stem separation
- Instrument stem volume mixer

Planned:
- Section looping
- Session saving/restoring
- URL import support
- Keyboard shortcuts support
- Built in metronome with beat detection
- Built in PDF viewer for viewing notation

## Usage

### Install the latest version of Python

Ubuntu:
```bash
$ sudo apt install python3
```

Fedora:
```bash
$ sudo dnf install python3
```

Arch:
```bash
$ sudo pacman -S python
```

MacOS:
```sh
$ brew install python
```

Windows:
- Open the Microsoft Store and search for Python
- Pick the newest version and install it

### Clone the repository
```bash
$ git clone https://github.com/AnicJov/SPT.git
$ cd SPT
```

### Setup a Python virtual environment
```bash
$ python3 -m venv venv
$ venv/bin/pip3 install -r requirements.txt
```

### Run with
```bash
$ venv/bin/python3 main.py
```

### or
```bash
$ ./run.sh
```
