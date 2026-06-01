import evdev
import threading
import os
import time

class InputHandler:
    def __init__(self, target_name=None):
        self.target_name = target_name
        self.device_path = None
        self.device = None
        self.running = False
        self.thread = None
        self.callback = None
        self.reconnect_delay = 5 # seconds
        
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
        """Attempts to find the specified or default controller among input devices."""
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for device in devices:
                if self.target_name:
                    if self.target_name == device.name:
                        return device.path
                else:
                    # Default fallback
                    if "8BitDo Zero 2" in device.name:
                        return device.path
        except Exception as e:
            print(f"Error listing devices: {e}")
        return None

    def start(self, callback):
        """Starts a background thread to listen for input and handle reconnection."""
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self._run_monitor, daemon=True)
        self.thread.start()
        print("Input handler monitor started.")
        return True

    def _run_monitor(self):
        """Monitor loop that handles connection and reconnection."""
        while self.running:
            if not self.device:
                path = self.find_controller()
                if path:
                    self.device_path = path
                    try:
                        self.device = evdev.InputDevice(self.device_path)
                        print(f"Connected to 8BitDo Zero 2 at {self.device_path}")
                        self._process_events()
                    except Exception as e:
                        print(f"Failed to connect to device at {self.device_path}: {e}")
                        self.device = None
                else:
                    # Optional: only print every few attempts to avoid log spam
                    pass
            
            if self.running and not self.device:
                time.sleep(self.reconnect_delay)

    def _process_events(self):
        """Internal loop to process events from the current device."""
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
                        
        except (OSError, EOFError) as e:
            print(f"Controller disconnected: {e}")
        except Exception as e:
            print(f"Input handler error: {e}")
        finally:
            if self.device:
                try:
                    self.device.close()
                except:
                    pass
                self.device = None

    def _run(self):
        # Kept for compatibility if anything calls it directly, but now using _run_monitor
        self._run_monitor()

    def stop(self):
        self.running = False
        if self.device:
            self.device.close()
