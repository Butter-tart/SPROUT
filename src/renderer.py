from PIL import Image, ImageDraw, ImageFont
import os
import time

class Renderer:
    def __init__(self, width=250, height=122, theme="Default"):
        self.width = width
        self.height = height
        self.theme = theme
        
        # Colors: 0 is Black, 255 is White (or 1 for some 1-bit modes, PIL '1' uses 0/255)
        self.bg_color = 255
        self.fg_color = 0
        
        if theme == "Dark":
            self.bg_color = 0
            self.fg_color = 255
        elif theme == "High Contrast":
            # Potentially different later, for now just sharp B&W
            self.bg_color = 255
            self.fg_color = 0

        # E-ink typically uses 1-bit color (black and white)
        self.image = Image.new('1', (self.width, self.height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        
    def draw_pet(self, pet_data, x=60, y=60):
        """Draws a character based on level and status at position (x, y)."""
        level = pet_data.get('level', 1)
        status = pet_data.get('status', 'Healthy')
        
        # Simple procedural character
        cx, cy = x, y
        
        if level == 1:
            # Stage 1: Simple Sprout
            r = 15
            self.draw.ellipse((cx-r, cy, cx+r, cy+r*2), outline=self.fg_color, fill=self.bg_color) # Pot/Base
            self.draw.line((cx, cy, cx, cy-15), fill=self.fg_color, width=2) # Stem
            self.draw.ellipse((cx-8, cy-18, cx, cy-12), outline=self.fg_color) # Leaf 1
            self.draw.ellipse((cx, cy-18, cx+8, cy-12), outline=self.fg_color) # Leaf 2
        
        elif level == 2:
            # Stage 2: Bud
            r = 20
            self.draw.ellipse((cx-r, cy+5, cx+r, cy+r*2+5), outline=self.fg_color, fill=self.bg_color) # Pot
            self.draw.line((cx, cy+5, cx, cy-20), fill=self.fg_color, width=2) # Stem
            # Leaves
            self.draw.ellipse((cx-12, cy-10, cx, cy-5), outline=self.fg_color)
            self.draw.ellipse((cx, cy-10, cx+12, cy-5), outline=self.fg_color)
            # Bud
            self.draw.ellipse((cx-8, cy-28, cx+8, cy-20), outline=self.fg_color, fill=self.bg_color)
            
        elif level == 3:
            # Stage 3: Small Flower
            r = 25
            self.draw.ellipse((cx-r, cy+10, cx+r, cy+r*2+10), outline=self.fg_color, fill=self.bg_color) # Pot
            self.draw.line((cx, cy+10, cx, cy-25), fill=self.fg_color, width=3) # Stem
            # Flower petals
            pr = 10
            self.draw.ellipse((cx-pr, cy-35, cx+pr, cy-15), outline=self.fg_color) # Center
            for i in range(4):
                import math
                angle = i * (math.pi / 2)
                px = cx + math.cos(angle) * 12
                py = cy - 25 + math.sin(angle) * 12
                self.draw.ellipse((px-8, py-8, px+8, py+8), outline=self.fg_color)

        else:
            # Stage 4: Big Flower
            r = 30
            self.draw.ellipse((cx-r, cy+15, cx+r, cy+r*2+15), outline=self.fg_color, fill=self.bg_color) # Pot
            self.draw.line((cx, cy+15, cx, cy-30), fill=self.fg_color, width=4) # Stem
            # Large Flower
            cr = 12
            self.draw.ellipse((cx-cr, cy-42, cx+cr, cy-18), outline=self.fg_color, fill=self.bg_color) # Center
            for i in range(6):
                import math
                angle = i * (math.pi / 3)
                px = cx + math.cos(angle) * 20
                py = cy - 30 + math.sin(angle) * 20
                self.draw.ellipse((px-10, py-10, px+10, py+10), outline=self.fg_color)

        # Eyes and Mouth on the "main" part (depends on level)
        eye_y = cy - 8 if level == 1 else cy - 24 if level == 2 else cy - 25 if level == 3 else cy - 30
        eye_x_off = 5 if level == 1 else 4
        
        if pet_data.get('is_sleeping'):
            # Sleeping eyes (closed)
            self.draw.line((cx-eye_x_off-3, eye_y, cx-eye_x_off+3, eye_y), fill=self.fg_color, width=1)
            self.draw.line((cx+eye_x_off-3, eye_y, cx+eye_x_off+3, eye_y), fill=self.fg_color, width=1)
            # Small "o" mouth
            self.draw.ellipse((cx-2, eye_y+4, cx+2, eye_y+8), outline=self.fg_color)
            return

        # Eyes
        if status == "Needs Sun":
            self.draw.ellipse((cx-eye_x_off-2, eye_y-2, cx-eye_x_off+2, eye_y+2), fill=self.fg_color)
            self.draw.ellipse((cx+eye_x_off-2, eye_y-2, cx+eye_x_off+2, eye_y+2), fill=self.fg_color)
        elif status == "Tired":
            self.draw.line((cx-eye_x_off-3, eye_y, cx-eye_x_off+3, eye_y), fill=self.fg_color, width=1)
            self.draw.line((cx+eye_x_off-3, eye_y, cx+eye_x_off+3, eye_y), fill=self.fg_color, width=1)
        else:
            self.draw.ellipse((cx-eye_x_off-2, eye_y-2, cx-eye_x_off+2, eye_y+2), fill=self.fg_color)
            self.draw.ellipse((cx+eye_x_off-2, eye_y-2, cx+eye_x_off+2, eye_y+2), fill=self.fg_color)
            
        # Mouth
        if status in ["Healthy", "Needs Sun"]:
            self.draw.arc((cx-5, eye_y+2, cx+5, eye_y+8), 0, 180, fill=self.fg_color)
        elif status == "Stressed":
            self.draw.line((cx-5, eye_y+5, cx+5, eye_y+5), fill=self.fg_color, width=1)
        else:
            self.draw.arc((cx-5, eye_y+5, cx+5, eye_y+10), 180, 0, fill=self.fg_color)

    def draw_loading_frame(self, progress):
        """Draws a frame of the loading animation. progress is 0.0 to 1.0."""
        # Clear image
        self.image = Image.new('1', (self.width, self.height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        
        # Calculate position - hop across the screen
        x = int(progress * (self.width + 60)) - 30
        
        # Hopping effect (sine wave for y)
        import math
        # 4 hops across the screen
        hop_height = 20
        y_offset = abs(math.sin(progress * math.pi * 4)) * hop_height
        y = self.height // 2 + 10 - int(y_offset)
        
        self.draw_pet({"level": 1, "status": "Healthy"}, x, y)
        
        # Optional loading text
        self.draw.text((self.width // 2 - 30, self.height - 20), "Loading...", fill=self.fg_color)

    def draw_stats(self, pet_data):
        """Draws health bars and status text."""
        margin = 130
        y_start = 2 # Moved up slightly more
        
        # Name & XP
        self.draw.text((margin, y_start), f"Name: {pet_data['name']}", fill=self.fg_color)
        self.draw.text((margin + 80, y_start), f"Lv: {pet_data.get('level', 1)}", fill=self.fg_color)
        
        # Stats bars
        self.draw_bar(margin, y_start + 12, "Hap", pet_data['happiness'])
        self.draw_bar(margin, y_start + 24, "Enr", pet_data['energy'])
        self.draw_bar(margin, y_start + 36, "Str", pet_data['stress'])
        self.draw_bar(margin, y_start + 48, "Sun", pet_data['sunshine'])
        self.draw_bar(margin, y_start + 60, "Wat", pet_data.get('hydration', 50))
        self.draw_bar(margin, y_start + 72, "Soc", pet_data.get('social', 50))
        
        # Status text
        self.draw.text((margin, y_start + 85), f"Status: {pet_data['status']}", fill=self.fg_color)

        # Walk Time & Streak
        walk_text = f"Walk: {int(pet_data.get('walk_time_today', 0))}m"
        if pet_data.get('is_walking'):
            walk_text += " [ACT]"
        self.draw.text((margin, y_start + 96), walk_text, fill=self.fg_color)
        
        streak_text = f"Streak: {pet_data.get('streak', 0)}d Grat: {pet_data.get('gratitude_count', 0)}"
        self.draw.text((margin, y_start + 107), streak_text, fill=self.fg_color)
        
        # Decorative icons
        if pet_data['sunshine'] > 70:
            self.draw_sun(20, 20)
        elif pet_data.get('hydration', 50) > 80:
            self.draw_rain(20, 20)
        
        # Affirmation
        if not pet_data.get('is_sleeping'):
            affirmations = [
                "You are doing great!",
                "Keep growing!",
                "Take a deep breath.",
                "You are enough.",
                "Today is a new day."
            ]
            import random
            # Use seed based on day to keep it consistent for the day if possible, 
            # but here we'll just pick one.
            aff = affirmations[int(time.time() / 3600) % len(affirmations)]
            self.draw.text((5, self.height - 12), aff, fill=self.fg_color)

    def draw_rain(self, x, y):
        """Draws a small cloud with rain."""
        self.draw.ellipse((x-10, y-5, x+10, y+5), outline=self.fg_color, fill=self.bg_color)
        self.draw.ellipse((x-5, y-8, x+5, y), outline=self.fg_color, fill=self.bg_color)
        for i in range(3):
            rx = x - 6 + i*6
            self.draw.line((rx, y+6, rx-2, y+10), fill=self.fg_color)

    def draw_breathing_frame(self, progress, text="Breathe In"):
        """progress 0.0 to 1.0 (one full breath cycle)"""
        import math
        self.image = Image.new('1', (self.width, self.height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        
        # Breathing scale effect
        # 0 -> 0.5 (In), 0.5 -> 1.0 (Out)
        if progress < 0.5:
            scale = 0.8 + (progress * 2) * 0.4 # 0.8 to 1.2
            current_text = "Breathe In..."
        else:
            scale = 1.2 - ((progress - 0.5) * 2) * 0.4 # 1.2 to 0.8
            current_text = "Breathe Out..."
            
        # Draw pet centered and scaled
        cx, cy = self.width // 2, self.height // 2
        # Simple scaling by moving y or just drawing a bigger one? 
        # Let's just adjust y for a "lifting" effect
        y_off = int((scale - 1.0) * 20)
        self.draw_pet({"level": 3, "status": "Healthy"}, cx, cy - y_off)
        
        # Text
        self.draw.text((cx - 40, 10), current_text, fill=self.fg_color)
        self.draw.rectangle((20, self.height - 15, self.width - 20, self.height - 5), outline=self.fg_color)
        self.draw.rectangle((20, self.height - 15, 20 + int(progress * (self.width - 40)), self.height - 5), fill=self.fg_color)

    def draw_sun(self, x, y):
        """Draws a small sun icon."""
        r = 10
        self.draw.ellipse((x-r, y-r, x+r, y+r), outline=self.fg_color)
        for i in range(8):
            import math
            angle = i * (math.pi / 4)
            x1 = x + math.cos(angle) * (r + 2)
            y1 = y + math.sin(angle) * (r + 2)
            x2 = x + math.cos(angle) * (r + 6)
            y2 = y + math.sin(angle) * (r + 6)
            self.draw.line((x1, y1, x2, y2), fill=self.fg_color, width=1)

    def draw_bar(self, x, y, label, value):
        bar_width = 80
        bar_height = 10
        self.draw.text((x, y-2), label, fill=self.fg_color)
        # Bar outline
        self.draw.rectangle((x + 30, y, x + 30 + bar_width, y + bar_height), outline=self.fg_color)
        # Bar fill
        fill_width = int((value / 100) * bar_width)
        self.draw.rectangle((x + 30, y, x + 30 + fill_width, y + bar_height), fill=self.fg_color)

    def draw_menu(self, options, selected_index, title="MENU"):
        """Draws a simple menu overlay."""
        # Draw a box for the menu
        menu_w, menu_h = 100, 95
        mx, my = (self.width - menu_w) // 2, (self.height - menu_h) // 2
        self.draw.rectangle((mx, my, mx + menu_w, my + menu_h), fill=self.bg_color, outline=self.fg_color)
        
        self.draw.text((mx + 10, my + 5), title, fill=self.fg_color)
        self.draw.line((mx + 5, my + 18, mx + menu_w - 5, my + 18), fill=self.fg_color)
        
        # Limit visible options if needed, but here 3-5 should fit
        for i, option in enumerate(options):
            prefix = "> " if i == selected_index else "  "
            self.draw.text((mx + 10, my + 25 + (i * 12)), f"{prefix}{option}", fill=self.fg_color)

    def get_image(self):
        return self.image

    def save_preview(self, filename="preview.png"):
        self.image.save(filename)
