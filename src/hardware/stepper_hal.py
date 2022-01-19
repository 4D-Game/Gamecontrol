#!/usr/bin/env python3

"""
Created: 08/01/22
by: Sonja Lukas
Tower control with 2 stepper
version Motor HAT library: MotorKit
classes: StepperHAL, Encoder
"""

import asyncio
from pickle import TRUE
import board
import logging
import atexit

from typing import Literal
from gpiozero import Button, Device
from gpiozero.pins.pigpio import PiGPIOFactory

from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit
from hardware.hal import HAL

class StepperHAL(HAL):
    """
        Stepper hardware abstraction layer

        Attributes:
                motor: map stepper
                direction: stepper direction with default FORWARD
                step_style: step type with default DOUBLE
                interval: initial waiting time
                step_count: motor rock control without encoder 
                frequency: motor shield per default 1600 Hz
                motor_step_angle: with step_style DOUBLE step resolution
                max_angle: limit rocking forward stepper1
                min_angle: limit rocking backward stepper1
    """
    direction:Literal=STEPPER.FORWARD
    step_style=STEPPER.DOUBLE
    interval=0.03
    step_count=0
    motor_step_angle=0.45 
    max_angle=float(16)
    min_angle=float(-16)
    
    def __init__(self, stepper_name, port_number, stop_at_exit=True):
        """
            Arguments:
                stepper_name: stepper naming
                port_number: Motor HAT ports 1, 2
                forward_, backward_stopper: software rock protection with stopper instead of an encoder for stepper1
        """
        station=MotorKit(i2c=board.I2C())
        #station.frequency=1600               #default 1600Hz       
        self.name=stepper_name
        self.port_number=port_number
        if port_number==1:
            self.motor=station.stepper1
        elif port_number==2:
            self.motor=station.stepper2
        if stop_at_exit:
            atexit.register(self.motor_stop)  #currently still necessary as motor voltage is otherwise not released 
        
        if port_number ==1: #position has to change ....
            self.forward_stopper = Button(24, pull_up=True)   #GPIO 24, 25
            self.backward_stopper = Button(25, pull_up=True)
            self.forward_stopper.when_pressed = self.change_direction
            self.backward_stopper.when_pressed = self.change_direction

    async def rock(self): #rocking stepper1 - new part for test 
        """
            thread control rocking stepper1
        """
        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            
            if self.direction == STEPPER.FORWARD:       #stepper1 steps counter
                self.step_count = self.step_count+1
                logging.debug(f"{self.name} step_count {self.step_count}")
            else:
                self.step_count = self.step_count-1
                logging.debug(f"{self.name} step_count {self.step_count}")
            
            rock_angle=self.step_count*self.motor_step_angle 
            await self.change_direction(rock_angle)
            # if rock_angle>=self.max_angle:            #check angle limits
            #     await self.change_direction(rock_angle)
            # elif rock_angle<=self.min_angle:
            #     await self.change_direction(rock_angle)
            await asyncio.sleep(self.interval)
            logging.debug(f"rotate: {self.name} direction: {self.direction} with interval {self.interval}")

    async def change_direction(self, angle):
        """
            Direction change provided for rocking stepper1
            Trigger: min. & max defined angle
            Callback: stopper to prevent overwinding and to reset position 
        """
        old_direction:Literal=self.direction

        if self.forward_stopper.is_pressed:        #callback: stopper
            self.direction=STEPPER.BACKWARD
            logging.info(f"stopper FW pressed")
        elif self.backward_stopper.is_pressed:
            self.direction=STEPPER.FORWARD
            logging.info(f"stopper BW pressed")

        if angle >= self.max_angle:                 #trigger: angle
            if old_direction==STEPPER.FORWARD:      #security check
                self.direction=STEPPER.BACKWARD
                logging.info(f"direction changes to BW, Trigger: cd max_angle")
            else:
                logging.info(f"ERROR_change_direction, trigger max_angle")    
        elif angle <= self.min_angle:
            if old_direction==STEPPER.BACKWARD:
                self.direction=STEPPER.FORWARD
                logging.info(f"direction changes to FORWARD, Trigger: cd min_angle")
            else:
                logging.info(f"ERROR_change_direction, trigger min_angle")   

    async def rotate(self):
        """
            thread control rotating stepper2
        """
        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            # if self.port_number == 2:                   #currently not used in algo stepper2
            #     if self.direction == STEPPER.FORWARD:
            #         self.step_count = self.step_count+1
            #         logging.debug(f"{self.name} step_count {self.step_count}")
            #     else:
            #         self.step_count = self.step_count-1
            #         logging.debug(f"{self.name} step_count {self.step_count}")
            await asyncio.sleep(self.interval)
            logging.debug(f"rotate: {self.name} direction: {self.direction} with interval {self.interval}")

    def motor_stop(self):
        """
            single motor hold for play algorithm and after end of game
        """
        self.motor.release()
        logging.info(f"Check release on hardware: motor stop {self.name}")

    def close(self):
        """
           stop and release motor
        """
        self.motor_stop()
        logging.info(f"StepperHAL close: {self.name}")

class EncoderStepperHAL(StepperHAL):
    """
        Stepper hardware abstraction layer with Encoder

        Attributes:
                motor: map stepper
                encoder: encoder of the motor
                direction: stepper direction with default FORWARD
                step_style: step type with default DOUBLE
                interval: waiting time
                angle_max: limit rocking forward stepper1
                angle_min: limit rocking backward stepper1
                interval_max: max. waiting time rotate stepper 2
                interval_min: min. waiting time rotate stepper 2
    """

    def __init__(self, stepper_name, port_number):
        """
            Arguments:
                stepper_name: stepper naming
                port_number: Motor HAT ports 1,2
        """
        super().__init__(stepper_name, port_number)
        self.encoder = Encoder()

    async def get_position(self):    #without stopper 
        """
            Use encoder device: returns current stepper position - for point system or game start
            Use step counter: returns the variable step_count
        """
        #with encoder device - not verified due to missing hardware 
        # angle_pos=await self.encoder.angle_calc()
        # logging.debug(f"current angle: {angle_pos}")
        # pos_current=int(angle_pos/self.encoder.motor_step_angle)
        # return int(pos_current)     #Algo adaptation necessary so that angle can be passed
        
        #without encoder device:
        return self.step_count

    async def set_position(self, pos_goal: int) -> int: #without stopper 
        """
            Reading the current position
            Set stepper to goal position for game start
            Calculation step size

            Arguments:
                pos_goal: target position to be moved to
        """
        pos_current = await self.get_position()
        logging.debug(f"Port {self.name} current position {pos_current}")

        steps = pos_current-pos_goal
        direction = STEPPER.FORWARD if steps<0 else STEPPER.BACKWARD

        logging.debug(f"steps to go {abs(steps)} in direction {direction}")

        for _ in range(abs(steps)):
            self.motor.onestep(direction=direction, style=self.step_style)
            await asyncio.sleep(0.05)
            if direction == STEPPER.FORWARD:
                self.step_count = self.step_count+1
                #logging.debug(f"{self.name} step_count {self.step_count}")
            else:
                self.step_count = self.step_count-1
                #logging.debug(f"{self.name} step_count {self.step_count}"

        pos_current = await self.get_position()
        logging.debug(f"{self.name} check {pos_current} = {pos_goal} as start position?")
        return pos_current

    async def close(self):
        await super().close()

class Encoder():
    """
        Code not yet verified due to missing hardware: 

        Class to proof the rocking steppermotor myStepper1
        Connection asyncio and GPIO thread

        Attributes:
            pin_A: Encoder channel A connected to GPIO pin for Tx
            pin_B: Encoder channel B connectet to GPIO pin for Rx
    """
    motor_step_angle=0.45
    old_state='00'
    enc_imp=0

    def __init__(self):    
        self.direction=None
        # self.pin_A=None    #currently not defined
        # self.pin_B=None    #currently not defined    

        # self.input_A = Button(self.pin_A, pull_up=False)
        # self.input_B = Button(self.pin_B, pull_up=False)
        # self.input_A.when_pressed = self.enc_impulses
        # self.input_A.when_released = self.enc_impulses
        # self.input_B.when_pressed = self.enc_impulses
        # self.input_B.when_released = self.enc_impulses

    async def set_imp_count_zero(self):
        """
            Not yet verified: 
            Function to set pulse counter to 0,
            required at game_start
        """
        old_imp_val=self.enc_imp
        self.enc_imp=0
        logging.info(f"Encoder.set_imp_zero: old {old_imp_val} new {self.enc_imp}")

    def enc_impulses(self):
        """
            Event is called when edges are detected.
            Use Gray Code            
        """
        current_A= int(self.input_A.is_pressed)
        current_B= int(self.input_B.is_pressed)
        state=f"{current_A}{current_B}"

        if self.old_state=='00':
            if state=='01':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction ->")
                self.direction='Right'
            elif self.state=='10':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction <-")
                self.direction='Left'

        elif self.old_state=='01':
            if state=='11':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction ->")
                self.direction='Right'
            elif state=='00':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction <-")
                self.direction='Left'
                self.enc_imp= self.enc_imp-1

        elif self.old_state=='10':
            if state=='00':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction ->")
                self.direction='Right'
                self.enc_imp= self.enc_imp+1
            elif state=='11':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction <-")
                self.direction='Left'

        elif self.old_state=='11':
            if state=='10':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction ->")
                self.direction='Right'
            elif state=='01':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction <-")
                self.direction='Left'

        self.old_state=state

    def angle_calc(self):
        """
            Stepper angle calculation
        """
        total_angle = self.enc_imp * self.motor_step_angle
        return total_angle

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Device.pin_factory = PiGPIOFactory()
    #...