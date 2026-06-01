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

@app.route('/customize', methods=['GET', 'POST'])
def customize():
    pet = SproutPet.load(SAVE_FILE)
    if request.method == 'POST':
        pet.name = request.form.get('name', pet.name)
        pet.theme = request.form.get('theme', pet.theme)
        pet.save(SAVE_FILE)
        flash(f"Character updated! Meet the new {pet.name}! ✨")
        return redirect(url_for('index'))
    
    return render_template('customize.html', pet=pet.to_dict())

if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible on the local network
    app.run(host='0.0.0.0', port=8080, debug=True)
