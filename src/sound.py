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

    async def on_score(self):
        """
            Makes sound when a player makes a point
        """
        self.sound.play_sound(2)
        await asyncio.sleep(5)
        self.sound.stop_sound(2)

    async def on_end(self):
        """
            Sound when the game ends.  
        """
        pass