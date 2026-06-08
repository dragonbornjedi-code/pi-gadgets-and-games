# RetroPie & 3.5" LCD Setup Guide

This guide covers setting up your Raspberry Pi Zero 2 W with RetroPie, a 3.5" LCD screen, an Xbox One Controller, and this Memory Game.

## 1. Flash the SD Card
1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Insert your SD card.
3. Choose OS: **Emulation and game OS** > **RetroPie** > **RetroPie 4.8.x (Pi 2/3/Zero 2)**.
4. Choose Storage: Select your SD card.
5. Click **Write**.

## 2. Initial Configuration
1. Put the SD card in your Pi and boot it up.
2. Connect a keyboard or configure WiFi via the RetroPie menu.
3. Enable SSH (optional but recommended for easier setup):
   - **RetroPie Settings** > **Raspi-Config** > **Interfacing Options** > **SSH** > **Yes**.

## 3. Install 3.5" LCD Drivers
Most 3.5" SPI displays (like Waveshare) require specific drivers to work.
Run these commands over SSH or in the terminal:
```bash
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show/
chmod +x LCD35-show
sudo ./LCD35-show
```
*The Pi will reboot and the display should now show the console/RetroPie.*

## 4. Connect Xbox One Controller
If using a Bluetooth Xbox One controller, it's best to install `xpadneo`:
```bash
sudo apt-get update
sudo apt-get install -y dkms raspberrypi-kernel-headers
git clone https://github.com/atar-axis/xpadneo.git
cd xpadneo
sudo ./install.sh
```
Then pair it via:
- **RetroPie Settings** > **Bluetooth**.

## 5. Install the Memory Game
Run these commands in the home directory (`/home/pi`):
```bash
git clone https://github.com/your-repo/pi-gadgets-and-games.git
cd pi-gadgets-and-games
bash scripts/deployment/install_dependencies.sh
bash scripts/deployment/setup_retropie_integration.sh
```

## 6. Launching the Game
1. Restart EmulationStation.
2. Navigate to the **Ports** section.
3. Select **MemoryGame**.

Enjoy!
