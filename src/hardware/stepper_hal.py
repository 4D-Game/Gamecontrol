import asyncio
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
                direction: stepper direction with default FORWARD
                step_style: step type with default DOUBLE
                interval: initial waiting time
                step_count: motor rock control without encoder
                motor_step_angle: step resolution with step_style DOUBLE
                max_angle: max rocking angle
                min_angle: min rocking angle
                motor: Stepper reference
                forward_stopper: micro-limit-switch at GPIO Pin 24
                backward_stopper: micro-limit-switch at GPIO Pin 25
    """
    direction:Literal = STEPPER.FORWARD
    step_style:int = STEPPER.DOUBLE
    interval:float = 0.03
    step_count:int = 0
    motor_step_angle:float = 0.225
    max_angle:float = float(16)
    min_angle:float = float(-16)

    def __init__(self, stepper_name, port_number, stop_at_exit=True):
        """
            Initialize motors and stopper

            Arguments:
                stepper_name: Name of the stepper
                port_number: Motor HAT ports 1, 2
        """

        station=MotorKit(i2c=board.I2C())
        self.name=stepper_name
        self.port_number=port_number
        if port_number==1:
            self.motor=station.stepper1
        elif port_number==2:
            self.motor=station.stepper2
        if stop_at_exit:
            atexit.register(self.motor_stop)  #necessary as motor voltage is otherwise not released

        if port_number ==1:
            self.forward_stopper = Button(24, pull_up=True)             #GPIO 24 stopper
            self.backward_stopper = Button(25, pull_up=True)            #GPIO 25 stopper
            self.forward_stopper.when_pressed = self.change_direction   #Callback functions
            self.backward_stopper.when_pressed = self.change_direction

    async def rock(self): #Rocking Stepper
        """
            Rock stepper within given angle
        """

        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            await asyncio.sleep(self.interval)
            logging.debug(f"rock_direction: {self.direction} with interval {self.interval}")

            step = (1 if self.direction == STEPPER.FORWARD else - 1)
            self.step_count = self.step_count + step

            logging.debug(f"{self.name} step_count {self.step_count}")

            rock_angle=self.step_count*self.motor_step_angle
            self.change_direction(rock_angle)     #option: add conditions here

    def change_direction(self, angle:float = 0):  #Rocking Stepper
        """
            Change direction when stopper is pressed

            Arguments:
                angle: current position in degree
        """

        if angle >= self.max_angle or self.forward_stopper.is_pressed:                 #trigger: max. def. angle
            self.direction=STEPPER.BACKWARD
            logging.info(f"direction changes to BACKWARD")
        elif angle <= self.min_angle or self.backward_stopper.is_pressed:               #trigger: min. def. angle
            self.direction=STEPPER.FORWARD
            logging.info(f"direction changes to FORWARD")

    async def rotate(self):
        """
            Rotate stepper
        """

        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            await asyncio.sleep(self.interval)
            logging.debug(f"rotate: {self.name} direction: {self.direction} with interval {self.interval}")

    def motor_stop(self):
        """
            Single motor hold
        """

        self.motor.release()

    def close(self):
        """
           Stop and release motor
        """

        self.motor_stop()
        logging.info(f"Close stepper {self.name}")


class EncoderStepperHAL(StepperHAL): #currently works with stopper instead of an encoder
    """
        Stepper hardware abstraction layer for Rocking Stepper with encoder simulated by counting the steps

        Attributes:
                direction: stepper direction with default FORWARD
                step_style: step type with default DOUBLE
                max_angle: forward limit for Rocking Stepper
                min_angle: backward limit for Rocking Stepper
    """

    def __init__(self, stepper_name, port_number, stop_at_exit=True):
        """
            Arguments:
                stepper_name: stepper naming
                port_number: Motor HAT ports 1,2
        """
        super().__init__(stepper_name, port_number, stop_at_exit=True)
        #self.encoder = Encoder()      #currently not used

    async def get_position(self):      #currently without stopper
        """
            Return:
                Stepper position in steps (0 == Center)
        """

        return self.step_count  #WITHOUT encoder device

        #WITH encoder device - not verified due to missing working hardware
        # angle_pos=await self.encoder.angle_calc()
        # logging.debug(f"current angle: {angle_pos}")
        # pos_current=int(angle_pos/self.encoder.motor_step_angle)
        # return int(pos_current)     #Algo adaptation necessary so that angle can be passed

    async def calibrate(self): #with stopper
        """
            Determine middle position rocking stepper by stopper
        """

        direction=STEPPER.FORWARD               #used current interval
        interval=0.05
        while(not self.forward_stopper.is_pressed):
            self.motor.onestep(direction=direction, style=self.step_style)
            await asyncio.sleep(interval)

        direction=STEPPER.BACKWARD
        counter=0
        while(not self.backward_stopper.is_pressed):
            self.motor.onestep(direction=direction, style=self.step_style)
            await asyncio.sleep(interval)
            counter += 1

        middle=round(counter/2)
        logging.info(f"Found center at {middle} steps")

        for _ in range(middle):
            self.motor.onestep(direction=STEPPER.FORWARD, style=self.step_style)
            await asyncio.sleep(interval)

        self.step_count=0             #start_position; counter reset


    async def set_position(self, pos_goal: int) -> int: #without stopper
        """
            Move stepper to given position

            Arguments:
                pos_goal: target position to be moved to in steps (negative => backward, positive => forward)
        """

        pos_current = await self.get_position()
        logging.debug(f"Port {self.name} current position {pos_current}")

        steps = pos_current-pos_goal
        direction = STEPPER.FORWARD if steps<0 else STEPPER.BACKWARD

        logging.debug(f"steps to go {abs(steps)} in direction {direction}")

        for _ in range(abs(steps)):
            self.motor.onestep(direction=direction, style=self.step_style)
            await asyncio.sleep(self.interval)

            if direction == STEPPER.FORWARD:
                self.step_count = self.step_count+1
            else:
                self.step_count = self.step_count-1

            logging.debug(f"{self.name} step_count {self.step_count}")

        pos_current = await self.get_position()
        logging.debug(f"{self.name} check {pos_current} = {pos_goal} as start position?")
        return pos_current

class Encoder():
    """
        !!! WARNING
            Encoder not yet verified due to missing hardware

        Class to get position information from encoder

        Attributes:
            pin_A: Encoder channel A connected to GPIO pin for Tx
            pin_B: Encoder channel B connectet to GPIO pin for Rx
    """
    motor_step_angle:float = 0.225
    old_state:str = '00'
    enc_imp:int = 0

    def __init__(self):
        self.direction = None
        # self.pin_A=xx    #currently not defined
        # self.pin_B=xx    #currently not defined

        # self.input_A = Button(self.pin_A, pull_up=False)
        # self.input_B = Button(self.pin_B, pull_up=False)
        # self.input_A.when_pressed = self.enc_impulses
        # self.input_A.when_released = self.enc_impulses
        # self.input_B.when_pressed = self.enc_impulses
        # self.input_B.when_released = self.enc_impulses

    async def set_imp_count_zero(self):
        """
            Set pulse counter to zero
        """

        old_imp_val=self.enc_imp
        self.enc_imp=0
        logging.info(f"Encoder.set_imp_zero: old {old_imp_val} new {self.enc_imp}")

    def enc_impulses(self):
        """
            Callbacks when edges are detected

            Decode Gray Code and update counter
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