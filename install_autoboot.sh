#!/bin/bash

# SPROUT Autoboot Installation Script

# Define variables
SERVICE_NAME="sprout.service"
INSTALL_DIR="/home/pi/SPROUT"
USER_NAME="pi"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

echo "Installing SPROUT autoboot service..."

# 0. Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-pip python3-pil python3-numpy libopenjp2-7 libtiff5 spi-tools python3-evdev

# 1. Ensure SPI is enabled (non-interactive)
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
  echo "Enabling SPI in /boot/config.txt..."
  echo "dtparam=spi=on" >> /boot/config.txt
  echo "SPI enabled. A reboot might be required if it wasn't already on."
fi

# 2. Update WorkingDirectory and User in the service file if necessary
# We assume the user might have named their user differently or put it in a different spot, 
# but for RPi zero the default is usually /home/pi/SPROUT.
# We'll stick to the provided sprout.service template but make sure paths exist.

# 2. Copy service file to systemd directory
cp sprout.service /etc/systemd/system/$SERVICE_NAME

# 3. Reload systemd to recognize the new service
systemctl daemon-reload

# 4. Enable the service to start on boot
systemctl enable $SERVICE_NAME

# 5. Ensure the user is in the correct groups for hardware access
usermod -a -G spi,gpio,i2c,input $USER_NAME

# 6. Inform the user
echo "-------------------------------------------------------"
echo "SPROUT autoboot service installed and enabled!"
echo "User $USER_NAME added to spi, gpio, i2c, and input groups."
echo "It will start automatically on the next boot."
echo "To start it now, run: sudo systemctl start $SERVICE_NAME"
echo "To check status, run: sudo systemctl status $SERVICE_NAME"
echo "-------------------------------------------------------"
