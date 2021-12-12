import logging 
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341
from hardware.hal import HAL

class DisplayHAL(HAL):

    def __init__(self):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)
        baud = 24000000
        rot = 90
        spi = board.SPI()

        self.disp = ili9341.ILI9341(
            spi,
            rotation = rot,  #2.2", 2.4", 2.8", 3.2" ILI9341
            cs = cs_pin,
            dc = dc_pin,
            rst = reset_pin,
            baudrate = baud,
        )

        self.show_circle()
        
    def show_circle(self):
        if self.disp.rotation % 180 == 90:
            height = self.disp.width  #we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width  
            height = self.disp.height

        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 155, 250))
        draw.ellipse((80,50,230,200), fill = (0, 155, 250), outline ='white', width=10)
        self.disp.image(image)

    def show_score(self, score_A: int, score_B: int):
        if self.disp.rotation % 180 == 90:
            height = self.disp.width  #we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width  
            height = self.disp.height
            
        #Load a TTF font. .ttf font file should be same directory as the python script
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
        
        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        #Draw a blue filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 155, 250))

        text1 = "Team A: " 
        text2 = "Team B: " 

        y = 50
        x = 30
        draw.text((x, y),text1, font=font, fill= "#FFFFFF")
        x += font.getsize(text1)[0]
        draw.text((x, y), str(score_A), font=font, fill= (255, 0, 0))  
        y += 40+font.getsize(text1)[1]
        x = 30
        draw.text((x, y), text2, font=font, fill="#FFFFFF")
        x += font.getsize(text2)[0]
        draw.text((x, y), str(score_B), font=font, fill= (255, 0, 0))  

        # Display image.
        self.disp.image(image)

    def end_display(self, points: int, name: str):
        #Make sure to create image with mode 'RGB' for full color.
        if self.disp.rotation % 180 == 90:
            height = self.disp.width  #we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width  
            height = self.disp.scaled_height
            
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        image = Image.open("win.jpg")
        text1 = name
        point = str(points)

        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))
        image_editable = ImageDraw.Draw(image)

        y1= 80
        x1 = 30
        image_editable.text((x1, y1),text1, font=font, fill= "Red")
        x1 += font.getsize(text1)[0]
        image_editable.text((x1, y1), point, font=font, fill= "Red")  
        self.disp.image(image)
    
    def close(self):
        if self.disp.rotation % 180 == 90:
            height = self.disp.width  #we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width  
            height = self.disp.height


        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

        #draw.ellipse((20, 180, 180, 20), outline ='white', fill=(0, 250, 0))
        self.disp.image(image)