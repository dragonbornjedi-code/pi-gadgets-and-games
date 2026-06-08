#!/bin/bash
# ==========================================================
# pi-gadgets-and-games — Fresh RetroPie SD Card Builder
# ==========================================================
# Wipes /dev/sda, flashes Raspberry Pi OS Lite (Bookworm),
# injects first-boot automation for:
#   - SSH, WiFi, hostname
#   - 3.5" GPIO LCD driver (Waveshare)
#   - PS5 DualSense bluetooth pairing
#   - RetroPie installation
#   - pi-gadgets-and-games game integration
# ==========================================================
set -euo pipefail

DEVICE="/dev/sda"
HOSTNAME="retropie"
SSID="SpectrumSetup-325A"
WIFI_PASS="${1:-majorvacation057}"  # pass as first arg: bash setup_sd_card.sh "yourpassword"
PS5_MAC="90:B6:85:C7:EC:74"

# --------------------------------------------------------
# Sanity checks
# --------------------------------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run with sudo:  sudo bash $0 \"your_wifi_password\""
    exit 1
fi

if [ -z "$WIFI_PASS" ]; then
    echo "USAGE: sudo bash $0 \"your_wifi_password\""
    exit 1
fi

echo "========================================="
echo " pi-gadgets-and-games SD Card Builder"
echo "========================================="
echo "Device:  $DEVICE"
echo "Hostname: $HOSTNAME"
echo "SSID:    $SSID"
echo "PS5 MAC: $PS5_MAC"
echo ""
echo "WARNING: ALL DATA ON $DEVICE WILL BE DESTROYED"
echo ""
read -rp "Press Enter to continue or Ctrl+C to abort..."

# --------------------------------------------------------
# Step 1 — Wipe old partitions
# --------------------------------------------------------
echo ""
echo "[1/6] Wiping old partition table..."
# Use parted to create a new MBR label (deletes all partitions)
parted -s "$DEVICE" mklabel msdos 2>/dev/null || true
wipefs -a "$DEVICE" 2>/dev/null || true
dd if=/dev/zero of="$DEVICE" bs=1M count=10 status=progress 2>/dev/null || true
sync
echo "  ✓ SD card wiped"

# --------------------------------------------------------
# Step 2 — Download Raspberry Pi OS Lite (Bookworm)
# --------------------------------------------------------
echo "[2/6] Downloading Raspberry Pi OS Lite (Bookworm) 64-bit..."
IMAGE_URL="https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-11-19/2024-11-19-raspios-bookworm-arm64-lite.img.xz"
IMAGE_FILE="raspios-bookworm-arm64-lite.img.xz"

if [ ! -f "$IMAGE_FILE" ]; then
    wget -O "$IMAGE_FILE" "$IMAGE_URL"
else
    echo "  Already downloaded, reusing."
fi

echo "  ✓ Download complete"

# --------------------------------------------------------
# Step 3 — Flash image to SD card
# --------------------------------------------------------
echo "[3/6] Flashing image to $DEVICE..."
xzcat "$IMAGE_FILE" | dd of="$DEVICE" bs=4M status=progress conv=fsync
echo "  ✓ Image flashed"
sleep 1

# --------------------------------------------------------
# Step 4 — Mount and inject boot configs
# --------------------------------------------------------
echo "[4/6] Mounting and injecting boot config..."

# Determine partition naming
BOOT_PART=""
ROOT_PART=""
if ls /dev/sda1 2>/dev/null; then
    BOOT_PART="/dev/sda1"
    ROOT_PART="/dev/sda2"
elif ls /dev/mmcblk0p1 2>/dev/null; then
    BOOT_PART="/dev/mmcblk0p1"
    ROOT_PART="/dev/mmcblk0p2"
fi

if [ -z "$BOOT_PART" ]; then
    echo "ERROR: Could not find boot partition after flash. Try: lsblk"
    exit 1
fi

MNT_BOOT="/mnt/boot"
MNT_ROOT="/mnt/root"
mkdir -p "$MNT_BOOT" "$MNT_ROOT"

# Mount boot partition (FAT32)
mount "$BOOT_PART" "$MNT_BOOT"

# Mount root partition if it exists
if [ -b "$ROOT_PART" ]; then
    mount "$ROOT_PART" "$MNT_ROOT"
fi

# --- Enable SSH ---
touch "$MNT_BOOT/ssh"
echo "  ✓ SSH enabled"

# --- Configure WiFi ---
cat > "$MNT_BOOT/wpa_supplicant.conf" << WPAEOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="$SSID"
    psk="$WIFI_PASS"
    key_mgmt=WPA-PSK
}
WPAEOF
echo "  ✓ WiFi configured (SSID: $SSID)"

# --- Set hostname ---
echo "$HOSTNAME" > "$MNT_ROOT/etc/hostname" 2>/dev/null || true
sed -i "s/127.0.1.1.*/127.0.1.1\t$HOSTNAME/g" "$MNT_ROOT/etc/hosts" 2>/dev/null || true
echo "  ✓ Hostname set to $HOSTNAME"

# --- Create firstboot automation script ---
cat > "$MNT_ROOT/root/firstboot.sh" << 'FIRSTBOOT'
#!/bin/bash
# ==========================================================
# First-boot automation — runs once after initial login
# ==========================================================
set -euo pipefail
exec 2>&1 > /root/firstboot.log

echo "=== pi-gadgets-and-games First Boot Setup ==="

# Fix sources.list if needed (bookworm should be fine, but apt update anyway)
apt-get update -qq
echo "[1/9] System updated"

# Install basic tools
apt-get install -y git python3-pygame python3-venv python3-pip \
    bluez bluez-tools bluetooth dkms raspberrypi-kernel-headers \
    xz-utils wget curl
echo "[2/9] Core packages installed"

# --------------------------------------------------------
# 3.5" GPIO LCD Driver (Waveshare)
# --------------------------------------------------------
echo "[3/9] Installing 3.5\" LCD driver..."
cd /root
git clone --depth=1 https://github.com/waveshare/LCD-show.git
cd LCD-show
# Apply the 3.5" LCD overlay
chmod +x LCD35-show
# We don't run this directly because it reboots — instead manually apply
# the device-tree overlay and framebuffer config
cat >> /boot/config.txt << 'LCDEOF'

# --- 3.5" GPIO LCD ---
dtoverlay=waveshare35a
hdmi_force_hotplug=1
hdmi_cvt=480 320 60 6 0 0 0
hdmi_group=2
hdmi_mode=1
hdmi_mode=87
dtparam=spi=on
dtoverlay=waveshare35a:rotate=90
LCDEOF

# Install the fbtft driver
modprobe fbtft_device 2>/dev/null || true
echo "  ✓ LCD driver configured"

# --------------------------------------------------------
# PS5 DualSense Bluetooth setup
# --------------------------------------------------------
echo "[4/9] Installing PS5 controller driver..."
# Install hid-playstation kernel module
apt-get install -y linux-modules-extra-raspi 2>/dev/null || true

# Load hid-playstation module
echo "hid_playstation" >> /etc/modules
modprobe hid_playstation 2>/dev/null || true

# Install xpadneo for better compatibility
cd /root
git clone --depth=1 https://github.com/atar-axis/xpadneo.git
cd xpadneo
./install.sh || true
echo "  ✓ PS5 driver installed"

# --------------------------------------------------------
# Bluetooth pairing
# --------------------------------------------------------
echo "[5/9] Pairing PS5 controller..."
cat > /root/pair_ps5.sh << 'PAIRSCRIPT'
#!/bin/bash
MAC="90:B6:85:C7:EC:74"
echo "Powering on Bluetooth..."
bluetoothctl power on
bluetoothctl agent on
bluetoothctl default-agent
echo "Removing any previous pairing..."
bluetoothctl remove "$MAC" 2>/dev/null || true
sleep 1
echo "Scanning..."
bluetoothctl scan on &
SCAN_PID=$!
sleep 5
kill $SCAN_PID 2>/dev/null || true
echo "Pairing and trusting..."
bluetoothctl pair "$MAC"
bluetoothctl trust "$MAC"
bluetoothctl connect "$MAC"
echo "PS5 controller paired: $MAC"
PAIRSCRIPT
chmod +x /root/pair_ps5.sh

# Run pairing (controller must be in pairing mode: PS + Share buttons)
echo "  ✓ PS5 pairing script created at /root/pair_ps5.sh"
echo "  NOTE: Put controller in pairing mode (PS+Share), then run:"
echo "        sudo bash /root/pair_ps5.sh"

# --------------------------------------------------------
# RetroPie Installation
# --------------------------------------------------------
echo "[6/9] Installing RetroPie..."
cd /root
git clone --depth=1 https://github.com/RetroPie/RetroPie-Setup.git
cd RetroPie-Setup
# Run unattended basic install (skip emulators to save space, user can add later)
__nodialog=1 __auto=1 ./retropie_packages.sh setup basic_install
echo "  ✓ RetroPie installed"

# --------------------------------------------------------
# Python & game deps
# --------------------------------------------------------
echo "[7/9] Installing game dependencies..."
apt-get install -y python3-pygame python3-evdev python3-psutil \
    libsdl2-2.0-0 libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-ttf-2.0-0
echo "  ✓ Game dependencies installed"

# --------------------------------------------------------
# Clone and setup pi-gadgets-and-games
# --------------------------------------------------------
echo "[8/9] Setting up pi-gadgets-and-games..."
cd /home/pi
git clone https://github.com/dragonbornjedi-code/pi-gadgets-and-games.git
cd pi-gadgets-and-games
python3 -m venv .venv
source .venv/bin/activate
pip install pygame evdev psutil
deactivate
chown -R pi:pi /home/pi/pi-gadgets-and-games
echo "  ✓ Game cloned and dependencies installed"

# --------------------------------------------------------
# Integrate into RetroPie Ports
# --------------------------------------------------------
echo "[9/9] Integrating into RetroPie Ports..."
mkdir -p /home/pi/RetroPie/roms/ports
cat > /home/pi/RetroPie/roms/ports/MemoryGame.sh << 'GAMESCRIPT'
#!/bin/bash
cd /home/pi/pi-gadgets-and-games
source .venv/bin/activate
python3 main.py
GAMESCRIPT
chmod +x /home/pi/RetroPie/roms/ports/MemoryGame.sh
chown -R pi:pi /home/pi/RetroPie/roms/ports
echo "  ✓ Game integrated into Ports menu"

# --------------------------------------------------------
# Done
# --------------------------------------------------------
echo ""
echo "========================================="
echo " pi-gadgets-and-games First Boot Complete"
echo "========================================="
echo ""
echo "What's installed:"
echo "  - Raspberry Pi OS Bookworm"
echo "  - 3.5\" GPIO LCD driver (Waveshare)"
echo "  - PS5 DualSense driver (hid-playstation + xpadneo)"
echo "  - RetroPie (EmulationStation)"
echo "  - Memory Game in Ports menu"
echo ""
echo "Post-install steps:"
echo "  1. Pair your PS5 controller:"
echo "     sudo bash /root/pair_ps5.sh"
echo "  2. Reboot: sudo reboot"
echo "  3. Game appears in Ports > MemoryGame"
echo ""

# Mark as done
touch /root/.firstboot_complete
FIRSTBOOT

chmod +x "$MNT_ROOT/root/firstboot.sh"
echo "  ✓ First-boot script created at /root/firstboot.sh"

# --- Create auto-start for firstboot via rc.local ---
cat > "$MNT_ROOT/etc/rc.local" << 'RCLOCAL'
#!/bin/sh -e
# First-boot auto-setup
if [ ! -f /root/.firstboot_complete ]; then
    /root/firstboot.sh &
fi
exit 0
RCLOCAL
chmod +x "$MNT_ROOT/etc/rc.local"

# Sync and unmount
sync
umount "$MNT_BOOT" 2>/dev/null || true
umount "$MNT_ROOT" 2>/dev/null || true
rmdir "$MNT_BOOT" "$MNT_ROOT" 2>/dev/null || true

echo ""
echo "========================================="
echo " SD Card Build Complete!"
echo "========================================="
echo ""
echo "NEXT STEPS:"
echo "  1. Insert SD card into Pi Zero 2 W"
echo "  2. Connect ethernet (recommended for first boot)"
echo "  3. Power on the Pi"
echo "  4. Wait 30-60 minutes (first boot auto-setup runs)"
echo "  5. SSH: ssh pi@retropie.local"
echo "     (Default password: raspberry)"
echo "  6. Pair PS5: sudo bash /root/pair_ps5.sh"
echo "     (Press PS+Share on controller to enter pairing mode)"
echo "  7. Reboot: sudo reboot"
echo "  8. Game is in Ports > MemoryGame"
echo ""