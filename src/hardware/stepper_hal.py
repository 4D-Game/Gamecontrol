#!/usr/bin/env python3

"""
Created: 08/01/22
by: Sonja Lukas
Tower control with 2 stepper
version Motor HAT library: MotorKit
classes: StepperHAL, Encoder
"""

#import atexit
import asyncio
import board
import logging

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
                interval: waiting time
                angle_max: limit rocking forward stepper1
                angle_min: limit rocking backward stepper1
                interval_max: max. waiting time rotate stepper 2
                interval_min: min. waiting time rotate stepper 2
    """

    direction=STEPPER.FORWARD
    step_style=STEPPER.DOUBLE
    interval=0.05

    def __init__(self, stepper_name, port_number):
        """
            Arguments:
                stepper_name: stepper naming
                port_number: Motor HAT ports 1,2
        """
        station=MotorKit(i2c=board.I2C())
        self.name=stepper_name
        self.port_number=port_number
        if port_number==1:
            self.motor=station.stepper1
        elif port_number==2:
            self.motor=station.stepper2

    async def rotate(self):
        """
            thread control
        """
        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            await asyncio.sleep(self.interval)
            #logging.debug(f"rotate: {self.name} direction: {self.direction} with sleeptime {self.interval}")

    def motor_stop(self):
        """
            single motor hold for play algorithm and after end of game
        """
        self.motor.release()
        logging.info(f"Check on hardware: motor stop {self.name}")

    async def close(self):
        """
           stop and release motor
        """
        await self.motor_stop()
        logging.info(f"stepperHAL close: {self.name}")

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

    async def get_position(self):
        """
            returns current stepper position as angle - for point system or game start
        """
        angle_pos=await self.encoder.angle_calc()
        logging.debug(f"current angle: {angle_pos}")
        pos_current=int(angle_pos/self.encoder.motor_step_angle)
        return int(pos_current)

    async def set_position(self, pos_goal: int) -> int:
        """
            Reading the current angle position
            Set stepper to goal angle for game start or on game
            Calculatio step size

            Arguments:
                pos_goal: target position to be moved to
        """
        pos_current=await self.get_position()
        logging.debug(f"Port {self.name} current position {pos_current}")

        steps = pos_current-pos_goal
        direction = STEPPER.FORWARD if steps<0 else STEPPER.BACKWARD

        logging.debug(f"steps to go {steps}")
        for _ in range(steps):
            self.motor.onestep(direction=direction, style=self.step_style)
            await asyncio.sleep(0.05)

        pos_current = await self.get_position()
        logging.debug(f"{self.name} check current position {pos_current} is equal to {pos_goal}?")
        return pos_current

    async def close(self):
        await super().close()
        await self.encoder.remove_event_detect()
        logging.info(f"Encoder GPIO clear")


class Encoder():
    """
        Class to proof the rocking steppermotor myStepper1
        Connection asyncio and GPIO thread

        Attributes:
            pin_A: Encoder channel A connected to GPIO pin 25, Tx
            pin_B: Encoder channel B connectet to GPIO pin 24, Rx
    """
    motor_step_angle=1.8
    old_state='00'
    enc_imp=0

    def __init__(self):
        self.direction=None
        self.pin_A=25 
        self.pin_B=24

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setwarnings(True)
        # GPIO.setup(self.Pin_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # GPIO.setup(self.Pin_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # self.loop=asyncio.get_event_loop()
        # GPIO.add_event_detect(self.Pin_A, GPIO.BOTH, callback=self.enc_impulses)
        # GPIO.add_event_detect(self.Pin_B, GPIO.BOTH, callback=self.enc_impulses)

        self.input_A = Button(self.pin_A, pull_up=False)
        self.input_B = Button(self.pin_B, pull_up=False)

        self.input_A.when_pressed = self.enc_impulses
        self.input_A.when_released = self.enc_impulses
        self.input_B.when_pressed = self.enc_impulses
        self.input_B.when_released = self.enc_impulses

    # # @asyncio.coroutine -> wurde durch das async vor der Funktion ersetzt
    # async def gpio_event_on_loop_thread(self):
    #     """
    #         Stop the created loop after detection: async coroutine function call
    #     """
    #     #asyncio.sleep(0.001)
    #     logging.info('Stopping Event Loop')
    #     asyncio.get_event_loop().stop() # Wird das gesamte Programm beenden

    async def set_imp_zero(self):
        """
            Function to set pulse counter to 0,
            required at game_start
        """
        old_imp_val=self.enc_imp
        self.enc_imp=0
        logging.info(f"Encoder.set_imp_zero: old {old_imp_val} new {self.enc_imp}")

    def enc_impulses(self):
        """
            Event is called when edges are detected
            Gray code
                    
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
                if self.callback is not None:
                   self.callback(self.enc_imp, self.direction)

        elif self.old_state=='10':
            if state=='00':
                logging.debug(f"old_state {self.old_state}, new_state {state}, direction ->")
                self.direction='Right'
                self.enc_imp= self.enc_imp+1
                if self.callback is not None:
                   self.callback(self.enc_imp, self.direction)
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