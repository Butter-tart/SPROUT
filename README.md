# SPROUT: Mental Health Tamagotchi
Mental health companion for Raspberry Pi Zero 2 WH & Waveshare e-Paper.

## Features
- Mood & Sunshine tracking; growth stages.
- 8BitDo Zero 2 support & Web App.
- E-Ink optimized.

## Setup
1. **SPI**: `sudo raspi-config` -> Interface -> SPI -> Yes.
2. **Deps**: `sudo apt install python3-pip python3-pil python3-numpy fonts-liberation`
3. **E-Ink Lib**: Clone [waveshare/e-Paper](https://github.com/waveshare/e-Paper), run `sudo python3 setup.py install` in `python` dir.
4. **Flask**: `pip3 install flask`
5. **Run**: `python3 src/main.py` & `python3 src/webapp.py` (port 8080).

## Controller
- `bluetoothctl`: `scan on`, `pair [MAC]`, `trust [MAC]`, `connect [MAC]`.
- **START**: Menu | **A**: Select/Walk.

## Troubleshooting
- **Test**: `sudo python3 test_display.py` or `test_controller.py`.
- **SPI**: Check `ls /dev/spi*`.
- **Perms**: `sudo usermod -a -G spi,gpio,i2c,input $USER`.

## Autoboot
`chmod +x install_autoboot.sh && sudo ./install_autoboot.sh`

## Dev
Runs in mock mode (generates `sprout_display_preview.png`) on non-Pi systems.
