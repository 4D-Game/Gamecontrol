#!/usr/bin/env python3

"""
Created: 10.08.21
by: Lukas Schüttler

Entrypoint to control the Gamecontrol
"""

import logging

from game_sdk.game_io import GameState
from game_sdk.gamecontrol import Game


class CrazyComet(Game):
    async def on_score(self):
        scores = self.players.score

        for seat, score in scores.items():
            if score >= 10:
                logging.info("Player %s wins !!!", score)
                await self.set_game_state(GameState.END)


if __name__ == "__main__":
    game = CrazyComet()
    game.run("/home/pi/Gamecontrol/config.toml")
