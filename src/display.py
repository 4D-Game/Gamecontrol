import digitalio
import board
import asyncio
from asyncio import sleep
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341
from game_sdk.passive.game import Game
from hardware.display_hal import DisplayHAL
import logging

class Display(Game):
    """
        Class to manage displaydata
    """

    async def on_init(self):
        """
            Configures pins and spi for connection of the display
        """
        self.display = DisplayHAL()
        logging.info("Display initalized")

    async def on_score(self):
        """
            Updates score on the display when a player makes a point
        """
        scores_dict = self.players.score
        score_A = 0
        score_B = 0

        for key, value in scores_dict.items():
            if key in self.config['team_A']:
                score_A += value
            elif key in self.config['team_B']:
                score_B += value

        self.display.show_score(score_A, score_B)
        logging.info("Score update")

    async def on_pregame(self):
        """
            Display shows logo until game starts (ready)
        """
        self.display.show_score(0, 0)
        logging.info("ECE Logo")

    async def on_end(self):
        """
            Display shows winner when game ends.
            After a period of time the display shwos the logo again.
        """

        self.display.end_display()
        await asyncio.sleep(1)
        self.display.show_circle()

    async def on_exit(self, err: Exception = None):
        """
            Cleans display when the game is finished.
        """

        self.display.close()

        await self.on_exit(err)

if __name__ == '__main__':
    disp = Display()
    disp.run("/home/pi/Gamecontrol/config.toml")

