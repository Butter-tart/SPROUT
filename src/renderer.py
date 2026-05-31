from PIL import Image, ImageDraw, ImageFont
import os

class Renderer:
    def __init__(self, width=250, height=122):
        self.width = width
        self.height = height
        # E-ink typically uses 1-bit color (black and white)
        self.image = Image.new('1', (self.width, self.height), 255)  # 255 is white
        self.draw = ImageDraw.Draw(self.image)
        
    def draw_pet(self, pet_status):
        """Draws a simple character based on status."""
        # Simple procedural character for Day 1
        cx, cy = 60, 60
        r = 30
        
        # Body
        self.draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=0, fill=255)
        
        # Eyes
        eye_r = 3
        if pet_status == "Tired":
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
        if pet_status == "Healthy":
            self.draw.arc((cx-10, cy, cx+10, cy+15), 0, 180, fill=0)
        elif pet_status == "Stressed":
            self.draw.line((cx-10, cy+10, cx+10, cy+10), fill=0, width=2)
        else:
            self.draw.arc((cx-10, cy+5, cx+10, cy+20), 180, 0, fill=0)

    def draw_stats(self, pet_data):
        """Draws health bars and status text."""
        margin = 130
        y_start = 20
        
        # Name
        self.draw.text((margin, y_start), f"Name: {pet_data['name']}", fill=0)
        
        # Stats bars
        self.draw_bar(margin, y_start + 20, "Hap", pet_data['happiness'])
        self.draw_bar(margin, y_start + 40, "Enr", pet_data['energy'])
        self.draw_bar(margin, y_start + 60, "Str", pet_data['stress'])
        
        # Status text
        self.draw.text((margin, y_start + 85), f"Status: {pet_data['status']}", fill=0)

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
