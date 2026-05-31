import time
import json
import os

class SproutPet:
    def __init__(self, name="Sprout"):
        self.name = name
        self.happiness = 50  # 0-100
        self.energy = 50     # 0-100
        self.stress = 20     # 0-100
        self.last_update = time.time()
        self.status = "Healthy"
        
    def update(self):
        """Natural decay of stats over time."""
        now = time.time()
        elapsed = now - self.last_update
        # Decay rates (per hour)
        self.happiness = max(0, self.happiness - (elapsed / 3600) * 5)
        self.energy = max(0, self.energy - (elapsed / 3600) * 10)
        self.stress = min(100, self.stress + (elapsed / 3600) * 2)
        
        self.last_update = now
        self._update_status()

    def _update_status(self):
        if self.stress > 70:
            self.status = "Stressed"
        elif self.energy < 20:
            self.status = "Tired"
        elif self.happiness < 30:
            self.status = "Sad"
        else:
            self.status = "Healthy"

    def check_in(self, mood_score):
        """
        User logs their mood. 
        mood_score: 1 (Bad) to 5 (Great)
        """
        # Helping the user helps Sprout!
        self.happiness = min(100, self.happiness + mood_score * 10)
        self.stress = max(0, self.stress - mood_score * 5)
        self.energy = min(100, self.energy + 5)
        self.update()

    def to_dict(self):
        return {
            "name": self.name,
            "happiness": round(self.happiness, 1),
            "energy": round(self.energy, 1),
            "stress": round(self.stress, 1),
            "status": self.status,
            "last_update": self.last_update
        }

    def save(self, filename="sprout_save.json"):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls, filename="sprout_save.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            pet = cls(data['name'])
            pet.happiness = data['happiness']
            pet.energy = data['energy']
            pet.stress = data['stress']
            pet.status = data['status']
            pet.last_update = data['last_update']
            return pet
        return cls()
