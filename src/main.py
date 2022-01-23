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
from controls.tower import TowerControl


class CrazyComet(Game):
    max_score = 10

    async def on_init(self):
        self.tower = TowerControl()
        await self.tower.set_start_position()

    async def on_pregame(self):
        self.tower.set_score(0, self.max_score * 2)
        self.tower.game_run()

    async def on_score(self):
        scores = self.players.score
        score_A = 0
        score_B = 0

        for seat, score in scores.items():
            if seat in self.config['team_A']:
                score_A += score
            elif seat in self.config['team_B']:
                score_B += score

        self.tower.set_score(score_A + score_B, self.max_score * 2)

        if score_A >= self.max_score:
            logging.info("Team A wins !!!")
            await self.set_game_state(GameState.END)
        elif score_B >= self.max_score:
            logging.info("Team B wins !!!")
            await self.set_game_state(GameState.END)

    async def on_end(self):
        await self.tower.game_stop()

    async def on_exit(self, err: Exception = None):
        return await super().on_exit(err=err)


if __name__ == "__main__":
    Device.pin_factory = PiGPIOFactory()

    game = CrazyComet()
    game.run("/home/pi/Gamecontrol/config.toml")
