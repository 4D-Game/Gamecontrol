from gamecontrol_sdk import Game
from gamecontrol_sdk.game import LogLevel

if __name__ == '__main__':
    game = Game()
    game.run(log_level=LogLevel.DEBUG)
