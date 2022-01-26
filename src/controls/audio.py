
from hardware.sound_hal import SOUND
from pygame.mixer import Sound

class AudioControl:
  """
    Control wich plays audio on specific events

    Attributes
      start: Sound played at the start of a game
      end: Sound played at the end of a game
      hit: Sound played when a player hits the comet
  """

  start: Sound
  end: Sound
  hit: Sound

  def __init__(self):
      """
        Create differen sound objects
      """

      self.start = SOUND.create_sound("home/pi/Gamecontrol/src/assets/start.wav")
      self.end = SOUND.create_sound("home/pi/Gamecontrol/src/assets/end.wav")
      self.hit = SOUND.create_sound("home/pi/Gamecontrol/src/assets/score.wav")

  def start(self):
    SOUND.play_sound(self.start)

  def end(self):
    SOUND.play_sound(self.end)

  def hit(self):
    SOUND.play_sound(self.hit)
