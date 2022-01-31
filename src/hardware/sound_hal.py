import logging
from pygame import mixer
from hardware.hal import HAL

class SoundHAL(HAL):
    """
        Hardware abstraction layer class for the sounds
    """

    def __init__(self):
        """
            Configures the mixer to play and load needed sounds
        """
        mixer.init()
        self.start_sound = mixer.Sound("home/pi/Gamecontrol/src/assets/start.wav")
        self.end_sound = mixer.Sound("home/pi/Gamecontrol/src/assets/end.wav")
        self.hit_sound = mixer.Sound("home/pi/Gamecontrol/src/assets/score.wav")

    def start(self):
        """
            Play sound durring the game
        """

        self.start_sound.set_volume(10)
        self.start_sound.play(-1)

    def end(self):
        """
            Stop start sound and play sound for the end of the game
        """

        self.start_sound.stop()
        self.end_sound.set_volume(10)
        self.end_sound.play()

    def hit(self):
        """
            Play sound for score
        """

        self.hit_sound.set_volume(10)
        self.hit_sound.play()

    def close():
        pass