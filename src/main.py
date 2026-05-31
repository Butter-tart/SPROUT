import sys
import os
import time

# Try to import e-paper library if available
EPD_AVAILABLE = False
try:
    from waveshare_epd import epd2in13_V2 as epd_driver
    EPD_AVAILABLE = True
    print("Detected Waveshare 2.13inch V2 display.")
except ImportError:
    try:
        from waveshare_epd import epd2in13 as epd_driver
        EPD_AVAILABLE = True
        print("Detected Waveshare 2.13inch (Legacy) display.")
    except ImportError as e:
        print(f"Waveshare library not found or wrong driver: {e}")
        print("Running in mock mode.")

from pet_logic import SproutPet
from renderer import Renderer

def main():
    # Loop mode if specified via arguments
    loop_mode = "--loop" in sys.argv
    
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
                pass
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
                print("Initializing display...")
                epd = epd_driver.EPD()
                # Some versions use epd.init(), some use epd.init(epd.FULL_UPDATE)
                try:
                    epd.init(epd.FULL_UPDATE)
                except TypeError:
                    epd.init()
                
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

if __name__ == "__main__":
    main()
