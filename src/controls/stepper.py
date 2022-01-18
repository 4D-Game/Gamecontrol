#!/usr/bin/env python3

"""
Created: 12/08/21
by: Sonja Lukas
Tower control with 2 stepper
Motorkit version
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
                max_interval: max. waiting time rotate stepper 2
                min_interval: min. waiting time rotate stepper 2
    """
    start_position=10
    max_angle=float(10)
    min_angle=float(-10)
    max_interval=0.04
    min_interval=0.01
    max_rock_interval=0.05
    min_rock_interval=0.03
    total_score=0
    score_goal=20      #todo::::: call sdk definition

    def __init__(self):
        """
            Use encoder device: instantiation of the 2 steppers and encoder for rocking stepper
            Use step counter: instantiation of the 2 steppers, use step_count for rocking stepper
        """
        self.stepper1 = EncoderStepperHAL("myStepper1",1)
        self.stepper2 = StepperHAL("myStepper2",2)
        self.stepper1.encoder.enc_imp=0

    async def set_start_position(self):
        """
            Set start position at initialisation and after each game round.
            current version: use variable step_count
        """
        await self.stepper1.set_position(self.start_position) 

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
            mapping attributes to rotate()

            Attributes:
                stepper1: rocking stepper with random start direction
                stepper2: rotate stepper
        """
        stepper1_start_dir=random.randint(1, 2)
        if stepper1_start_dir==1:
            self.stepper1.direction=STEPPER.FORWARD
        else:
            self.stepper1.direction=STEPPER.BACKWARD

        asyncio.create_task(self.stepper1.rock())   #Problem: works much faster than algo calls
        asyncio.create_task(self.stepper2.rotate())
    
        while True:
            self.stepper1.interval, self.stepper1.direction = await self.stepper1_algo()
            self.stepper2.interval, self.stepper2.direction = await self.stepper2_algo()

    async def stepper1_algo(self):
        """
            Algorithm of the rocking stepper 1
            The rocking speed is determined via random factor, generated with random.uniform.

            Attributes
                max_angle: limit forward rocking value, definition in class stepperHAL
                max_angle: limit backward rocking value, definition in class stepperHAL
        """
        interval=random.uniform(self.min_rock_interval,self.max_rock_interval)
        #logging.debug(f"stepper1_algo with random interval: {interval}")

        old_direction:Literal=self.stepper1.direction
        angle= self.stepper1.step_count*self.stepper1.encoder.motor_step_angle
        logging.debug(f"stepper1_algo calc angle over steps: {angle} direction {old_direction} random interval {interval}")

        #angle = self.stepper1.encoder.angle_calc()
        #logging.debug(f"stepper1_algo get angle {angle}")
        if angle >= self.max_angle:
            if old_direction==STEPPER.FORWARD:
                new_dire=STEPPER.BACKWARD
                logging.info(f"direction changes to BACKWARD, Trigger: algo max_angle")
                return interval, new_dire                
            else:
                logging.debug(f"Trigger: max_angle")
                return interval, old_direction 
        elif angle <= self.min_angle:
            if old_direction==STEPPER.BACKWARD:
                new_dire=STEPPER.FORWARD
                logging.info(f"stepper direction changes to FORWARD, Trigger: algo min_angle")
                return interval, new_dire
            else:
                logging.debug(f"Trigger: min_angle")
                return interval, old_direction
        else:
            logging.debug(f"Trigger: 3rd path stepper1_algo")
            return interval, old_direction

    async def score_map(self, x, in_min, in_max, out_min, out_max):
        """
        Maps the score range 0 to maximum to the interval range min to max

        """
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

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
        logging.info(f"function call stepper2_algo, score: {current_score} mapping to interval {interval}")
        return interval, direction

    async def score_map(self, x, in_min, in_max, out_min, out_max):
        """
        maps the percentage range -100 to -1 or 1 to 100  to interval range 0.01 to 0.05

        """
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def on_exit(self):
        """
            threading stop, motor_release via atexit register
        """
        self.set_start_position()
        self.stepper1.close()    #todo:::::::::::: check hal.close
        self.stepper2.close()

Tower1=TowerControl()
async def main():
    #try: 
        #await asyncio.wait_for(Tower1.set_start_position(), timeout=2) #test set_start_position
        #await asyncio.sleep(2)
    await asyncio.gather(Tower1.game_run())
    #except KeyboardInterrupt:
        #Tower1.on_exit()    

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)    
    asyncio.run(main())