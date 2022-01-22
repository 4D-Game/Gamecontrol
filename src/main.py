#!/usr/bin/env python3

"""
Created: 10.08.21
by: Lukas Schüttler

Entrypoint to control the Gamecontrol
"""

import logging

from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory

from game_sdk.game_io import GameState
from game_sdk.gamecontrol import Game


class CrazyComet(Game):
    async def on_score(self):
        scores = self.players.score

        for seat, score in scores.items():
            if score >= 10:
                logging.info("Player %s wins !!!", score)
                await self.set_game_state(GameState.END)

    async def on_exit(self, err: Exception = None):
        return await super().on_exit(err=err)
        #controls.on_exit()


if __name__ == "__main__":
    Device.pin_factory = PiGPIOFactory()

    game = CrazyComet()
    game.run("/home/pi/Gamecontrol/config.toml")
