import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341
from game_sdk.passive.game import Game

class Display(Game):
    """
        Class to manage displaydata
    """

    def on_init(self):
        """
            Configures pins and spi for connection of the display
        """
        # Configuration for CS and DC pins (these are PiTFT defaults):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)

        # Config for display baudrate (default max is 24mhz):
        baudrate = 24000000

        # Setup SPI bus using hardware SPI:
        spi = board.SPI()

        self.disp = ili9341.ILI9341(
            spi,
            rotation = 90,  #2.2", 2.4", 2.8", 3.2" ILI9341
            cs = cs_pin,
            dc = dc_pin,
            rst = reset_pin,
            baudrate = baudrate,
        )

        if self.disp.rotation % 180 == 90:
            self.height = self.disp.width  #we swap height/width to rotate it to landscape!
            self.width = self.disp.height
        else:
            self.width = self.disp.width  
            self.height = self.disp.height

        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(image)

    async def on_score(self):
        scores_dict = self.players.score

        score_A = 0
        score_B = 0

        for key, value in scores_dict.items():
            if key in self.config['team_A']
                score_A += value
            elif key in self.config['team_B']:
                score_B += value

        if score_A or score_B >= 10:
            if score_A > score_B:
                logging.info("Team A wins!!!")
            else:
                logging.info("Team B wins!!!")
            await self.set_game_state(GameState.END)

        #Load a TTF font. .ttf font file should be same directory as the python script
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)

        #Draw a blue filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 155, 250))

        text1 = "Team A: " 
        text2 = "Team B: " 

        y = 50
        x = 30
        self.draw.text((x, y),text1, font=font, fill= "#FFFFFF")
        x += font.getsize(text1)[0]
        self.draw.text((x, y), str(score_A), font=font, fill= (255, 0, 0))  
        y += 40+font.getsize(text1)[1]
        x = 30
        self.draw.text((x, y), text2, font=font, fill="#FFFFFF")
        x += font.getsize(text2)[0]
        self.draw.text((x, y), str(score_B), font=font, fill= (255, 0, 0))  

        # Display image.
        self.disp.image(image)

    async def on_pregame(self):
        """
            Display until game starts (ready)
        """
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 155, 250))
        self.disp.image(image)
        image = Image.open("logo.png")

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

        # Display image.
        self.disp.image(image)

    async def on_start(self):
        pass
        
    async def on_end(self):
        pass
    