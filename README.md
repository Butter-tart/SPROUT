# SPROUT: Mental Health Tamagotchi

SPROUT is a mental health companion designed for the Raspberry Pi Zero 2 WH and Waveshare e-Paper displays.

## Features
- **Mood Check-ins**: Log your daily mental health state to help your Sprout grow.
- **Sunshine Tracker**: SPROUT encourages you to go outside! Getting sunshine boosts both your and Sprout's happiness and growth.
- **Supportive Companion**: Updated messaging to be more compassionate on tough mental health days.
- **Dynamic Character**: Sprout now grows from a tiny seedling into a beautiful flower as you care for it and yourself.
- **Growth Stages**: Level up by checking in, going for walks, and getting sunshine.
- **Animated Loading**: A hopping seedling greets you during startup using e-ink partial refreshes.
- **8BitDo Zero 2 Support**: Use your controller to navigate menus and control functions.
- **Settings Menu**: Customize your experience with different themes (Default, Dark, High Contrast).
- **System Controls**: Shutdown or Restart your Raspberry Pi directly from the SPROUT menu.
- **Walk Timer**: Start and stop a walk timer to track your outdoor activity and boost Sprout's health.
- **Web App Companion**: Access Sprout from any device on your network! Care for your pet via a web interface that syncs with your physical device.
- **E-Ink Optimized**: Low power consumption and easy on the eyes.

## Installation on Raspberry Pi

1. **Enable SPI**:
   ```bash
   sudo raspi-config
   # Interface Options -> SPI -> Yes
   ```

2. **Install Dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-pil python3-numpy
   pip3 install spidev RPi.GPIO
   ```

3. **Install Waveshare Library**:
   ```bash
   git clone https://github.com/waveshare/e-Paper.git
   cd e-Paper/RaspberryPi_JetsonNano/python/
   sudo python3 setup.py install
   ```

4. **Install Required Fonts (Optional but recommended)**:
   ```bash
   sudo apt-get install fonts-liberation
   ```

5. **Run SPROUT**:
   ```bash
   python3 src/main.py
   ```

## Web App Companion

SPROUT now includes a web application that allows you to care for your pet from any browser on your local network.

1. **Install Flask**:
   ```bash
   pip3 install flask
   ```

2. **Run the Web App**:
   ```bash
   python3 src/webapp.py
   ```
   By default, it will be available at `http://[your-pi-ip]:5000`.

3. **Care from anywhere**: You can water, pet, and check on Sprout's stats from your phone or computer. Changes are synced with the physical device.

## 8BitDo Zero 2 Controller Setup

1. **Pair your controller**:
   - Hold `START` to turn on the controller (Blue light flashes).
   - Hold `SELECT` for 3 seconds to enter pairing mode (Rapid flashing).
   - On your Raspberry Pi, use `bluetoothctl`:
     ```bash
     bluetoothctl
     scan on
     # Find the MAC address of "8BitDo Zero 2"
     pair [MAC_ADDRESS]
     trust [MAC_ADDRESS]
     connect [MAC_ADDRESS]
     ```

2. **Test the controller**:
   ```bash
   sudo python3 test_controller.py
   ```
   If buttons don't register, ensure your user is in the `input` group: `sudo usermod -a -G input $USER` and reboot.

3. **Controller Usage**:
   - **START**: Open/Close Menu.
   - **A**: Select (in menu) or Shortcut to Start/Stop Walk.
   - **DPAD / Buttons**: Navigate menu.
   - **Menu Options**:
     - **Walk Timer**: Start/Stop tracking your walk.
     - **Settings**: Change the display theme (Dark mode, etc).
     - **Restart/Shutdown**: Safely power off or reboot your device.

## Troubleshooting Display Issues
If the e-ink screen is not updating:
1. **Run the Diagnostic Tool**:
   ```bash
   sudo python3 test_display.py
   ```
   This script will attempt to communicate with the display using several different 2.13-inch drivers. If one works, it will tell you which one.

2. **Check Hardware Diagnostic in SPROUT**:
   Run `python3 src/main.py`. It now performs a hardware check on startup and will warn you if SPI is disabled or libraries are missing.

3. **Verify SPI is enabled**: Run `ls /dev/spi*`. You should see `/dev/spidev0.0`. If not, run `sudo raspi-config` > Interfacing Options > SPI > Yes.

4. **Permissions**: Ensure your user has access to hardware:
   ```bash
   sudo usermod -a -G spi,gpio,i2c $USER
   ```
   (You must log out and back in for this to take effect).

5. **Reinstall Dependencies**: Sometimes system libraries are missing for image processing:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-pil python3-numpy libopenjp2-7 libtiff5
   ```

## Autoboot Setup
To make SPROUT start automatically when the Raspberry Pi powers on:

1. **Make the install script executable**:
   ```bash
   chmod +x install_autoboot.sh
   ```

2. **Run the installation script**:
   ```bash
   sudo ./install_autoboot.sh
   ```

*Note: The service assumes the project is located at `/home/pi/SPROUT`. If you installed it elsewhere, please edit `sprout.service` before running the script.*

## Development / Mock Mode
If running on a desktop, SPROUT will generate a `sprout_display_preview.png` file instead of trying to talk to an e-paper display.

## Prototype Structure
- `src/pet_logic.py`: Core state machine for Sprout.
- `src/renderer.py`: Drawing logic using Pillow.
- `src/main.py`: Main entry point and user interaction.
