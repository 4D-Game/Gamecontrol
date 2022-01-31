import logging
import asyncio
import random

from typing import Literal
from adafruit_motor import stepper as STEPPER
from hardware.stepper_hal import EncoderStepperHAL, StepperHAL

class TowerControl():
    """
        Gamecontroll Stepper

        Attributes:
            start_position: set Rocking Stepper in center position
            max_interval: max stepping time for Rotate Stepper
            min_interval: min stepping time for Rotate Stepper
            max_rock_interval: max stepping time for Rock Stepper
            min_rock_interval: min stepping time for Rock Stepper
    """

    start_position:int = 0
    max_interval:float = 0.02
    min_interval:float = 0.005
    max_rock_interval:float = 0.03
    min_rock_interval:float = 0.01

    _total_score:int = 0
    _score_goal:int = 20

    _algo_task = None
    _rock_task = None
    _rotate_task = None

    def __init__(self):
        """
            Initialize Rock and Rotate Stepper
        """

        self.rock_stepper = EncoderStepperHAL("Rock Stepper",1)
        self.rotate_stepper = StepperHAL("Rotate Stepper",2)

    async def set_start_position(self):
        """
            Set start position at initialisation and after each game round.
            Current version: uses stopper to determine middle_position
        """

        #self.stepper1.set_position(self.start_position)  #without stopper; used init value start_position
        await self.rock_stepper.calibrate()               #with stopper

    def set_score(self, score, max_score):
        """
            Set total score and max score for the rotation algorithm
        """

        self._total_score = score
        self._score_goal = max_score
        self.rotate_stepper.interval, self.rotate_stepper.direction = self._rotate_algo()

    async def get_score(self):
        """
            !!! Deprecated !!!

            Control depending on the score
        """

        if self.total_score<self._score_goal:
            self.total_score=self.total_score+1
            await asyncio.sleep(3)
        else:
            self.total_score=0
        return self.total_score

    def game_run(self):
        """
            Mapping attributes to rotate() and rock()
        """

        stepper1_start_dir=random.randint(1, 2)
        if stepper1_start_dir==1:
            self.rock_stepper.direction=STEPPER.FORWARD
        else:
            self.rock_stepper.direction=STEPPER.BACKWARD

        self._rock_task = asyncio.create_task(self.rock_stepper.rock())        #stepper1
        self._rotate_task = asyncio.create_task(self.rotate_stepper.rotate())      #stepper2

        self._algo_task = asyncio.create_task(self._run(0.5))

    async def _run(self, T:float = 0.5):
        """
            Start game loop
        """

        while True:
            self.rock_stepper.interval, self.rock_stepper.direction = await self._rock_algo()
            #self.rotate_stepper.interval, self.rotate_stepper.direction = await self._rotate_algo()
            await asyncio.sleep(T)

    async def _rock_algo(self):
        """
            Algorithm of the rocking stepper
            The rocking speed is determined via random factor, generated with random.uniform.
            The max. & min. angles for the direction change also have a random factor.
        """

        interval=random.uniform(self.min_rock_interval,self.max_rock_interval)
        old_direction:Literal=self.rock_stepper.direction
        angle=self.rock_stepper.step_count*self.rock_stepper.motor_step_angle

        algo1_max_angle=float(random.uniform(self.rock_stepper.max_angle-5, self.rock_stepper.max_angle))
        algo1_min_angle=float(random.uniform(self.rock_stepper.min_angle, self.rock_stepper.min_angle+5))
        logging.info(f"rock_algo: angle {angle} random max_angle {algo1_max_angle} min_angle {algo1_min_angle} direction {old_direction} random interval {interval}")
        await asyncio.sleep(self.rock_stepper.interval)
        #angle = self.stepper1.encoder.angle_calc()          #currently not used
        #logging.debug(f"stepper1_algo get angle {angle}")
        if angle >= algo1_max_angle:
            if old_direction==STEPPER.FORWARD:
                new_dire=STEPPER.BACKWARD
                logging.info(f"direction changes to BACKWARD, Trigger: algo1 max_angle")
                return interval, new_dire
            else:
                return interval, old_direction
        elif angle <= algo1_min_angle:
            if old_direction==STEPPER.BACKWARD:
                new_dire=STEPPER.FORWARD
                logging.info(f"direction changes to FORWARD, Trigger: rock min_angle")
                return interval, new_dire
            else:
                return interval, old_direction
        else:
            logging.info(f"Trigger: 3rd path rock_algo")
            return interval, old_direction

    def _rotate_algo(self):
        """
            Algorithm of the rotate stepper

            The rotation interval depends on the total score of the players.
            A change of direction is possible, but currently not included in the game definition.
        """
        direction:Literal=self.rotate_stepper.direction
        current_score=self._total_score

        interval=self._score_map(current_score, 0, self._score_goal, self.max_interval, self.min_interval)
        logging.info(f"rotate_algo, score: {current_score} mapping to interval {interval}")
        return interval, direction

    def _score_map(self, x, in_min, in_max, out_min, out_max):
        """
        Maps the score range zero to goal_score to interval range min_interval to max_interval
        """
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def game_stop(self):
        if self._algo_task:
            self._algo_task.cancel()
            self._algo_task = None

        if self._rock_task:
            self._rock_task.cancel()
            self._rock_task = None

        if self._rotate_task:
            self._rotate_task.cancel()
            self._rotate_task = None

        await self.set_start_position() #use stopper


    async def on_exit(self):
        """
            Reset position
            Threading stop, motor_release via atexit register
        """

        await self.game_stop()

        self.rock_stepper.close()     #todo:::::::::::: check hal.close
        self.rotate_stepper.close()


async def main():
    Tower1=TowerControl()
    #try:
        #await asyncio.wait_for(Tower1.set_start_position(), timeout=50) #test set_start_position
        #await asyncio.sleep(2)
    await asyncio.gather(Tower1.game_run())
    #except KeyboardInterrupt:
        #Tower1.on_exit()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    asyncio.run(main())