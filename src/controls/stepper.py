#!/usr/bin/env python3

"""
Created: 21/01/22
by: Sonja Lukas
Tower control with 2 stepper
Library for motor shield: adafruit_motorkit
"""
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
                start_position: set rocking stepper1 in middle position 
                max_angle: limit rocking forward stepper1
                min_angle: limit rocking backward stepper1
                max_-& min interval: max und min waiting time rotate stepper 2
                max_- & min_rock_interval: max und min waiting time rock stepper1
    """
    start_position=0
    max_interval=0.02
    min_interval=0.005
    max_rock_interval=0.03
    min_rock_interval=0.01
    total_score=0
    score_goal=20        #todo::::: call sdk definition

    def __init__(self):
        """
            Use encoder device: instantiation of the 2 steppers and encoder for rocking stepper
            Use step counter: instantiation of the 2 steppers, use step_count for rocking stepper
        """
        self.stepper1 = EncoderStepperHAL("myStepper1",1)
        self.stepper2 = StepperHAL("myStepper2",2)
        #self.stepper1.encoder.enc_imp=0                 #placed for encoder

    async def set_start_position(self):
        """
            Set start position at initialisation and after each game round.
            Current version: used stopper to determine middle_position
        """
        #self.stepper1.set_position(self.start_position)  #without stopper; used init value start_position
        await self.stepper1.detect_middle_position()      #with stopper

    async def get_score(self):
        """
            Control depending on the score
        """
        #in main: function call!
        #scores=score.values(score)
        #total_score=sum(scores)

        #for use score sim only
        if self.total_score<self.score_goal:
            self.total_score=self.total_score+1
            await asyncio.sleep(3)
        else:
            self.total_score=0
        return self.total_score

    async def game_run(self):
        """
            Mapping attributes to rotate() and rock()

            Attributes:
                stepper1: rocking stepper with random start direction
                stepper2: rotate stepper
        """
        stepper1_start_dir=random.randint(1, 2)
        if stepper1_start_dir==1:
            self.stepper1.direction=STEPPER.FORWARD
        else:
            self.stepper1.direction=STEPPER.BACKWARD

        asyncio.create_task(self.stepper1.rock())        #stepper1
        asyncio.create_task(self.stepper2.rotate())      #stepper2
    
        while True:
            self.stepper1.interval, self.stepper1.direction = await self.stepper1_algo()
            self.stepper2.interval, self.stepper2.direction = await self.stepper2_algo()

    async def stepper1_algo(self):
        """
            Algorithm of the rocking stepper 1
            The rocking speed is determined via random factor, generated with random.uniform.
            The max. & min. angles for the direction change also have a random factor.
        """
        interval=random.uniform(self.min_rock_interval,self.max_rock_interval)
        old_direction:Literal=self.stepper1.direction
        angle=self.stepper1.step_count*self.stepper1.motor_step_angle

        algo1_max_angle=float(random.uniform(self.stepper1.max_angle-5, self.stepper1.max_angle))
        algo1_min_angle=float(random.uniform(self.stepper1.min_angle, self.stepper1.min_angle+5))
        logging.info(f"stepper1_algo: angle {angle} random max_angle {algo1_max_angle} min_angle {algo1_min_angle} direction {old_direction} random interval {interval}")
        await asyncio.sleep(self.stepper1.interval)
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
                logging.info(f"direction changes to FORWARD, Trigger: algo1 min_angle")
                return interval, new_dire
            else:
                return interval, old_direction
        else:
            logging.info(f"Trigger: 3rd path stepper1_algo")
            return interval, old_direction

    async def stepper2_algo(self):
        """
            Algorithm of the rotate stepper 2

            Attributes:
                The rotation interval depends on the total score of the players.
                A change of direction is possible, but currently not included in the game definition.
        """
        direction:Literal=self.stepper2.direction
        current_score=await self.get_score()

        interval=await self.score_map(current_score, 0, self.score_goal, self.max_interval, self.min_interval)
        logging.info(f"stepper2_algo, score: {current_score} mapping to interval {interval}")
        return interval, direction

    async def score_map(self, x, in_min, in_max, out_min, out_max):
        """
        Maps the score range zero to goal_score to interval range min_interval to max_interval
        """
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def on_exit(self):
        """
            Reset position
            Threading stop, motor_release via atexit register
        """
        self.set_start_position() #use stopper 
        self.stepper1.close()     #todo:::::::::::: check hal.close
        self.stepper2.close()

Tower1=TowerControl()

async def main():
    #try: 
        #await asyncio.wait_for(Tower1.set_start_position(), timeout=50) #test set_start_position
        #await asyncio.sleep(2)
    await asyncio.gather(Tower1.game_run())
    #except KeyboardInterrupt:
        #Tower1.on_exit()    

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)    
    asyncio.run(main())