from PIL import Image, ImageDraw, ImageFont
import os

class Renderer:
    def __init__(self, width=250, height=122):
        self.width = width
        self.height = height
        # E-ink typically uses 1-bit color (black and white)
        self.image = Image.new('1', (self.width, self.height), 255)  # 255 is white
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
            self.draw.ellipse((cx-r, cy, cx+r, cy+r*2), outline=0, fill=255) # Pot/Base
            self.draw.line((cx, cy, cx, cy-15), fill=0, width=2) # Stem
            self.draw.ellipse((cx-8, cy-18, cx, cy-12), outline=0) # Leaf 1
            self.draw.ellipse((cx, cy-18, cx+8, cy-12), outline=0) # Leaf 2
        
        elif level == 2:
            # Stage 2: Bud
            r = 20
            self.draw.ellipse((cx-r, cy+5, cx+r, cy+r*2+5), outline=0, fill=255) # Pot
            self.draw.line((cx, cy+5, cx, cy-20), fill=0, width=2) # Stem
            # Leaves
            self.draw.ellipse((cx-12, cy-10, cx, cy-5), outline=0)
            self.draw.ellipse((cx, cy-10, cx+12, cy-5), outline=0)
            # Bud
            self.draw.ellipse((cx-8, cy-28, cx+8, cy-20), outline=0, fill=255)
            
        elif level == 3:
            # Stage 3: Small Flower
            r = 25
            self.draw.ellipse((cx-r, cy+10, cx+r, cy+r*2+10), outline=0, fill=255) # Pot
            self.draw.line((cx, cy+10, cx, cy-25), fill=0, width=3) # Stem
            # Flower petals
            pr = 10
            self.draw.ellipse((cx-pr, cy-35, cx+pr, cy-15), outline=0) # Center
            for i in range(4):
                import math
                angle = i * (math.pi / 2)
                px = cx + math.cos(angle) * 12
                py = cy - 25 + math.sin(angle) * 12
                self.draw.ellipse((px-8, py-8, px+8, py+8), outline=0)

        else:
            # Stage 4: Big Flower
            r = 30
            self.draw.ellipse((cx-r, cy+15, cx+r, cy+r*2+15), outline=0, fill=255) # Pot
            self.draw.line((cx, cy+15, cx, cy-30), fill=0, width=4) # Stem
            # Large Flower
            cr = 12
            self.draw.ellipse((cx-cr, cy-42, cx+cr, cy-18), outline=0, fill=255) # Center
            for i in range(6):
                import math
                angle = i * (math.pi / 3)
                px = cx + math.cos(angle) * 20
                py = cy - 30 + math.sin(angle) * 20
                self.draw.ellipse((px-10, py-10, px+10, py+10), outline=0)

        # Eyes and Mouth on the "main" part (depends on level)
        eye_y = cy - 8 if level == 1 else cy - 24 if level == 2 else cy - 25 if level == 3 else cy - 30
        eye_x_off = 5 if level == 1 else 4
        
        # Eyes
        if status == "Needs Sun":
            self.draw.ellipse((cx-eye_x_off-2, eye_y-2, cx-eye_x_off+2, eye_y+2), fill=0)
            self.draw.ellipse((cx+eye_x_off-2, eye_y-2, cx+eye_x_off+2, eye_y+2), fill=0)
        elif status == "Tired":
            self.draw.line((cx-eye_x_off-3, eye_y, cx-eye_x_off+3, eye_y), fill=0, width=1)
            self.draw.line((cx+eye_x_off-3, eye_y, cx+eye_x_off+3, eye_y), fill=0, width=1)
        else:
            self.draw.ellipse((cx-eye_x_off-2, eye_y-2, cx-eye_x_off+2, eye_y+2), fill=0)
            self.draw.ellipse((cx+eye_x_off-2, eye_y-2, cx+eye_x_off+2, eye_y+2), fill=0)
            
        # Mouth
        if status in ["Healthy", "Needs Sun"]:
            self.draw.arc((cx-5, eye_y+2, cx+5, eye_y+8), 0, 180, fill=0)
        elif status == "Stressed":
            self.draw.line((cx-5, eye_y+5, cx+5, eye_y+5), fill=0, width=1)
        else:
            self.draw.arc((cx-5, eye_y+5, cx+5, eye_y+10), 180, 0, fill=0)

    def draw_loading_frame(self, progress):
        """Draws a frame of the loading animation. progress is 0.0 to 1.0."""
        # Clear image
        self.image = Image.new('1', (self.width, self.height), 255)
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
        self.draw.text((self.width // 2 - 30, self.height - 20), "Loading...", fill=0)

    def draw_stats(self, pet_data):
        """Draws health bars and status text."""
        margin = 130
        y_start = 5 # Moved up to fit more
        
        # Name
        self.draw.text((margin, y_start), f"Name: {pet_data['name']}", fill=0)
        self.draw.text((margin + 80, y_start), f"Lv: {pet_data.get('level', 1)}", fill=0)
        
        # Stats bars
        self.draw_bar(margin, y_start + 18, "Hap", pet_data['happiness'])
        self.draw_bar(margin, y_start + 34, "Enr", pet_data['energy'])
        self.draw_bar(margin, y_start + 50, "Str", pet_data['stress'])
        self.draw_bar(margin, y_start + 66, "Sun", pet_data['sunshine'])
        
        # Status text
        self.draw.text((margin, y_start + 85), f"Status: {pet_data['status']}", fill=0)

        # Walk Time
        walk_text = f"Walk: {int(pet_data.get('walk_time_today', 0))}m"
        if pet_data.get('is_walking'):
            walk_text += " [ACTIVE]"
        self.draw.text((margin, y_start + 101), walk_text, fill=0)
        
        # Decorative Sun if sunshine is high
        if pet_data['sunshine'] > 70:
            self.draw_sun(20, 20)

    def draw_sun(self, x, y):
        """Draws a small sun icon."""
        r = 10
        self.draw.ellipse((x-r, y-r, x+r, y+r), outline=0)
        for i in range(8):
            import math
            angle = i * (math.pi / 4)
            x1 = x + math.cos(angle) * (r + 2)
            y1 = y + math.sin(angle) * (r + 2)
            x2 = x + math.cos(angle) * (r + 6)
            y2 = y + math.sin(angle) * (r + 6)
            self.draw.line((x1, y1, x2, y2), fill=0, width=1)

    def draw_bar(self, x, y, label, value):
        bar_width = 80
        bar_height = 10
        self.draw.text((x, y-2), label, fill=0)
        # Bar outline
        self.draw.rectangle((x + 30, y, x + 30 + bar_width, y + bar_height), outline=0)
        # Bar fill
        fill_width = int((value / 100) * bar_width)
        self.draw.rectangle((x + 30, y, x + 30 + fill_width, y + bar_height), fill=0)

    def draw_menu(self, options, selected_index):
        """Draws a simple menu overlay."""
        # Draw a white box for the menu
        menu_w, menu_h = 100, 80
        mx, my = (self.width - menu_w) // 2, (self.height - menu_h) // 2
        self.draw.rectangle((mx, my, mx + menu_w, my + menu_h), fill=255, outline=0)
        
        self.draw.text((mx + 10, my + 5), "MENU", fill=0)
        self.draw.line((mx + 5, my + 18, mx + menu_w - 5, my + 18), fill=0)
        
        for i, option in enumerate(options):
            prefix = "> " if i == selected_index else "  "
            self.draw.text((mx + 10, my + 25 + (i * 15)), f"{prefix}{option}", fill=0)

    def get_image(self):
        return self.image

    def save_preview(self, filename="preview.png"):
        self.image.save(filename)
