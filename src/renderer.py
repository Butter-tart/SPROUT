from PIL import Image, ImageDraw, ImageFont
import os

class Renderer:
    def __init__(self, width=250, height=122):
        self.width = width
        self.height = height
        # E-ink typically uses 1-bit color (black and white)
        self.image = Image.new('1', (self.width, self.height), 255)  # 255 is white
        self.draw = ImageDraw.Draw(self.image)
        
    def draw_pet(self, pet_status, x=60, y=60):
        """Draws a simple character based on status at position (x, y)."""
        # Simple procedural character
        cx, cy = x, y
        r = 30
        
        # Body
        self.draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=0, fill=255)
        
        # Eyes
        eye_r = 3
        if pet_status == "Needs Sun":
            # Looking up for sun
            self.draw.ellipse((cx-12, cy-12, cx-8, cy-8), fill=0)
            self.draw.ellipse((cx+8, cy-12, cx+12, cy-8), fill=0)
        elif pet_status == "Tired":
            # Closed eyes
            self.draw.line((cx-15, cy-5, cx-5, cy-5), fill=0, width=2)
            self.draw.line((cx+5, cy-5, cx+15, cy-5), fill=0, width=2)
        elif pet_status == "Sad":
            # Downward eyes
            self.draw.ellipse((cx-12, cy-8, cx-8, cy-4), fill=0)
            self.draw.ellipse((cx+8, cy-8, cx+12, cy-4), fill=0)
        else:
            self.draw.ellipse((cx-12, cy-10, cx-8, cy-6), fill=0)
            self.draw.ellipse((cx+8, cy-10, cx+12, cy-6), fill=0)
            
        # Mouth
        if pet_status in ["Healthy", "Needs Sun"]:
            self.draw.arc((cx-10, cy, cx+10, cy+15), 0, 180, fill=0)
        elif pet_status == "Stressed":
            self.draw.line((cx-10, cy+10, cx+10, cy+10), fill=0, width=2)
        else:
            self.draw.arc((cx-10, cy+5, cx+10, cy+20), 180, 0, fill=0)

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
        
        self.draw_pet("Healthy", x, y)
        
        # Optional loading text
        self.draw.text((self.width // 2 - 30, self.height - 20), "Loading...", fill=0)

    def draw_stats(self, pet_data):
        """Draws health bars and status text."""
        margin = 130
        y_start = 5 # Moved up to fit more
        
        # Name
        self.draw.text((margin, y_start), f"Name: {pet_data['name']}", fill=0)
        
        # Stats bars
        self.draw_bar(margin, y_start + 18, "Hap", pet_data['happiness'])
        self.draw_bar(margin, y_start + 34, "Enr", pet_data['energy'])
        self.draw_bar(margin, y_start + 50, "Str", pet_data['stress'])
        self.draw_bar(margin, y_start + 66, "Sun", pet_data['sunshine'])
        
        # Status text
        self.draw.text((margin, y_start + 85), f"Status: {pet_data['status']}", fill=0)
        
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

    def get_image(self):
        return self.image

    def save_preview(self, filename="preview.png"):
        self.image.save(filename)
