import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont

print("--- SPROUT Display Tester ---")

drivers = [
    ('epd2in13_V4', "2.13inch V4"),
    ('epd2in13_V3', "2.13inch V3"),
    ('epd2in13_V2', "2.13inch V2"),
    ('epd2in13', "2.13inch Legacy"),
    ('epd2in13bc', "2.13inch B/C"),
    ('epd2in13d', "2.13inch D"),
]

def test_driver(module_name, name):
    print(f"\nTesting {name} ({module_name})...")
    try:
        # Import dynamically
        epd_module = __import__('waveshare_epd.' + module_name, fromlist=['EPD'])
        epd = epd_module.EPD()
        
        print(f"Initializing {name}...")
        try:
            epd.init(epd.FULL_UPDATE)
        except:
            epd.init()
            
        print("Creating test image...")
        # Most 2.13 screens are 250x122 or 212x104
        # We'll use a safe size or get from epd
        width = getattr(epd, 'width', 250)
        height = getattr(epd, 'height', 122)
        
        image = Image.new('1', (width, height), 255)  # 255: white
        draw = ImageDraw.Draw(image)
        
        draw.rectangle((0, 0, width-1, height-1), outline=0)
        draw.text((10, 10), f"Test: {name}", fill=0)
        draw.text((10, 30), f"Time: {time.strftime('%H:%M:%S')}", fill=0)
        draw.text((10, 50), "If you see this, driver works!", fill=0)
        
        print("Updating display...")
        epd.display(epd.getbuffer(image))
        
        time.sleep(2)
        print("Clearing display...")
        epd.Clear(0xFF)
        
        print("Going to sleep...")
        epd.sleep()
        print(f"SUCCESS with {name}!")
        return True
    except ImportError:
        print(f"Driver {module_name} not installed.")
    except Exception as e:
        print(f"Failed with {name}: {e}")
    return False

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Warning: This script might need sudo to access SPI/GPIO.")
    
    # Check SPI
    if not os.path.exists("/dev/spidev0.0"):
        print("ERROR: SPI (/dev/spidev0.0) is not enabled!")
    
    success = False
    for module, name in drivers:
        if test_driver(module, name):
            success = True
            print(f"\n*** FOUND WORKING DRIVER: {name} ***")
            print(f"Update SPROUT/src/main.py to use this driver if SPROUT is still failing.")
            break
            
    if not success:
        print("\nCould not find a working driver. Please check your hardware connection and SPI settings.")
