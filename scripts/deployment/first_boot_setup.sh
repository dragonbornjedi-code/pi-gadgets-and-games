#!/bin/bash
# first_boot_setup.sh
# Pi-specific system configuration
sudo raspi-config nonint do_boot_splash 0
sudo raspi-config nonint do_memory_split 128
# Configure SPI/LCD
sudo raspi-config nonint do_spi 0
