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
        self.shoot_sound = mixer.Sound('test_1.mp3')
        self.score_sound = mixer.Sound('test_2.mp3')
    
    def play_sound(self, event: int):
        """
            Plays sound depending on event (score, shoot)
        """
        if event == 1:
            self.shoot_sound.set_volume(10)
            self.shoot_sound.play()
        elif event == 2:
            self.score_sound.set_volume(10)
            self.score_sound.play() 

    def stop_sound(self, event: int)
        """
            Stops sound depending on the event
        """
        if event == 1:
            self.shoot_sound.stop()
        elif event == 2:
            self.score_sound.stop() 