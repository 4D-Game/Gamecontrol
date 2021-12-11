#!/usr/bin/env python3

"""
Created: 12/08/21
by: Sonja Lukas
Tower control with 2 stepper
Motorkit version
"""
from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit
from ..hardware.stepperHAL import StepperHAL, Encoder

import time
import atexit 
import logging
import asyncio
#import board

class Stepper(StepperHAL): #Control
    """
        Gamecontroll Stepper
    """

    def __init__(self, stepper_name, port_number):
        """
            instantiation of the 2 steppers
            instantiation case structure with a dictionary for game_run() conditions
        """
        #self.stepper1 = StepperHAL("myStepper1",1) #Conversion open, for test still different 
        #self.stepper2 = StepperHAL("myStepper2",2)
        super(). __init__(stepper_name, port_number)
        self.case=Cases()

    async def set_start_position(self):
        """
            set start position after each game round 
        """
        await self.set_position(100) #definition open

    async def get_score(self):
        """
            Control depending on the score 
            Attribute: 
        """
        # on end:
        # await self.motor_stop() # todo: change in on_end at game_sdk
        pass

    async def set_values(self, new_sleepy, new_dir):
        """
            set variable 
        """
        #todo: create a function to value transfer 
        self.sleepy=new_sleepy
        self.direction=new_dir

    async def game_run(self):
        """
            game starts in game sdk
            mapping attributes to rotate()
        """    
        while True:
            print("test I am in game_run loop") #ok, ok
            await self.rotate() #ok, ok 
            await self.case.func_dict.get(self.case.func_dict.myStepper1, self.case.func_dict.handler_default)()

            # if self.name=='myStepper2': #not ok!!!! 
            #     self.new_dir=STEPPER.FORWARD                  #No change of direction at Step2            
            #     self.new_sleepy=0.04
            #     await self.set_values(self.new_sleepy, self.new_dir)

            # if self.name=='myStepper1':
            #     start=time.time()
            #     duration = await time.time()-start
            #     print(f"{duration}")
            #     if duration>2:
            #         self.new_sleepy=0.05
            #         if self.new_dir==STEPPER.FORWARD:
            #             self.new_dir=STEPPER.BACKWARD
            #         else:
            #             self.new_dir=STEPPER.FORWARD       
            #         await self.set_values(self.new_sleepy, self.new_dir)
            #         duration=0                

        #logging.info(f"set_start_position Duration: {duration}")         

    async def on_exit(self):
        """
            threading stop, motor_release via atexit register 
        """
        await self.set_start_position() 
        self.close()    #todo: check hal.close


class Cases():
    def __init__(self):   
        self.func_dict={
            'myStepper1': self.handle_St1,
            self.name=='myStepper2': self.handle_St2,
            'handle_default':self.handle_default,       
        }
        self.enc=Encoder()  
        self.angle=self.enc.angle_calc
    async def handle_St1(self):
        print(self.enc.angle_calc())

    async def handle_St2(self):
        pass
    async def handle_default(self):
        pass    






Step1 = Stepper("myStepper1",1) #for tests 
Step2 = Stepper("myStepper2",2)

async def main():
    await asyncio.gather((Step2.game_run()),(Step1.game_run()))

if __name__ == "__main__":
    asyncio.run(main())

    #testloop.close()   #check:                                            
    #set_start_position()
    #get_positon()
    #set_position()
    #motor_stop()