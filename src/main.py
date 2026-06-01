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

    # Mock Haptics/LED check
    print("Haptics Interface: NOT DETECTED (Using dummy hooks)")
    print("LED Interface: ONBOARD ONLY")
    print("---------------------------\n")
    return spi_enabled

def trigger_haptic():
    """Dummy hook for haptic feedback."""
    print("[HAPTIC] *Bzzzt*")

def set_led(r, g, b):
    """Dummy hook for RGB LED control."""
    print(f"[LED] Setting color to ({r}, {g}, {b})")

def get_mock_weather():
    """Mock weather service."""
    # In a real app, this would use an API or local sensor
    hour = time.localtime().tm_hour
    if 6 <= hour <= 18:
        return "Sunny"
    return "Clear Night"

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

def show_loading_screen(epd):
    """Shows a static loading screen on the e-ink display."""
    print("Showing loading screen...")
    renderer = Renderer()
    renderer.draw_static_loading()
    
    # Save the static loading image for easy editing
    renderer.save_preview("loading.png")
    
    if EPD_AVAILABLE and epd:
        try:
            epd.init()
            epd.display(epd.getbuffer(renderer.get_image()))
            if hasattr(epd, 'sleep'):
                epd.sleep()
                time.sleep(0.5)
        except Exception as e:
            print(f"Displaying loading screen failed: {e}")
    else:
        print("Loading... (Image saved to loading.png)")
        time.sleep(1.0)

def main():
    # Diagnostic check
    check_hardware()
    
    # Loop mode by default, can be disabled if needed (though usually we want it on)
    loop_mode = "--no-loop" not in sys.argv
    
    pet = SproutPet.load()
    epd = None
    
    # Menu State
    menu_active = False
    menu_level = "Main" # Main, Settings, Breathing
    menu_selection = 0
    menu_options_main = ["Water", "Breathing", "Gratitude", "Social", "Walk", "Sleep", "Settings", "Quit"]
    menu_options_settings = ["Theme: Default", "Theme: Dark", "Theme: High Contrast", "Restart", "Shutdown", "Back"]

    def run_breathing_exercise():
        nonlocal epd, pet
        print("Starting breathing exercise...")
        trigger_haptic()
        duration = 30 # seconds
        start_time = time.time()
        while time.time() - start_time < duration:
            progress = ((time.time() - start_time) % 6) / 6 # 6 second breath cycle
            
            # LED feedback for breathing
            if progress < 0.5:
                set_led(0, 0, int(progress * 2 * 255)) # Blue fade in
            else:
                set_led(0, 0, int((1.0 - progress) * 2 * 255)) # Blue fade out

            renderer = Renderer(theme=pet.theme)
            renderer.draw_breathing_frame(progress)
            
            if EPD_AVAILABLE and epd:
                # Use partial update if possible for animation
                epd.init()
                epd.display(epd.getbuffer(renderer.get_image()))
                epd.sleep()
            else:
                renderer.save_preview("sprout_display_preview.png")
                time.sleep(0.5)
            
            # Allow break? For now just run
        trigger_haptic()
        set_led(0, 0, 0)
        pet.stress = max(0, pet.stress - 20)
        pet.experience += 20
        pet.save()

    def input_callback(event_type, value):
        nonlocal menu_active, menu_level, menu_selection, pet, epd
        
        # Helper to get current options
        def get_options():
            if menu_level == "Settings":
                return menu_options_settings
            return menu_options_main

        if event_type == 'KEY_DOWN':
            print(f"Input: {value}")
            if value == 'START':
                menu_active = not menu_active
                menu_level = "Main"
                menu_selection = 0
            
            elif value == 'SELECT': # Using SELECT as petting
                trigger_haptic()
                pet.pet()
                pet.save()
                print("Sprout was petted!")
            
            elif menu_active:
                options = get_options()
                if value == 'DPAD_Y' or value == 'BTN_1': # Up
                    menu_selection = (menu_selection - 1) % len(options)
                elif value == 'BTN_2': # Down
                    menu_selection = (menu_selection + 1) % len(options)
                elif value == 'A':
                    selection = options[menu_selection]
                    
                    if menu_level == "Main":
                        if selection == "Water":
                            trigger_haptic()
                            pet.water()
                            menu_active = False
                        elif selection == "Breathing":
                            menu_active = False
                            run_breathing_exercise()
                        elif selection == "Gratitude":
                            trigger_haptic()
                            pet.record_gratitude()
                            menu_active = False
                        elif selection == "Social":
                            trigger_haptic()
                            pet.socialize()
                            menu_active = False
                        elif selection == "Walk":
                            if pet.is_walking:
                                pet.stop_walk()
                            else:
                                pet.start_walk()
                            menu_active = False
                        elif selection == "Sleep":
                            pet.toggle_sleep()
                            menu_active = False
                        elif selection == "Settings":
                            menu_level = "Settings"
                            menu_selection = 0
                        elif selection == "Quit":
                            menu_active = False
                    
                    elif menu_level == "Settings":
                        if "Theme:" in selection:
                            new_theme = selection.split(": ")[1]
                            pet.theme = new_theme
                            print(f"Theme changed to {new_theme}")
                        elif selection == "Restart":
                            print("Restarting system...")
                            os.system("sudo reboot")
                        elif selection == "Shutdown":
                            print("Shutting down system...")
                            os.system("sudo poweroff")
                        elif selection == "Back":
                            menu_level = "Main"
                            menu_selection = 6 # Back to Settings option
                    
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
                options = get_options()
                if axis == 'DPAD_Y':
                    if axis_val == -1: # Up
                        menu_selection = (menu_selection - 1) % len(options)
                    elif axis_val == 1: # Down
                        menu_selection = (menu_selection + 1) % len(options)

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
            show_loading_screen(epd)
        except Exception as e:
            print(f"Could not show loading screen: {e}")
    else:
        show_loading_screen(None)
    
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
            weather = get_mock_weather()
            renderer = Renderer(theme=pet.theme)
            renderer.draw_pet(pet.to_dict())
            renderer.draw_stats(pet.to_dict())
            
            # Show weather info if relevant - Improved positioning
            if weather == "Sunny" and pet.sunshine < 50:
                renderer.draw.text((10, 30), "Go outside!", fill=renderer.fg_color)
            elif "Night" in weather and not pet.is_sleeping:
                renderer.draw.text((10, 30), "Time for bed?", fill=renderer.fg_color)
            
            if menu_active:
                options = menu_options_settings if menu_level == "Settings" else menu_options_main
                renderer.draw_menu(options, menu_selection, title=menu_level.upper())
            
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
