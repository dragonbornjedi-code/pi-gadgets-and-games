#!/bin/bash
# install_dependencies.sh
# Installs pygame, evdev, psutil on target Pi
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip libsdl2-2.0-0 libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-ttf-2.0-0
python3 -m venv .venv
source .venv/bin/activate
pip install pygame evdev psutil
