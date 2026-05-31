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
try:
    from input_handler import InputHandler
    INPUT_AVAILABLE = True
except ImportError:
    INPUT_AVAILABLE = False
    print("evdev library not found. Input handler disabled.")

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

def show_loading_animation(epd):
    """Shows a hopping character animation on the e-ink display."""
    print("Showing loading animation...")
    renderer = Renderer()
    steps = 10
    
    # Pre-init display for partial updates if possible
    if EPD_AVAILABLE and epd:
        try:
            # Full update for the first frame to clear everything
            epd.init()
            renderer.draw_loading_frame(0)
            epd.display(epd.getbuffer(renderer.get_image()))
            
            # Some drivers need to be initialized for partial update
            if hasattr(epd, 'init'):
                try:
                    # Some drivers use epd.init(epd.PART_UPDATE)
                    if hasattr(epd, 'PART_UPDATE'):
                        epd.init(epd.PART_UPDATE)
                    else:
                        epd.init()
                except:
                    epd.init()

            # Switch to partial update mode if supported
            # Note: partial update is very driver-dependent
            for i in range(1, steps + 1):
                progress = i / steps
                renderer.draw_loading_frame(progress)
                
                # Check for display_Partial or similar
                if hasattr(epd, 'display_Partial'):
                    epd.display_Partial(epd.getbuffer(renderer.get_image()))
                elif hasattr(epd, 'display_partial'):
                    epd.display_partial(epd.getbuffer(renderer.get_image()))
                else:
                    # Fallback to full update but it will flicker
                    epd.display(epd.getbuffer(renderer.get_image()))
                
            # Put display back to sleep after animation
            if hasattr(epd, 'sleep'):
                epd.sleep()
                time.sleep(0.5) # Wait for sleep
        except Exception as e:
            print(f"Loading animation failed: {e}")
    else:
        # Mock mode loading animation
        for i in range(steps + 1):
            progress = i / steps
            renderer.draw_loading_frame(progress)
            renderer.save_preview(f"loading_frame_{i}.png")
            print(f"Loading... {int(progress*100)}%")
            time.sleep(0.1)

def main():
    # Diagnostic check
    check_hardware()
    
    # Loop mode if specified via arguments
    loop_mode = "--loop" in sys.argv
    
    pet = SproutPet.load()
    epd = None
    
    # Menu State
    menu_active = False
    menu_selection = 0
    menu_options = ["Walk Timer", "Check-in", "Cancel"]
    
    def input_callback(event_type, value):
        nonlocal menu_active, menu_selection, pet
        
        if event_type == 'KEY_DOWN':
            print(f"Input: {value}")
            if value == 'START':
                menu_active = not menu_active
            
            elif menu_active:
                if value == 'DPAD_Y' or value == 'BTN_1': # BTN_1 might be Up on some modes
                    menu_selection = (menu_selection - 1) % len(menu_options)
                elif value == 'BTN_2': # Down
                    menu_selection = (menu_selection + 1) % len(menu_options)
                elif value == 'A':
                    # Select option
                    selection = menu_options[menu_selection]
                    if selection == "Walk Timer":
                        if pet.is_walking:
                            pet.stop_walk()
                            print("Walking stopped.")
                        else:
                            pet.start_walk()
                            print("Walking started!")
                    elif selection == "Check-in":
                        print("Check-in selected (Interactive only for now)")
                    
                    menu_active = False
                    pet.save()
            
            elif value == 'A' and not menu_active:
                # Shortcut to start/stop walk
                if pet.is_walking:
                    pet.stop_walk()
                else:
                    pet.start_walk()
                pet.save()

        elif event_type == 'ABS':
            axis, axis_val = value
            if menu_active:
                if axis == 'DPAD_Y':
                    if axis_val == -1: # Up
                        menu_selection = (menu_selection - 1) % len(menu_options)
                    elif axis_val == 1: # Down
                        menu_selection = (menu_selection + 1) % len(menu_options)

    # Start input handler
    if INPUT_AVAILABLE:
        input_handler = InputHandler()
        input_handler.start(input_callback)
    else:
        print("Input handler skipped (evdev missing).")

    if EPD_AVAILABLE:
        try:
            print("Initializing display for loading screen...")
            epd = epd_driver.EPD()
            show_loading_animation(epd)
        except Exception as e:
            print(f"Could not show loading animation: {e}")
    else:
        show_loading_animation(None)
    
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
            pet.save()
            
            # Render the screen
            renderer = Renderer()
            renderer.draw_pet(pet.to_dict())
            renderer.draw_stats(pet.to_dict())
            
            if menu_active:
                renderer.draw_menu(menu_options, menu_selection)
            
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
