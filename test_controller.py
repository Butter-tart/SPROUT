import evdev
from evdev import list_devices, InputDevice

def test_controller():
    print("Searching for input devices...")
    devices = [InputDevice(path) for path in list_devices()]
    
    if not devices:
        print("No input devices found. Are you running with sudo?")
        return

    print("\nAvailable devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device.path} - {device.name}")

    print("\nAttempting to find 8BitDo Zero 2...")
    target = None
    for device in devices:
        if "8BitDo Zero 2" in device.name:
            target = device
            break
    
    if not target:
        print("8BitDo Zero 2 not found by name.")
        try:
            idx = int(input("Select device index to test manually (or enter to exit): "))
            target = devices[idx]
        except (ValueError, IndexError):
            return

    print(f"\nTesting {target.name} ({target.path})")
    print("Press buttons on your controller. Ctrl+C to exit.")
    
    try:
        for event in target.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                print(f"Key Event: Code={event.code}, Value={event.value}")
            elif event.type == evdev.ecodes.EV_ABS:
                print(f"Abs Event: Code={event.code}, Value={event.value}")
    except KeyboardInterrupt:
        print("\nTest finished.")
    except PermissionError:
        print("\nPermission denied. Please run with sudo.")

if __name__ == "__main__":
    test_controller()
