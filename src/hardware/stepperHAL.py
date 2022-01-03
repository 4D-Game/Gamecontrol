#!/usr/bin/env python3

"""
Created: 12/08/21
by: Sonja Lukas
Tower control with 2 stepper
Hardware part 
version MotorKit
"""
import time
import atexit
import asyncio
import board
import logging
import RPi.GPIO as EncPin

from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit

logging.basicConfig(level=logging.INFO)

class StepperHAL():
    #step_style=STEPPER.DOUBLE
    def __init__(self, stepper_name, port_number, stop_at_exit=True): 
        """
            with '_station' create an MotorKit Object
            'turn_off_motor' required for auto-disabling motors on shutdown
        """
        self.enc=Encoder()
       
        self._station=MotorKit(i2c=board.I2C())    #composition attribute
        if stop_at_exit:
            atexit.register(self.turn_off_motor)   #self.stop 
        self.name=stepper_name                     #gets myStepper1 and myStepper2
        self.port_number=port_number               #only 1 or 2!
    
        if port_number==1:
            self.motor=self._station.stepper1 
        elif port_number==2:
            self.motor=self._station.stepper2

        self.sleepy=0.05  #naming open #without self test open #default=0.05
        self.direction=STEPPER.FORWARD #default=FORWARD
        self.step_style=STEPPER.DOUBLE #default=DOUBLE   

    async def get_position(self):
        """
            returns current stepper position - for point system or game start       
        """
        #todo Encoder()
        angle_pos=await self.enc.angle_calc()
        position = 50                  #only for current test!!!!!!!!!!!!!!!!!!!!!!!!!
        logging.info(f"current position is {position} and angle {angle_pos}")
        return int(position), int(angle_pos)

    async def set_position(self, pos_goal) -> int:
        """
            set stepper position for game start
            Arguments:  pos_goal
                        rpm
        """ 
        pos_current=await self.get_position()
        
        logging.info(f"Port {self.name} current position {pos_current}")

        steps:int=pos_current-pos_goal      #calc step size    
        if steps>0:
            logging.info(f"steps to go {steps}")
            for step in range(steps):
                self.motor.onestep(direction=STEPPER.BACKWARD, style=self.step_style)
                await asyncio.sleep(0.05)
        elif steps<0:
            for step in range(abs(steps)):
                self.motor.onestep(direction=STEPPER.FORWARD, style=self.step_style)
                await asyncio.sleep(0.05)
        
        pos_current = await self.get_position()
        logging.info(f"{self.name} check current position {pos_current} is equal to {pos_goal}?")
        return pos_current  

    async def rotate(self):    
        """
            thread control
        """    
        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            await asyncio.sleep(self.sleepy)
            #logging.info(f"rotate: {self.name} direction: {self.direction} with sleeptime {self.sleepy}") 
    
    async def motor_stop(self):
        """
            single motor hold for play algorithm
        """
        self.motor.release()
        #Distinction should not be necessary, test open, hedging? 
        
        # if self.name=='myStepper1':
        #     self.motor.release()
        #     print(f"Motor {self.name} stop")
        #     logging.info(f"Motor {self.name} stop")
        # elif self.name=='myStepper2':
        #     self.motor.release()
        #     print(f"Motor {self.name} stop")
        #     logging.info(f"Motor {self.name} stop") 
        # else:
        #     logging.info(f"Motor {self.name} does not stop") 
          
    def turn_off_motor(self):
        """
            Auto-disabling motors on shutdown   
        """
        self.motor.release()
        logging.info(f"Check on hardware: both ports release")
        
    async def close(self):
        """
           call in superordinate structure
        """
        await self.motor_stop()
        EncPin.cleanup() 
        self.enc.remove_event_detect() 
        logging.info(f"stepperHAL close function: {self.name} close")


class Encoder():
    """
        Checking the rocking steppermotor myStepper1
    """
    def __init__(self, callback=None):
        self.motor_steps_per_rev=200 #not yet verified 
        self.motor_step_angle=1.8
        self.imp=0                   #for simulation only
        self.state='00'                 
        self.old_state='00'
        self.enc_imp=0
        EncPin.setmode(EncPin.BCM)
        self.Pin_A=24  #TX Enc
        self.Pin_B=25  #RX Enc
        EncPin.setup(self.Pin_A, EncPin.IN)
        EncPin.setup(self.Pin_B, EncPin.IN)
        self.callback=callback
         
        EncPin.add_event_detect(self.Pin_A, EncPin.BOTH, callback=self.enc_impulses)
        EncPin.add_event_detect(self.Pin_B, EncPin.BOTH, callback=self.enc_impulses)        

    async def set_imp_zero(self):
        """
            Function to set pulse counter to 0,
            required at game_start
        """
        old_imp_val=self.imp
        self.imp=0         #not yet practical 
        logging.info(f"Encoder.set_imp_zero values: old {old_imp_val} new {self.imp}")
       
    # async def impulses(self): #for test only, without hardware
    #     if self.state==0:
    #         self.imp=self.imp+1
    #         #logging.info(f"Encoder.impulses: value {self.imp}")
    #         await asyncio.sleep(0.5)
    #         if self.imp==5:
    #             self.state=1
    #     elif self.state==1:           
    #         self.imp=self.imp-1
    #         #logging.info(f"Encoder.impulses: value {self.imp}")
    #         await asyncio.sleep(0.5)
    #         if self.imp==-5:
    #             self.state=0
    #     else:
    #         logging.info(f"Error in impuls simulation")

        #return self.imp #for test only

    async def enc_impulses(self, channel):
        logging.info(f"I am in function enc_impulses") #test
        self.enc_imp=await self.enc_imp+1 #first test only 

        self.current_A=await EncPin.input(self.Pin_A)
        self.current_B=await EncPin.input(self.Pin_B)
        self.state=await "{}{}".format(self.current_A, self.current_B)

        # if self.state == "11":  #Forward    #only rising edge version
        #     self.enc_imp=await self.enc_imp+1
        #     logging.info(f"Encoder.impulses: value {self.enc_imp}")

        # elif self.state == "10": #Backward
        #     self.enc_imp=await self.enc_imp-1 
        #     logging.info(f"Encoder.impulses: value {self.enc_imp}")

        if self.old_state=='00':
            if self.state=='01':
                self.enc_imp=self.enc_imp #turn right #no inc
            elif self.state=='10':
                self.enc_imp=await self.enc_imp-1 #turn left #ok
                if self.callback is not None:
                    self.callback(self.enc_imp) 

        elif self.old_state=='01':
            if self.state=='11':
                self.enc_imp=await self.enc_imp+1 #turn right #ok
                if self.callback is not None:
                    self.callback(self.enc_imp)                   
            elif self.state=='00':
                self.enc_imp= self.enc_imp #turn left #no dec 

        elif self.old_state=='10': #can be removed
            if self.state=='00':
                self.enc_imp= self.enc_imp #turn right #no inc
            elif self.state=='11':
                self.enc_imp= self.enc_imp #turn left  #no dec  

        elif self.old_state=='11': #can be removed  
            if self.state=='10':
                self.enc_imp=self.enc_imp #turn right #no inc
            elif self.state=='01':
                self.enc_imp=self.enc_imp #turn left #no dec

        self.old_state=self.state    
        await asyncio.sleep(0.001) 
      
    async def get_enc_imp(self):
        return self.enc_imp        

    async def angle_calc(self):
        await self.get_enc_imp()
        total_angle= self.enc_imp * self.motor_step_angle
        return total_angle #calculation not verified  #input has to be +-angle!!!!

    async def remove_event_detect(self):
        EncPin.remove_event_detect(self.Pin_A, self.Pin_B) 
