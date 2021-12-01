#!/usr/bin/env python3

"""
Created: 11/22/21
by: Sonja Lukas
Tower control with 2 stepper
Hardware part
"""
import time
import atexit 
import logging
import threading
import asyncio

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

class StepperHAL():
    """
        Hardware interface of tower
        Attributes:
            port_name: for port M1_M2 is equal to port_number 1
                       for port M3_M4 is equal to port_number 2
            port_number: only 1 or 2!
            rpm: set speed () - specified to between 0 - 30, increase possible
            addr: I2C address of the motor HAT, default is 0x60
        Power specified at hardware: 
            port_number 1: rock 
            port_number 2: rotate, both directions possible
        Style:
            specified on DOUBLE, others possible
        Threads:  thread_St1 and thread_St2   
    """ 

    def __init__(self, stepper_name, port_number, rpm, addr=0x60): 
        """
            with '_station' create an MotorHAT Object
            'turn_off_motor' required for auto-disabling motors on shutdown
        """
        self._station=Adafruit_MotorHAT(addr)    #composition attribute
        atexit.register(self.turn_off_motor) 
        self.steps=1                             #default step size

        self.name=stepper_name        #gets myStepper1 and myStepper2
        self.port_number=port_number  #only 1 or 2!
        self.motor=self._station.getStepper(200, self.port_number)   # 200 steps/rev, motor port #1 oder #2
        self.motor.setSpeed(rpm)      #kick off when tests show it´s necessary
        self.stepper_thread=threading.Thread()   #init empty threads
        self.count=0                  #only for tests!!!!!!!

    async def get_position(self):
        """
            current stepper position - for point system or game start
        """
        #todo Encoder()
        position = 50                 #only for current test!!!!!!!!!!!!!!!!!!!!!!!!!
        print(f"current position is {position}")
        return int(position)

    async def set_position(self, pos_goal, rpm:int=20 ) -> int:
        """
            set stepper position for game start
                Arguments: position_zero
        """ 
        self.motor.setSpeed(rpm)         #rpm at setup default=10
        pos_current=await(self.get_position())
        
        logging.info(f"Port {self.name} current position {pos_current}")
        
        steps=pos_current-pos_goal     #calc step size    
        if steps>0:
            self.motor.step(steps, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
            print(f"steps to go {steps}")
        elif steps<0:
            self.motor.step(abs(steps), Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
            print(f"steps to go {steps}")
        
        pos_current = self.get_position()
        logging.info(f"{self.name} check current position {pos_current} is equal to {pos_goal}?")
        print(f"{self.name} check current position {pos_current} is equal to {pos_goal}")
        return pos_current    

    def _stepper_worker(self, steps, direction, rpm):
        self.motor.setSpeed(rpm)
        self.motor.step(steps, direction, Adafruit_MotorHAT.DOUBLE)

    async def rotate(self, direction: Adafruit_MotorHAT, rpm:int, step_size:int):    #Threads #step_size default=100 #todo:variable  
        if not self.stepper_thread.isAlive(): 
            self.stepper_thread=threading.Thread(target=self._stepper_worker, args=(step_size,direction, rpm)) 
            self.count+=1
            self.stepper_thread.start()
            logging.info(f"create and start Thread {self.name} in {self.stepper_thread}")     

    async def motor_stop(self):
        """
            motor hold 
        """
        if self.port_number == 1:
            self._station.getMotor(1).run(Adafruit_MotorHAT.BRAKE)
            self._station.getMotor(2).run(Adafruit_MotorHAT.BRAKE)
            logging.info(f"{self.name} stop")
            print(f"{self.name} stop")
        elif self.port_number == 2:
            self._station.getMotor(3).run(Adafruit_MotorHAT.BRAKE)
            self._station.getMotor(4).run(Adafruit_MotorHAT.BRAKE)
            logging.info(f"Port {self.port_number} stop") 
            print(f"{self.name} stop")
        else:
            logging.info(f"Port {self.port_number} don´t stop")          
        
    def turn_off_motor(self):
        """
            Auto-disabling motors on shutdown   
        """
        self._station.getMotor(1).run(Adafruit_MotorHAT.RELEASE) 
        self._station.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self._station.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self._station.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
        logging.debug(f"Both ports release")
        
    async def close(self):
        #should only be controlled via the GameSDK
        #mqtt.client.disconnect()  #close tower mqtt connection 
        pass


class EncoderHAL():
    
    pass  


if __name__ == "__main__":
    Stepper1= StepperHAL("myStepper1",1,20) #port_name, port_number, rpm_init 
    Stepper2= StepperHAL("myStepper2",2,20) 

    #tests:
    #asyncio.run(Stepper1.get_position())                 #ok test get_position
    #asyncio.run(Stepper2.get_position())  
    #asyncio.run(Stepper1.set_position(0))                 #ok test set_position, both directions 
    #asyncio.run(Stepper2.set_position(0)) 
    #asyncio.run(Stepper2.rotate(Adafruit_MotorHAT.FORWARD, 20, 500)) #ok test threads manual
    #asyncio.run(Stepper1.rotate(Adafruit_MotorHAT.FORWARD, 10, 100)) 
    #asyncio.run(Stepper1.motor_stop())                               #single function test ok
    #asyncio.run(Stepper2.motor_stop())
