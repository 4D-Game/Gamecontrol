import logging
from pygame import mixer
from hardware.hal import HAL

class SoundHAL(HAL):
    """
        Hardware abstraction layer class for the sounds (Do not instanciate this class. Use `SOUND` instead)
    """

    def __init__(self):
        """
            Configures the mixer to play and load needed sounds
        """
        mixer.init()

    def create_sound(self, path: str) -> mixer.Sound:
        """
            Create sound object from file at given path

            Arguments:
                path: Path to audiofile
        """

        return mixer.Sound(path)

    def play_sound(self, sound: mixer.Sound):
        """
            Plays sound depending on event

            Arguments:
                sound: Sound object
        """

        sound.set_volume(10)
        sound.play()

    def stop_sound(self, sound: mixer.Sound):
        """
            Stops sound depending on the event

            Arguments:
                sound: Sound object
        """

        sound.stop()

SOUND = SoundHAL()
"""
    Singleton of the sound interface
"""