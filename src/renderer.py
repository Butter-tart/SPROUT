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
        """Draws an ASCII-style character based on level and status at position (x, y)."""
        level = pet_data.get('level', 1)
        status = pet_data.get('status', 'Healthy')
        is_sleeping = pet_data.get('is_sleeping', False)
        
        # ASCII character sets for different stages
        # Stage 1: Simple Sprout
        #   ,vv,
        #  ( oo )
        #   \__/
        
        # Stage 2: Bud
        #    ()
        #  --/--
        #  |oo |
        #  \___/

        # Stage 3: Flower
        #   wWw
        #  (o o)
        #  --|--
        #  |___|
        
        # Build ASCII lines
        ascii_lines = []
        
        # Eyes/Mouth Logic
        if is_sleeping:
            eyes = "- -"
            mouth = "o"
        elif status == "Tired":
            eyes = "x x"
            mouth = "-"
        elif status == "Stressed":
            eyes = "o o"
            mouth = "~"
        elif status == "Needs Sun":
            eyes = "O O"
            mouth = "u"
        else: # Healthy
            eyes = "^ ^"
            mouth = "v"

        if level == 1:
            ascii_lines = [
                "  ,vv,  ",
                f" ( {eyes} ) ",
                f"  \\_{mouth}_/  "
            ]
        elif level == 2:
            ascii_lines = [
                "    ()    ",
                "  --/--   ",
                f" | {eyes} |  ",
                f" \\__{mouth}__/  "
            ]
        elif level == 3:
            ascii_lines = [
                "   wWw    ",
                f"  ({eyes})   ",
                " --/|\\--  ",
                f" | {mouth} |   ",
                " \\___/   "
            ]
        else: # level 4+
            ascii_lines = [
                " _\\(_)/_  ",
                "  >@ @<   ",
                f" ({eyes})  ",
                f" --{mouth}--  ",
                "  /   \\   "
            ]

        # Render ASCII lines
        line_height = 12
        for i, line in enumerate(ascii_lines):
            self.draw.text((x - 20, y - 30 + i * line_height), line, fill=self.fg_color)

    def draw_static_loading(self):
        """Draws a static loading screen."""
        self.image = Image.new('1', (self.width, self.height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        
        # Center position
        cx, cy = self.width // 2, self.height // 2
        
        # Draw a happy sprout in the center
        self.draw_pet({"level": 1, "status": "Healthy"}, cx, cy + 10)
        
        # Loading text
        self.draw.text((self.width // 2 - 30, self.height - 25), "Loading...", fill=self.fg_color)

    def draw_stats(self, pet_data):
        """Draws health bars and status text."""
        margin = 135
        y_start = 5
        
        # Name & XP - More compact
        self.draw.text((margin, y_start), f"{pet_data['name']} (Lv {pet_data.get('level', 1)})", fill=self.fg_color)
        
        # Stats bars - only 4 essential ones
        # Selecting: Happiness, Energy, Hydration, Stress
        self.draw_bar(margin, y_start + 15, "Hap", pet_data['happiness'])
        self.draw_bar(margin, y_start + 28, "Enr", pet_data['energy'])
        self.draw_bar(margin, y_start + 41, "Wat", pet_data.get('hydration', 50))
        self.draw_bar(margin, y_start + 54, "Str", pet_data['stress'])
        
        # Status text
        self.draw.text((margin, y_start + 70), f"Status: {pet_data['status']}", fill=self.fg_color)

        # Walk Time & Streak - Combined for space
        walk_val = int(pet_data.get('walk_time_today', 0))
        streak_val = pet_data.get('streak', 0)
        self.draw.text((margin, y_start + 82), f"Walk: {walk_val}m | {streak_val}d", fill=self.fg_color)
        
        # Gratitude
        self.draw.text((margin, y_start + 94), f"Gratitude: {pet_data.get('gratitude_count', 0)}", fill=self.fg_color)
        
        # Decorative icons
        # Move icons to top-left area
        if pet_data['sunshine'] > 70:
            self.draw_sun(15, 15)
        elif pet_data.get('hydration', 50) > 80:
            self.draw_rain(15, 15)
        
        # Affirmation - Moved up slightly from the very bottom
        if not pet_data.get('is_sleeping'):
            affirmations = [
                "You are doing great!",
                "Keep growing!",
                "Take a deep breath.",
                "You are enough.",
                "Today is a new day.",
                "Be kind to yourself.",
                "Small steps matter."
            ]
            import random
            # Use a seed based on day for a daily affirmation
            current_day = int(time.time() / 86400)
            # Re-seed with local time day to ensure it changes properly
            local_day = time.localtime().tm_yday
            random.seed(local_day)
            aff = random.choice(affirmations)
            self.draw.text((10, self.height - 15), aff, fill=self.fg_color)
            # Reset seed to avoid affecting other random calls if any
            random.seed()

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
        """Draws an improved menu overlay with scrolling."""
        menu_w, menu_h = 120, 100
        mx, my = (self.width - menu_w) // 2, (self.height - menu_h) // 2
        
        # Rounded-like rectangle (simple version)
        self.draw.rectangle((mx, my, mx + menu_w, my + menu_h), fill=self.bg_color, outline=self.fg_color)
        self.draw.rectangle((mx+1, my+1, mx + menu_w - 1, my + menu_h - 1), fill=self.bg_color, outline=self.fg_color)
        
        # Title
        self.draw.text((mx + (menu_w - len(title)*6)//2, my + 5), title, fill=self.fg_color)
        self.draw.line((mx + 5, my + 18, mx + menu_w - 5, my + 18), fill=self.fg_color)
        
        # Visible range for scrolling
        max_visible = 6
        start_index = max(0, min(selected_index - max_visible // 2, len(options) - max_visible))
        
        for i in range(min(max_visible, len(options))):
            idx = start_index + i
            if idx >= len(options): break
            
            option = options[idx]
            is_selected = (idx == selected_index)
            
            y_pos = my + 22 + (i * 12)
            if is_selected:
                # Highlight selection
                self.draw.rectangle((mx + 5, y_pos - 1, mx + menu_w - 5, y_pos + 11), fill=self.fg_color)
                self.draw.text((mx + 10, y_pos), option, fill=self.bg_color)
            else:
                self.draw.text((mx + 10, y_pos), option, fill=self.fg_color)

        # Scroll indicators
        if start_index > 0:
            self.draw.text((mx + menu_w - 12, my + 22), "^", fill=self.fg_color)
        if start_index + max_visible < len(options):
            self.draw.text((mx + menu_w - 12, my + menu_h - 15), "v", fill=self.fg_color)

    def get_image(self):
        return self.image

    def save_preview(self, filename="preview.png"):
        self.image.save(filename)
