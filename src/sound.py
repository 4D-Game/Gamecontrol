import logging
import asyncio
from asyncio import sleep
from hardware.sound_hal import SoundHAL
from game_sdk.passive.game import Game

class Sound(Game):
    """
        Class to manage sounds
    """

    async def on_init(self):
        """
            Configures mixer and loads sound
        """
        self.sound = SoundHAL()
        logging.info("Sound initalized")

    async def on_pregame(self):
        """
            Sound till the game starts
        """
        self.sound.play_sound(2)

    async def on_start(self):
        """
            Stops current sound
        """
        self.sound.stop_sound(2)

    async def on_score(self):
        """
            Makes sound when a player makes a point
        """
        self.sound.play_sound(1)
        await asyncio.sleep(3)
        self.sound.stop_sound(1)

    async def on_end(self):
        """
            Sound when the game ends.  
        """
        self.sound.play_sound(3)
        await asyncio.sleep(10)
        self.sound.stop_sound(3)