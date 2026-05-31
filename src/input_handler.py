import evdev
import threading
import os
import time

class InputHandler:
    def __init__(self, device_path=None):
        self.device_path = device_path
        self.device = None
        self.running = False
        self.thread = None
        self.callback = None
        
        # 8BitDo Zero 2 Mapping (standard Gamepad mode)
        # Note: Codes can vary depending on mode (Start+B, Start+A, etc.)
        # Defaulting to standard Linux event codes for buttons
        self.BUTTON_MAP = {
            304: 'A',
            305: 'B',
            307: 'X',
            308: 'Y',
            310: 'L',
            311: 'R',
            314: 'SELECT',
            315: 'START',
        }
        # D-pad often comes as ABS_X and ABS_Y
        self.ABS_MAP = {
            0: 'DPAD_X', # -1 left, 1 right
            1: 'DPAD_Y', # -1 up, 1 down
        }

    def find_controller(self):
        """Attempts to find the 8BitDo controller among input devices."""
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if "8BitDo Zero 2" in device.name:
                return device.path
        return None

    def start(self, callback):
        """Starts a background thread to listen for input."""
        if not self.device_path:
            self.device_path = self.find_controller()
            
        if not self.device_path:
            print("No 8BitDo Zero 2 controller found. Input handler disabled.")
            return False

        try:
            self.device = evdev.InputDevice(self.device_path)
            self.callback = callback
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print(f"Input handler started on {self.device_path} ({self.device.name})")
            return True
        except Exception as e:
            print(f"Failed to start input handler: {e}")
            return False

    def _run(self):
        try:
            for event in self.device.read_loop():
                if not self.running:
                    break
                
                if event.type == evdev.ecodes.EV_KEY:
                    if event.value == 1: # Button Press
                        button = self.BUTTON_MAP.get(event.code, f"BTN_{event.code}")
                        self.callback('KEY_DOWN', button)
                    elif event.value == 0: # Button Release
                        button = self.BUTTON_MAP.get(event.code, f"BTN_{event.code}")
                        self.callback('KEY_UP', button)
                
                elif event.type == evdev.ecodes.EV_ABS:
                    axis = self.ABS_MAP.get(event.code)
                    if axis:
                        self.callback('ABS', (axis, event.value))
                        
        except Exception as e:
            print(f"Input handler error: {e}")
            self.running = False

    def stop(self):
        self.running = False
        if self.device:
            self.device.close()
