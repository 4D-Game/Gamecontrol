#!/usr/bin/env python3

"""
Created: 12/08/21
by: Sonja Lukas
Tower control with 2 stepper
Motorkit version
"""
from asyncio.tasks import current_task
from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit
from hardware.stepperHAL import StepperHAL, Encoder

import time
import atexit 
import logging
import asyncio
import board

class TowerControl(): #Control
    """
        Gamecontroll Stepper
    """

    def __init__(self):
        """
            instantiation of the 2 steppers
            instantiation case structure with a dictionary for game_run() conditions
        """
        self.stepper1 = StepperHAL("myStepper1",1)  #Conversion open, for test still different 
        self.stepper2 = StepperHAL("myStepper2",2)
        #super(). __init__(stepper_name, port_number)
        #self.case=Cases()
        self.encoder=Encoder()
        self.total_score=0

    async def set_start_position(self):
        """
            set start position after each game round 
        """
        await self.set_position(100) #definition open

    async def get_score(self, score):
        """
            Control depending on the score 
            Attribute: 
        """
        #in main: function call!
        #scores=score.values(score)
        #total_score=sum(scores)
        # on end:
        # await self.motor_stop() # todo: change in on_end at game_sdk 

        #for sim only:
        if self.total_score<score:
            total_score=self.total_score+1                      
            return total_score

    async def game_run(self):
        """
            game starts in game sdk
            mapping attributes to rotate()
        """    
        asyncio.create_task(self.stepper2.rotate()) 
        asyncio.create_task(self.stepper1.rotate())

        while True:
            self.stepper1.sleepy, self.stepper1.direction = await self.stepper1_algo()
            self.stepper2.sleepy, self.stepper2.direction = await self.stepper2_algo()
            await asyncio.sleep(0.1)

    async def stepper1_algo(self):
        sleepy=0.03
        old_direction=self.stepper1.direction
        logging.info(f"I am in stepper1_algo")
        await asyncio.sleep(0.01)
    	
        angle = await self.encoder.angle_calc()
        angle_max = 7
        angle_min = -7
        logging.info(f"stepper angle {angle}")

        if angle >= angle_max:
            new_dire=STEPPER.BACKWARD
            logging.info(f"direction changes")
            return sleepy, new_dire

        elif angle <= angle_min:
            new_dire=STEPPER.FORWARD
            
            return sleepy, new_dire
        else:
            return sleepy, old_direction    

    async def stepper2_algo(self):
        score_goal=20
        direction=STEPPER.FORWARD
        current_score=await self.get_score(score_goal)
        if current_score < score_goal:
            sleepy=0.01       
        elif current_score >=score_goal:
            sleepy=0.005   
        new_dire=STEPPER.FORWARD
        return sleepy, direction         
                  

    async def on_exit(self):
        """
            threading stop, motor_release via atexit register 
        """
        await self.set_start_position() 
        self.close()    #todo: check hal.close

Tower1=TowerControl()

async def main():
    await asyncio.gather(Tower1.game_run())

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    asyncio.run(main())