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

class Stepper(StepperHAL): 
    """
        Gamecontroll Stepper
    """
    def __init__(self):
        super(). __init__(self, port_name, port_number:int, rpm:int, addr=0x60)    
    def set_speed(self): 
        pass
    def get_points(): #???
        pass     
    def close():
        #aufruf der close hal
        pass 

       


