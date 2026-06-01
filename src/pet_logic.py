import time
import json
import os

class SproutPet:
    def __init__(self, name="Sprout"):
        self.name = name
        self.happiness = 50  # 0-100
        self.energy = 50     # 0-100
        self.stress = 20     # 0-100
        self.sunshine = 50   # 0-100
        self.hydration = 50  # 0-100 (New)
        self.social = 50     # 0-100 (New)
        self.theme = "Default" 
        self.experience = 0   
        self.level = 1       
        self.walk_time_today = 0  
        self.is_walking = False
        self.walk_start_timestamp = None
        self.last_update = time.time()
        self.last_walk_timestamp = time.time()  # New: Track when the last walk ended
        self.status = "Healthy"
        self.is_sleeping = False # New
        self.streak = 0 # New
        self.last_check_in_day = None # New
        self.gratitude_count = 0 # New
        self.selected_controller = None # New: Stores the name of the selected controller
        
    def _check_level_up(self):
        """Growth stages: 1: Sprout, 2: Bud, 3: Bloom, 4: Big Flower"""
        # Thresholds for leveling up
        if self.level == 1 and self.experience >= 100:
            self.level = 2
        elif self.level == 2 and self.experience >= 300:
            self.level = 3
        elif self.level == 3 and self.experience >= 600:
            self.level = 4

    def update(self):
        """Natural decay of stats over time."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Check for daily streak update
        current_day = time.strftime("%Y-%m-%d", time.localtime(now))
        if self.last_check_in_day and self.last_check_in_day != current_day:
            # Check if it was yesterday or further back
            try:
                last_day_ts = time.mktime(time.strptime(self.last_check_in_day, "%Y-%m-%d"))
                # Use current day at 00:00 for comparison to be more robust
                current_day_ts = time.mktime(time.strptime(current_day, "%Y-%m-%d"))
                
                if current_day_ts - last_day_ts <= 86400: # Exactly 1 day or less gap
                    self.streak += 1
                else:
                    # Reset streak if missed more than a day
                    self.streak = 1
                self.last_check_in_day = current_day
            except Exception:
                self.streak = 1
                self.last_check_in_day = current_day
        elif not self.last_check_in_day:
            self.streak = 1
            self.last_check_in_day = current_day

        # Update walk timer if active
        if self.is_walking and self.walk_start_timestamp:
            walk_elapsed = now - self.walk_start_timestamp
            self.walk_time_today += (walk_elapsed / 60)
            self.walk_start_timestamp = now
            
            self.happiness = min(100, self.happiness + (walk_elapsed / 60) * 2)
            self.sunshine = min(100, self.sunshine + (walk_elapsed / 60) * 5)
            self.stress = max(0, self.stress - (walk_elapsed / 60) * 1)
        
        # Decay rates (per hour)
        if not self.is_sleeping:
            # Normal decay
            self.energy = max(0, self.energy - (elapsed / 3600) * 10)
            self.sunshine = max(0, self.sunshine - (elapsed / 3600) * 8)
            self.hydration = max(0, self.hydration - (elapsed / 3600) * 10)
            self.social = max(0, self.social - (elapsed / 3600) * 4)
            self.stress = min(100, self.stress + (elapsed / 3600) * 2)
            
            # Happiness decay: faster if not walking
            if not self.is_walking:
                # Calculate how long since the last walk (in hours)
                hours_since_walk = (now - self.last_walk_timestamp) / 3600
                # Base decay is 5, increases by 2 for every hour since last walk, capped at 15
                happiness_decay_rate = 5 + min(10, hours_since_walk * 2)
                self.happiness = max(0, self.happiness - (elapsed / 3600) * happiness_decay_rate)
            else:
                # When walking, happiness is already increasing in the walk section above,
                # but we can still have a small baseline decay if desired. 
                # For now, let's keep it as is (no extra decay while walking).
                pass
        else:
            # Energy recovers during sleep
            self.energy = min(100, self.energy + (elapsed / 3600) * 20)
            # Other stats decay slower
            self.happiness = max(0, self.happiness - (elapsed / 3600) * 1)
            self.hydration = max(0, self.hydration - (elapsed / 3600) * 3)
        
        # Gain XP for being healthy
        if self.status == "Healthy" and not self.is_sleeping:
            self.experience += (elapsed / 3600) * 10
            
        self.last_update = now
        self._update_status()
        self._check_level_up()

    def water(self):
        self.hydration = min(100, self.hydration + 40)
        self.happiness = min(100, self.happiness + 5)
        self.experience += 5

    def socialize(self):
        self.social = min(100, self.social + 30)
        self.stress = max(0, self.stress - 10)
        self.experience += 10

    def record_gratitude(self):
        self.gratitude_count += 1
        self.happiness = min(100, self.happiness + 15)
        self.stress = max(0, self.stress - 10)
        self.experience += 15

    def pet(self):
        self.happiness = min(100, self.happiness + 5)
        self.stress = max(0, self.stress - 2)
        self.experience += 2

    def toggle_sleep(self):
        self.is_sleeping = not self.is_sleeping
        self.update()

    def start_walk(self):
        if not self.is_walking:
            self.is_walking = True
            self.walk_start_timestamp = time.time()
            print("Walk started!")

    def stop_walk(self):
        if self.is_walking:
            now = time.time()
            walk_elapsed = now - self.walk_start_timestamp
            self.walk_time_today += (walk_elapsed / 60)
            self.is_walking = False
            self.walk_start_timestamp = None
            self.last_walk_timestamp = now  # Reset the last walk timer
            print(f"Walk stopped. Duration: {walk_elapsed/60:.1f} minutes.")

    def _update_status(self):
        if self.is_sleeping:
            self.status = "Zzz..."
        elif self.hydration < 20:
            self.status = "Thirsty"
        elif self.sunshine < 20:
            self.status = "Needs Sun"
        elif self.stress > 70:
            self.status = "Stressed"
        elif self.energy < 20:
            self.status = "Tired"
        elif self.happiness < 30:
            self.status = "Sad"
        else:
            self.status = "Healthy"

    def to_dict(self):
        return {
            "name": self.name,
            "happiness": round(self.happiness, 1),
            "energy": round(self.energy, 1),
            "stress": round(self.stress, 1),
            "sunshine": round(self.sunshine, 1),
            "hydration": round(self.hydration, 1),
            "social": round(self.social, 1),
            "theme": self.theme,
            "experience": round(self.experience, 1),
            "level": self.level,
            "walk_time_today": round(self.walk_time_today, 1),
            "status": self.status,
            "last_update": self.last_update,
            "is_sleeping": self.is_sleeping,
            "streak": self.streak,
            "gratitude_count": self.gratitude_count,
            "last_walk_timestamp": self.last_walk_timestamp,
            "selected_controller": self.selected_controller
        }

    def save(self, filename="sprout_save.json"):
        import fcntl
        try:
            with open(filename, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(self.to_dict(), f)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            print(f"Error saving pet: {e}")

    @classmethod
    def load(cls, filename="sprout_save.json"):
        if os.path.exists(filename):
            import fcntl
            try:
                with open(filename, 'r') as f:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    data = json.load(f)
                    fcntl.flock(f, fcntl.LOCK_UN)
                pet = cls(data['name'])
                pet.happiness = data.get('happiness', 50)
                pet.energy = data.get('energy', 50)
                pet.stress = data.get('stress', 20)
                pet.sunshine = data.get('sunshine', 50)
                pet.hydration = data.get('hydration', 50)
                pet.social = data.get('social', 50)
                pet.theme = data.get('theme', "Default")
                pet.experience = data.get('experience', 0)
                pet.level = data.get('level', 1)
                pet.walk_time_today = data.get('walk_time_today', 0)
                pet.status = data.get('status', 'Healthy')
                pet.last_update = data.get('last_update', time.time())
                pet.is_sleeping = data.get('is_sleeping', False)
                pet.streak = data.get('streak', 0)
                pet.gratitude_count = data.get('gratitude_count', 0)
                pet.last_walk_timestamp = data.get('last_walk_timestamp', time.time())
                pet.selected_controller = data.get('selected_controller', None)
                return pet
            except Exception:
                return cls()
        return cls()
