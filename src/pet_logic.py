import time
import json
import os

class SproutPet:
    def __init__(self, name="Sprout"):
        self.name = name
        self.happiness = 50  # 0-100
        self.energy = 50     # 0-100
        self.stress = 20     # 0-100
        self.sunshine = 50   # 0-100 (New sunshine/outdoor metric)
        self.theme = "Default" # Default, Dark, High Contrast
        self.experience = 0   # Total XP
        self.level = 1       # 1-4 Growth stages
        self.walk_time_today = 0  # Total walk minutes today
        self.is_walking = False
        self.walk_start_timestamp = None
        self.last_update = time.time()
        self.status = "Healthy"
        
    def update(self):
        """Natural decay of stats over time."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Update walk timer if active
        if self.is_walking and self.walk_start_timestamp:
            walk_elapsed = now - self.walk_start_timestamp
            # Convert to minutes for the metric
            self.walk_time_today += (walk_elapsed / 60)
            self.walk_start_timestamp = now
            
            # Walking helps health!
            self.happiness = min(100, self.happiness + (walk_elapsed / 60) * 2)
            self.sunshine = min(100, self.sunshine + (walk_elapsed / 60) * 5)
            self.stress = max(0, self.stress - (walk_elapsed / 60) * 1)
        
        # Decay rates (per hour)
        self.happiness = max(0, self.happiness - (elapsed / 3600) * 5)
        self.energy = max(0, self.energy - (elapsed / 3600) * 10)
        self.sunshine = max(0, self.sunshine - (elapsed / 3600) * 8)
        self.stress = min(100, self.stress + (elapsed / 3600) * 2)
        
        # Gain XP for being healthy and getting sun
        if self.status == "Healthy":
            self.experience += (elapsed / 3600) * 10
        if self.sunshine > 70:
            self.experience += (elapsed / 3600) * 5
            
        self.last_update = now
        self._update_status()
        self._check_level_up()

    def _check_level_up(self):
        """Growth stages: 1: Sprout, 2: Bud, 3: Bloom, 4: Big Flower"""
        # Thresholds for leveling up
        if self.level == 1 and self.experience >= 100:
            self.level = 2
        elif self.level == 2 and self.experience >= 300:
            self.level = 3
        elif self.level == 3 and self.experience >= 600:
            self.level = 4

    def _update_status(self):
        if self.sunshine < 20:
            self.status = "Needs Sun"
        elif self.stress > 70:
            self.status = "Stressed"
        elif self.energy < 20:
            self.status = "Tired"
        elif self.happiness < 30:
            self.status = "Sad"
        else:
            self.status = "Healthy"

    def check_in(self, mood_score, got_sunshine=False):
        """
        User logs their mood and whether they went outside. 
        mood_score: 1 (Bad) to 5 (Great)
        got_sunshine: Boolean
        """
        # Helping the user helps Sprout!
        self.happiness = min(100, self.happiness + mood_score * 10)
        self.stress = max(0, self.stress - mood_score * 5)
        self.energy = min(100, self.energy + 5)
        
        # XP gain from check-in
        self.experience += mood_score * 5
        
        if got_sunshine:
            self.sunshine = min(100, self.sunshine + 40)
            self.happiness = min(100, self.happiness + 10)
            self.experience += 20
            
        self.update()

    def start_walk(self):
        if not self.is_walking:
            self.is_walking = True
            self.walk_start_timestamp = time.time()
            self.update()

    def stop_walk(self):
        if self.is_walking:
            self.update()
            self.is_walking = False
            self.walk_start_timestamp = None

    def to_dict(self):
        return {
            "name": self.name,
            "happiness": round(self.happiness, 1),
            "energy": round(self.energy, 1),
            "stress": round(self.stress, 1),
            "sunshine": round(self.sunshine, 1),
            "theme": self.theme,
            "experience": round(self.experience, 1),
            "level": self.level,
            "walk_time_today": round(self.walk_time_today, 1),
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
            pet.sunshine = data.get('sunshine', 50)
            pet.theme = data.get('theme', "Default")
            pet.experience = data.get('experience', 0)
            pet.level = data.get('level', 1)
            pet.walk_time_today = data.get('walk_time_today', 0)
            pet.status = data['status']
            pet.last_update = data['last_update']
            return pet
        return cls()
