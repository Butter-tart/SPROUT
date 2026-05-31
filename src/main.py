import sys
import os
import time

import signal

# Try to import e-paper library if available
EPD_AVAILABLE = False
try:
    from waveshare_epd import epd2in13_V4 as epd_driver
    EPD_AVAILABLE = True
    EPD_VERSION = "2.13inch V4"
    print(f"Detected Waveshare {EPD_VERSION} display.")
except ImportError:
    try:
        from waveshare_epd import epd2in13_V3 as epd_driver
        EPD_AVAILABLE = True
        EPD_VERSION = "2.13inch V3"
        print(f"Detected Waveshare {EPD_VERSION} display.")
    except ImportError:
        try:
            from waveshare_epd import epd2in13_V2 as epd_driver
            EPD_AVAILABLE = True
            EPD_VERSION = "2.13inch V2"
            print(f"Detected Waveshare {EPD_VERSION} display.")
        except ImportError:
            try:
                from waveshare_epd import epd2in13 as epd_driver
                EPD_AVAILABLE = True
                EPD_VERSION = "2.13inch (Legacy)"
                print(f"Detected Waveshare {EPD_VERSION} display.")
            except ImportError:
                try:
                    from waveshare_epd import epd2in13bc as epd_driver
                    EPD_AVAILABLE = True
                    EPD_VERSION = "2.13inch (B/C)"
                    print(f"Detected Waveshare {EPD_VERSION} display.")
                except ImportError:
                    try:
                        from waveshare_epd import epd2in13d as epd_driver
                        EPD_AVAILABLE = True
                        EPD_VERSION = "2.13inch (D)"
                        print(f"Detected Waveshare {EPD_VERSION} display.")
                    except ImportError as e:
                        print(f"Waveshare library not found or no compatible 2.13inch driver found: {e}")
                        print("Running in mock mode.")

from pet_logic import SproutPet
from renderer import Renderer

def check_hardware():
    """Diagnostic check for hardware interfaces."""
    print("--- Hardware Diagnostic ---")
    spi_enabled = os.path.exists("/dev/spidev0.0")
    print(f"SPI Interface (/dev/spidev0.0): {'ENABLED' if spi_enabled else 'DISABLED'}")
    
    if not spi_enabled:
        print("WARNING: SPI is not enabled. Waveshare display will NOT work.")
        print("Please run 'sudo raspi-config', go to 'Interfacing Options', and enable SPI.")
    
    try:
        import RPi.GPIO as GPIO
        print(f"RPi.GPIO library: INSTALLED (Version {GPIO.VERSION})")
    except ImportError:
        print("RPi.GPIO library: NOT FOUND")
        
    try:
        from PIL import Image
        print("Pillow library: INSTALLED")
    except ImportError:
        print("Pillow library: NOT FOUND")
    print("---------------------------\n")
    return spi_enabled

def graceful_shutdown(epd):
    """Clear screen and put to sleep before exiting."""
    if epd:
        try:
            print("\nShutting down: Clearing display...")
            epd.init()
            epd.Clear(0xFF)
            print("Putting display to sleep...")
            epd.sleep()
            # On some drivers, we might need to module-level reset or close SPI
            # but usually epd.sleep() is enough for Waveshare
        except Exception as e:
            print(f"Error during shutdown: {e}")

def main():
    # Diagnostic check
    check_hardware()
    
    # Loop mode if specified via arguments
    loop_mode = "--loop" in sys.argv
    
    epd = None
    
    def signal_handler(sig, frame):
        print(f"\nReceived signal {sig}. Graceful shutdown...")
        if EPD_AVAILABLE and epd:
            graceful_shutdown(epd)
        sys.exit(0)

    # Register signals for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            pet = SproutPet.load()
            pet.update()
            
            # Check if we are running in interactive mode or as a service
            is_interactive = os.isatty(sys.stdin.fileno()) and not loop_mode
            
            if is_interactive:
                print(f"Welcome back to {pet.name}'s mental health check-in!")
                print(f"Current Status: {pet.status}")
                print(f"Happiness: {pet.happiness}% | Energy: {pet.energy}% | Stress: {pet.stress}%")
                print("\nHow are you feeling today? (1-5)")
                print("1: Not great")
                print("2: A bit down")
                print("3: Okay")
                print("4: Good")
                print("5: Fantastic!")
                
                try:
                    score = int(input(">> "))
                    if 1 <= score <= 5:
                        pet.check_in(score)
                        print(f"Thanks for sharing! {pet.name} feels better now too.")
                    else:
                        print("Invalid input, no check-in recorded.")
                except ValueError:
                    print("Invalid input, no check-in recorded.")
                except EOFError:
                    # Handle case where input is closed
                    break
            else:
                if not loop_mode:
                    print("\nNon-interactive mode: Skipping mood check-in.")

            pet.save()
            
            # Render the screen
            renderer = Renderer()
            renderer.draw_pet(pet.status)
            renderer.draw_stats(pet.to_dict())
            
            if EPD_AVAILABLE:
                try:
                    if epd is None:
                        print("Initializing display...")
                        epd = epd_driver.EPD()
                    
                    # Some versions use epd.init(), some use epd.init(epd.FULL_UPDATE)
                    print(f"Driver {EPD_VERSION} init...")
                    try:
                        epd.init(epd.FULL_UPDATE)
                    except (TypeError, AttributeError):
                        try:
                            epd.init()
                        except Exception as e:
                            print(f"Init failed: {e}. Trying alternative init...")
                            # Some older drivers might need different approach
                    
                    print("Updating display content...")
                    epd.display(epd.getbuffer(renderer.get_image()))
                    
                    print("Putting display to sleep...")
                    epd.sleep()
                    print("Display updated successfully.")
                except Exception as e:
                    print(f"Error updating display: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                renderer.save_preview("sprout_display_preview.png")
                print("Preview saved to sprout_display_preview.png")

            if not loop_mode:
                break
            
            # In loop mode, wait before next update (e.g., 5 minutes)
            print("Loop mode active. Waiting 5 minutes for next update...")
            time.sleep(300)
    finally:
        if EPD_AVAILABLE and epd:
            graceful_shutdown(epd)

if __name__ == "__main__":
    main()
