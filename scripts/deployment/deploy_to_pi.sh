#!/bin/bash
# deploy_to_pi.sh
# Syncs code to Pi Zero 2 W
rsync -avz --exclude '.venv' --exclude '__pycache__' . pi@raspberrypi.local:/home/pi/pi-gadgets-and-games/
