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
        self.shoot = mixer.Sound('/home/pi/sounds_effect/laser-shoot.wav')
        self.intro = mixer.Sound('/home/pi/sounds_effect/intro.wav')
        self.winner = mixer.Sound('/home/pi/sounds_effect/success-fanfare-trumpets.mp3')
    
    def play_sound(self, event: int):
        """
            Plays sound depending on event
        """
        if event == 1:
            self.shoot.set_volume(10)
            self.shoot.play()
        elif event == 2:
            self.intro.set_volume(10)
            self.intro.play(-1) 
        elif event == 3:
            self.winner.set_volume(10)
            self.winner.play()

    def stop_sound(self, event: int)
        """
            Stops sound depending on the event
        """
        if event == 1:
            self.shoot.stop()
        elif event == 2:
            self.intro.stop() 
        elif event == 3:
            self.winner.stop()