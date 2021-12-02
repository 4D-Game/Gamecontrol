#!/usr/bin/env python3

"""
Created: 11/22/21
by: Sonja Lukas
Tower control with 2 stepper
Game part
"""

#from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
from ..hardware.stepperHAL import StepperHAL

import time
import atexit 
import logging
import threading
import mqtt
import asyncio

class Stepper(StepperHAL): #Control
    """
        Gamecontroll Stepper
    """
    def __init__(self,stepper_name, port_number, rpm:int):
        super(). __init__(self, stepper_name, port_number, rpm) 

    async def set_speed(self):
        pass

    async def set_start_position(self):
        """
            set start position after each game round 
        """
        await asyncio.run(self.set_position())

    async def get_score(self):
        """
            Control depending on the score 
            Attribute: 
        """

        # await self.motor_stop() # todo: change in on_end at game_sdk
        pass
             
    async def on_exit(self):
        """
            threading stop, motor_release via atexit register 
        """
        await self.close()    #todo: check hal.close

       


