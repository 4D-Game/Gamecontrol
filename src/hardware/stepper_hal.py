#!/usr/bin/env python3

"""
Created: 08/01/22
by: Sonja Lukas
Tower control with 2 stepper
version Motor HAT library: MotorKit
classes: StepperHAL, Encoder
"""

import atexit
import asyncio
import board
import logging
import RPi.GPIO as GPIO

from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit

from hardware.hal import HAL

logging.basicConfig(level=logging.INFO)

class StepperHAL(HAL):
    """
        Stepper hardware application layer

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

    def __init__(self, stepper_name, port_number, stop_at_exit=True):
        """
            Arguments:
                stepper_name: stepper naming
                port_number: Motor HAT ports 1,2
                stop_at_exit: in case of crash or manual end Motor stop
        """
        self._station=MotorKit(i2c=board.I2C())
        if stop_at_exit:                            # Nicht notwendig.
            atexit.register(self.turn_off_motor)    # self.turn_off_motor in close
        self.name=stepper_name
        self.port_number=port_number
        if port_number==1:
            self.motor=self._station.stepper1
        elif port_number==2:
            self.motor=self._station.stepper2
        self.direction=STEPPER.FORWARD
        self.step_style=STEPPER.DOUBLE
        self.interval=0.05

        # Wozu is das notwendig?
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
        angle_pos=await Encoder.angle_calc()    # Encoder wird nicht initialisiert
        logging.debug(f"current angle: {angle_pos}")
        pos_current=int(angle_pos/1.8)
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

        # Kann auf eine for schleife reduziert werden
        steps = pos_current-pos_goal
        if steps>0:
            logging.debug(f"steps to go {steps}")
            for _ in range(steps):
                self.motor.onestep(direction=STEPPER.BACKWARD, style=self.step_style)
                await asyncio.sleep(0.05)
        elif steps<0:
            for _ in range(abs(steps)):
                self.motor.onestep(direction=STEPPER.FORWARD, style=self.step_style)
                await asyncio.sleep(0.05)

        pos_current = await self.get_position()
        logging.debug(f"{self.name} check current position {pos_current} is equal to {pos_goal}?")
        return pos_current

    async def rotate(self):
        """
            thread control
        """
        while True:
            self.motor.onestep(direction=self.direction, style=self.step_style)
            await asyncio.sleep(self.interval)
            #logging.info(f"rotate: {self.name} direction: {self.direction} with sleeptime {self.interval}")

    # selbe Funktion wie turn_off_motor
    async def motor_stop(self):
        """
            single motor hold for play algorithm
        """
        self.motor.release()
        logging.info(f"Check on hardware: motor stop {self.name}")

    # selbe Funktion wie motor stop
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
        await Encoder.remove_event_detect()    # Encoder wird nicht initialisiert
        logging.info(f"Encoder GPIO clear")

class Encoder(HAL):
    """
        Class to proof the rocking steppermotor myStepper1
        Connection asyncio and GPIO thread

        Attributes:
            pin_A: Encoder channel A connected to GPIO pin 25, Tx
            pin_B: Encoder channel B connectet to GPIO pin 24, Rx
            Event: BOTH rising and falling edges
    """

    # imp=0                   #for simulation only
    # state_test=0            #for simulation only
    motor_step_angle=1.8
    state='00'
    old_state='00'

    def __init__(self, loop=None, callback=None, direction=None):
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

        """GPIO interrupts mit gpiozero:

            from gpiozero import Buttons

            def pressed():
                print("button was pressed")

            def released():
                print("button was released")

            btn = Button(4)

            btn.when_pressed = pressed
            btn.when_released = released
        """

    # @asyncio.coroutine -> wurde durch das async vor der Funktion ersetzt
    async def gpio_event_on_loop_thread(self):
        """
            Stop the created loop after detection: async coroutine function call
        """
        #asyncio.sleep(0.001)
        logging.info('Stopping Event Loop')
        asyncio.get_event_loop().stop() # Wird das gesamte Programm beenden

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
        self.current_A= GPIO.input(self.Pin_A)                   # verwende lokale variablen
        self.current_B= GPIO.input(self.Pin_B)                   # verwende lokale variablen
        self.state="{}{}".format(self.current_A, self.current_B) # verwende f-strings self.state=f"{self.current_A}{self.current_B}", verwende lokale variable

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
        self.loop.call_soon_threadsafe(self.gpio_event_on_loop_thread) # wozu ist das notwendig

    # nicht notwendig da self.enc_imp nicht privat ist
    # muss nicht asynchron sein
    async def get_enc_imp(self):
        """
            Return of the current encoder pulse counter
        """
        return self.enc_imp

    # muss nicht asynchron sein
    async def angle_calc(self):
        """
            Stepper angle calculation
        """
        await self.get_enc_imp()
        total_angle= self.enc_imp * self.motor_step_angle
        return total_angle

    # async def close(self):
    async def remove_event_detect(self):
        """
            Clear the GPIO at the end
        """
        GPIO.cleanup()
