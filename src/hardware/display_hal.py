
import logging
import os
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341
from hardware.hal import HAL

class DisplayHAL(HAL):
    """
        Hardware abstraction layer class for RGB Display
    """


    _TEAM_A_NAME: str = "Team A: "
    _TEAM_B_NAME: str = "Team B: "
    _score_A: int = 0
    _score_B: int = 0

    _BACKGROUND_COLOR = (34, 36, 47)
    _TEXT_COLOR = (255, 255, 255)
    _PRIMARY_COLOR = (0, 155, 250)
    _TEAM_A_COLOR = (0, 155, 250)
    _TEAM_B_COLOR = (252, 126, 9)

    def __init__(self):
        """
            Initialization of the display, configure pins and settings
            for the spi connection
        """
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)
        baud = 24000000
        rot = 90
        spi = board.SPI()

        self.disp = ili9341.ILI9341(
            spi,
            rotation = rot,
            cs = cs_pin,
            dc = dc_pin,
            rst = reset_pin,
            baudrate = baud,
        )

        self.show_circle()

    def swap_height_width(self, end: bool = False):
        """
            Adjusts heigth and width to the display screen.
            Creates RGB images and drawing objects.

            Parameters:
                end: if display is in end mode
        """
        if self.disp.rotation % 180 == 90:
            height = self.disp.width
            width = self.disp.height
        else:
            width = self.disp.width
            height = self.disp.height

        if end == False:
            #create a new image with RGB mode (3x8-bit pixels, pixel range from 0-255).
            #size is a tuple, which contains width and height in pixels.
            image = Image.new("RGB", (width, height))

            #creates drawing object to draw on image
            draw = ImageDraw.Draw(image)

            return height, width, image, draw
        else:
            return height, width

    def show_circle(self):
        """
            Draws a white circle on the blue display screen.
        """
        height, width, image, draw = self.swap_height_width()

        #draw rectangle over the whole display and dye it blue
        #(x0, y0, x1, y1), color to use for outline, color to use for the fill
        draw.rectangle((0, 0, width, height), outline = 0, fill = self._PRIMARY_COLOR)

        #draw ellipse inside the bounding box: (x0, y0, x1, y1)
        #outline color of ellipse is white, width is line width in pixels
        draw.ellipse((80,50,230,200),  outline = 'white',  width=10)

        #shows generated image
        self.disp.image(image)

    def show_score(self, score_A: int, score_B: int):
        """
            Shows current score from diffrent Teams
        """

        self._score_A = 10 if score_A > 10 else score_A
        self._score_B = 10 if score_B > 10 else score_B

        height, width, image, draw = self.swap_height_width()

        #draw rectangle over the whole display and dye it blue
        #(x0, y0, x1, y1), color to use for outline, color to use for the fill
        draw.rectangle((0, 0, width, height), outline = 0, fill = self._BACKGROUND_COLOR)

        #Load a TTF font. .ttf font file should be same directory as the python script
        font = ImageFont.truetype("/home/pi/Gamecontrol/src/fonts/Roboto-Medium.ttf", 45)

        y = 50
        x = 30
        #draws string at a given position with set fill color for the text
        draw.text((x, y), self._TEAM_A_NAME, font = font, fill = self._TEXT_COLOR)

        #adds length of previous string to get new position for the next string
        x += font.getsize(self._TEAM_A_NAME)[0]
        draw.text((x, y), str(score_A), font = font, fill = self._TEAM_A_COLOR)

        #adds heigth of previous string to get new position for the next string
        y += 40 + font.getsize(self._TEAM_A_NAME)[1]
        x = 30
        draw.text((x, y), self._TEAM_B_NAME, font = font, fill = self._TEXT_COLOR)
        x += font.getsize(self._TEAM_B_NAME)[0]
        draw.text((x, y), str(score_B), font = font, fill = self._TEAM_B_COLOR)

        #shows generated image
        self.disp.image(image)

    def end_display(self):
        """
            Shows which Team wons with image and points
        """
        height, width = self.swap_height_width(True)

        points = self._score_A if self._score_A > self._score_B else self._score_B
        name = self._TEAM_A_NAME if self._score_A > self._score_B else self._TEAM_B_NAME

        if name is self._TEAM_A_NAME:
            image = Image.open("/home/pi/Gamecontrol/src/assets/team_a_win.jpg")
        else:
            image = Image.open("/home/pi/Gamecontrol/src/assets/team_b_win.jpg")

        #scale the image to the smaller screen dimension of the display
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        #crop and center the image
        x = scaled_width / 2 - width / 2
        y = scaled_height / 2 - height / 2
        image = image.crop((x, y, x + width, y + height))

        #shows generated image
        self.disp.image(image)

    def close(self):
        """
            Cleans display, shows black screen
        """
        height, width, image, draw = self.swap_height_width()

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline = 0, fill = (0, 0, 0))

        #shows generated image
        self.disp.image(image)