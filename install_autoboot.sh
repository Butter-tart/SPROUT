#!/bin/bash

# SPROUT Autoboot Installation Script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
USER_NAME=$(logname || echo $USER)
INSTALL_DIR="$SCRIPT_DIR"

# Define variables
SERVICE_NAME="sprout.service"
WEBAPP_SERVICE_NAME="sprout-webapp.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

echo "Installing SPROUT autoboot service..."
echo "Detected Installation Directory: $INSTALL_DIR"
echo "Detected User: $USER_NAME"

# 0. Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-pip python3-pil python3-numpy libopenjp2-7 libtiff5 spi-tools python3-evdev python3-rpi.gpio

# 0.1 Install Waveshare EPD library if not present
if ! python3 -c "import waveshare_epd" 2>/dev/null; then
    echo "Installing Waveshare EPD library..."
    pip3 install waveshare-epd --break-system-packages || pip3 install waveshare-epd
fi

# 1. Ensure SPI is enabled (non-interactive)
if [ -f /boot/config.txt ]; then
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
      echo "Enabling SPI in /boot/config.txt..."
      echo "dtparam=spi=on" >> /boot/config.txt
      echo "SPI enabled. A reboot might be required if it wasn't already on."
    fi
elif [ -f /boot/firmware/config.txt ]; then
    if ! grep -q "dtparam=spi=on" /boot/firmware/config.txt; then
      echo "Enabling SPI in /boot/firmware/config.txt..."
      echo "dtparam=spi=on" >> /boot/firmware/config.txt
      echo "SPI enabled. A reboot might be required if it wasn't already on."
    fi
fi

# 2. Prepare service files with correct paths and user
echo "Configuring service files..."

# Sprout Service
cat > /etc/systemd/system/$SERVICE_NAME <<EOF
[Unit]
Description=SPROUT Mental Health Tamagotchi
After=network.target

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/src/main.py --loop
WorkingDirectory=$INSTALL_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER_NAME
KillSignal=SIGINT
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# Webapp Service
cat > /etc/systemd/system/$WEBAPP_SERVICE_NAME <<EOF
[Unit]
Description=SPROUT Web Interface
After=network.target

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/src/webapp.py
WorkingDirectory=$INSTALL_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER_NAME

[Install]
WantedBy=multi-user.target
EOF

# 3. Reload systemd to recognize the new services
systemctl daemon-reload

# 4. Enable the services to start on boot
systemctl enable $SERVICE_NAME
systemctl enable $WEBAPP_SERVICE_NAME

# 5. Ensure the user is in the correct groups for hardware access
usermod -a -G spi,gpio,i2c,input $USER_NAME

# 6. Inform the user
echo "-------------------------------------------------------"
echo "SPROUT autoboot services installed and enabled!"
echo "User $USER_NAME added to spi, gpio, i2c, and input groups."
echo "They will start automatically on the next boot."
echo "To start them now, run:"
echo "  sudo systemctl start $SERVICE_NAME"
echo "  sudo systemctl start $WEBAPP_SERVICE_NAME"
echo "To check status, run:"
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo systemctl status $WEBAPP_SERVICE_NAME"
echo "-------------------------------------------------------"
