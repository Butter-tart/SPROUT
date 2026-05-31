import sys
import os
import time

# Try to import e-paper library if available
EPD_AVAILABLE = False
try:
    from waveshare_epd import epd2in13_V2 as epd_driver
    EPD_AVAILABLE = True
except ImportError:
    print("Waveshare library not found. Running in mock mode.")

from pet_logic import SproutPet
from renderer import Renderer

def main():
    pet = SproutPet.load()
    pet.update()
    
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

    pet.save()
    
    # Render the screen
    renderer = Renderer()
    renderer.draw_pet(pet.status)
    renderer.draw_stats(pet.to_dict())
    
    if EPD_AVAILABLE:
        try:
            epd = epd_driver.EPD()
            epd.init(epd.FULL_UPDATE)
            epd.display(epd.getbuffer(renderer.get_image()))
            epd.sleep()
            print("Display updated successfully.")
        except Exception as e:
            print(f"Error updating display: {e}")
    else:
        renderer.save_preview("sprout_display_preview.png")
        print("Preview saved to sprout_display_preview.png")

if __name__ == "__main__":
    main()
