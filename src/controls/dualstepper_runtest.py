#!/usr/bin/env python3

"""
Created: 12/08/21
by: Sonja Lukas
TEST_Code: both stepper run only in one direction
    scores only simulated
    set_position value only hard coded 
"""
from asyncio.tasks import current_task
from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit

import time
import atexit 
import logging
import asyncio
import RPi.GPIO as GPIO

from adafruit_motorkit import MotorKit

class StepperHAL():
    def __init__(self, stepper_name, port_number, stop_at_exit=True): 
        """
            Stepper hardware application layer 

            Arguments:
                stepper_name: stepper naming 
                port_number: Motor HAT ports 1,2
                stop_at_exit: in case of crash or manual end Motor stop

            Attributes: 
                _station: create an MotorKit Object
                atexit.register: required for auto-disabling motors on shutdown
                motor: map stepper
                direction: stepper direction with default FORWARD
                step_style: step type with default DOUBLE
                interval: waiting time
                angle_max: limit rocking forward stepper1 
                angle_min: limit rocking backward stepper1
                interval_max: max. waiting time rotate stepper 2
                interval_min: min. waiting time rotate stepper 2
        """      
        self._station=MotorKit(i2c=board.I2C())    
        if stop_at_exit:
            atexit.register(self.turn_off_motor)  
        self.name=stepper_name                     
        self.port_number=port_number                  
        if port_number==1:
            self.motor=self._station.stepper1 
        elif port_number==2:
            self.motor=self._station.stepper2       
        self.direction=STEPPER.FORWARD 
        self.step_style=STEPPER.DOUBLE   
        self.interval=0.05
        if port_number==1:
            self.angle_max=20
            self.angle_min=-20
        if port_number==2:
            self.interval_max=0.05
            self.interval_min=0.01

    async def get_position(self):
        """
            returns current stepper position as angle - for point system or game start       
        """
        angle_pos=await Encoder.angle_calc()
        logging.info(f"current angle: {angle_pos}")
        pos_current=int(angle_pos/1.8)
        return int(pos_current)

    async def set_position(self, pos_goal) -> int:
        """
            Reading the current angle position
            Set stepper to goal angle for game start or on game
            Calculatio step size

            Arguments: 
                pos_goal: target position to be moved to         
        """ 
        pos_current=await self.get_position()
        logging.info(f"Port {self.name} current position {pos_current}")

        steps:int=pos_current-pos_goal     
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
            await asyncio.sleep(self.interval)
            #logging.info(f"rotate: {self.name} direction: {self.direction} with sleeptime {self.interval}") 
    
    async def motor_stop(self):
        """
            single motor hold for play algorithm
        """
        self.motor.release()
        logging.info(f"Check on hardware: motor stop {self.name}")
          
    def turn_off_motor(self):
        """
            Auto-disabling motors on shutdown   
        """
        self.motor.release()
        logging.info(f"Check on hardware: port release {self.name}")
        
    async def close(self):
        """
           call in superordinate structure
        """
        await self.motor_stop()
        logging.info(f"stepperHAL close: {self.name}")
        await Encoder.remove_event_detect() 
        logging.info(f"Encoder GPIO clear")

class Encoder():
    """
        Class to proof the rocking steppermotor myStepper1
        Connection asyncio and GPIO thread

        Attributes:
            pin_A: Encoder channel A connected to GPIO pin 25, Tx
            pin_B: Encoder channel B connectet to GPIO pin 24, Rx
            Event: BOTH rising and falling edges 
    """
    def __init__(self, loop=None, callback=None, direction=None):
        self.motor_step_angle=1.8
        # self.imp=0                   #for simulation only
        # self.state_test=0                 #for simulation only
        self.state='00'                 
        self.old_state='00'
        self.enc_imp=0
        self.direction=direction
        self.callback=callback
        self.loop=loop 

        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        self.Pin_A=25 #I #A=25
        self.Pin_B=24  
        GPIO.setup(self.Pin_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.Pin_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.loop=asyncio.get_event_loop()     
        GPIO.add_event_detect(self.Pin_A, GPIO.BOTH, callback=self.enc_impulses)
        GPIO.add_event_detect(self.Pin_B, GPIO.BOTH, callback=self.enc_impulses) 

    @asyncio.coroutine
    def gpio_event_on_loop_thread(self):
        """
            Stop the created loop after detection: async coroutine function call
        """
        #asyncio.sleep(0.001)
        logging.info('Stopping Event Loop')
        asyncio.get_event_loop().stop()    

    async def set_imp_zero(self):
        """
            Function to set pulse counter to 0,
            required at game_start
        """
        old_imp_val=self.enc_imp
        self.enc_imp=0         
        logging.info(f"Encoder.set_imp_zero: old {old_imp_val} new {self.enc_imp}")
       
    # async def impulses(self):  #for test only, without hardware
    #     if self.state_test==0:
    #         self.imp=self.imp+1
    #         logging.info(f"test_impulses: value {self.imp}")
    #         await asyncio.sleep(0.5)
    #         if self.imp==5:
    #             self.state_test=1
    #     elif self.state_test==1:           
    #         self.imp=self.imp-1
    #         logging.info(f"test_impulses: value {self.imp}")
    #         await asyncio.sleep(0.5)
    #         if self.imp==-5:
    #             self.state_test=0
    #     else:
    #         logging.info(f"Error in impuls simulation")
    #     return self.imp #for test only

    def enc_impulses(self, channel):
        """
            Event is called when edge is detected on channel 
                Arguments: 
                    channel: self.pinA
        """
        self.current_A= GPIO.input(self.Pin_A)
        self.current_B= GPIO.input(self.Pin_B)
        self.state="{}{}".format(self.current_A, self.current_B)

        if self.old_state=='00':
            if self.state=='01':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction ->")
                self.direction='Right'
            elif self.state=='10':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction <-")
                self.direction='Left' 

        elif self.old_state=='01':
            if self.state=='11':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction ->")
                self.direction='Right'                  
            elif self.state=='00':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction <-")
                self.direction='Left' 
                self.enc_imp= self.enc_imp-1 
                if self.callback is not None:
                   self.callback(self.enc_imp, self.direction)

        elif self.old_state=='10': 
            if self.state=='00':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction ->")
                self.direction='Right'
                self.enc_imp= self.enc_imp+1 
                if self.callback is not None:
                   self.callback(self.enc_imp, self.direction)
            elif self.state=='11':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction <-")
                self.direction='Left' 

        elif self.old_state=='11': 
            if self.state=='10':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction ->")
                self.direction='Right' 
            elif self.state=='01':
                logging.info(f"old_state {self.old_state}, new_state {self.state}, direction <-")
                self.direction='Left' 

        self.old_state=self.state                 
        self.loop.call_soon_threadsafe(self.gpio_event_on_loop_thread) 

    async def get_enc_imp(self):
        """
            Return of the current encoder pulse counter 
        """
        return self.enc_imp        

    async def angle_calc(self):
        """
            Stepper angle calculation
        """
        await self.get_enc_imp()
        total_angle= self.enc_imp * self.motor_step_angle
        return total_angle 

    async def remove_event_detect(self):
        """
            Clear the GPIO at the end
        """
        GPIO.cleanup() 


class TowerControl(): #Control
    """
        Gamecontroll Stepper
    """

    def __init__(self):
        """
            instantiation of the 2 steppers
            instantiation case structure with a dictionary for game_run() conditions
        """
        self.stepper1 = StepperHAL("myStepper1",1) 
        self.stepper2 = StepperHAL("myStepper2",2)
        self.encoder=Encoder()
        self.total_score=0

    async def set_start_position(self):
        """
            set start position after each game round 
        """
        await self.set_position(100) 

    async def get_score(self, score):
        """
            Control depending on the score 
        """
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
            self.stepper1.interval, self.stepper1.direction = await self.stepper1_algo()
            self.stepper2.interval, self.stepper2.direction = await self.stepper2_algo()
            await asyncio.sleep(300)

    async def stepper1_algo(self):
        logging.info(f"call runonly stepper1_algo")
        direction=STEPPER.FORWARD
        sleepy=0.01   
        return sleepy, direction           

    async def stepper2_algo(self):
        logging.info(f"call runonly stepper1_algo")
        direction=STEPPER.FORWARD
        sleepy=0.01   
        return sleepy, direction                     

    async def on_exit(self):
        """
            threading stop, motor_release via atexit register 
        """
        await self.set_start_position() 
        self.close()

Tower1=TowerControl()

async def main():
    await asyncio.gather(Tower1.game_run())

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    asyncio.run(main())