import os
import sys
from flask import Flask, render_template, redirect, url_for, flash, request

# Add src to path so we can import pet_logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pet_logic import SproutPet

app = Flask(__name__)
app.secret_key = "sprout_secret_key" # For flash messages

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprout_save.json")

@app.route('/')
def index():
    pet = SproutPet.load(SAVE_FILE)
    pet.update() # Apply decay
    pet.save(SAVE_FILE)
    return render_template('index.html', pet=pet.to_dict())

@app.route('/action/<name>')
def action(name):
    pet = SproutPet.load(SAVE_FILE)
    pet.update()
    
    if name == 'water':
        pet.water()
        flash("You gave Sprout some water! 🌱")
    elif name == 'pet':
        pet.pet()
        flash("You petted Sprout! ❤️")
    elif name == 'socialize':
        pet.socialize()
        flash("You socialized with Sprout! 👋")
    elif name == 'gratitude':
        pet.record_gratitude()
        flash("You recorded gratitude! ✨")
    elif name == 'sleep':
        pet.toggle_sleep()
        status = "sleeping" if pet.is_sleeping else "awake"
        flash(f"Sprout is now {status}! 💤")
    
    pet.save(SAVE_FILE)
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    pet = SproutPet.load(SAVE_FILE)
    if request.method == 'POST':
        pet.name = request.form.get('name', pet.name)
        pet.theme = request.form.get('theme', pet.theme)
        pet.selected_controller = request.form.get('controller', pet.selected_controller)
        pet.save(SAVE_FILE)
        flash("Settings updated! ✨")
        return redirect(url_for('settings'))
    
    devices = []
    try:
        import evdev
        devices = [evdev.InputDevice(path).name for path in evdev.list_devices()]
    except Exception as e:
        print(f"Error listing input devices: {e}")

    return render_template('settings.html', pet=pet.to_dict(), devices=devices)

@app.route('/update-device')
def update_device():
    # Simulate a device update process
    # In a real scenario, this might trigger a git pull or download a firmware update
    flash("Checking for updates... 📡")
    # Simulate some logic
    flash("SPROUT device is already up to date! (v1.0.2) ✅")
    return redirect(url_for('settings'))

if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible on the local network
    app.run(host='0.0.0.0', port=8080, debug=True)
