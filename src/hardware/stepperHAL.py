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
#import mqtt

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

    def __init__(self, port_name, port_number, rpm, addr=0x60): 
        """
            with '_station' create an MotorHAT Object
            'turn_off_motor' required for auto-disabling motors on shutdown
        """
        self._station=Adafruit_MotorHAT(addr)  #composition attribute
        atexit.register(self.turn_off_motor)
        steps=1 #step size for set_position()
#possible problem: port_name used twice!!!?
        self.port_name=port_name     #gets myStepper1 and myStepper2
        self.port_number=port_number #only 1 or 2!
        self.port_name=self._station.getStepper(200,self.port_number)      # 200 steps/rev, motor port #1 oder #2
            #myStepper2=station.getStepper(200,2)                   # 200 steps/rev, motor port #2
        self.port_name.setSpeed(rpm) #kick off
        self.port_thread=threading.Thread() #init empty threads

    async def get_position(self):
        """
            current stepper position - for point system or game start
        """
        #todo Encoder()
        position = 15 #only for current test!!!!!!!!!!!!!!!!!!!!!!!!!
        logging.info(f"current position is {position}")
        return int(position)  

    async def set_position(self, position_zero, rpm:int=10 ) -> int:
        """
            set stepper position for game start
                Arguments: position_zero
        """ 
        self.port_name.setSpeed(rpm)         #rpm at setup default=10
        position=self.get_position()
        logging.info(f"Port {self.port_name} current position {position}") 
        while(position!=position_zero):      #current declared step size = 1
            if position>position_zero:
                steps=position-position_zero #calc step size    
                self.port_name(steps, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
                logging.info(f"Port {self.port_name} current position {position}")
                #todo: step backward to zero
            elif position<position_zero:
                steps=position_zero-position #calc step size                
                self.port_name(steps, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
                logging.info(f"Port {self.port_name} current position {position}")
                #todo: step forward to zero
        else:
            logging.info(f"Port {self.port_name} check current position {position} is equal to {position_zero}")
            if position == position_zero:
                self.port_name(Adafruit_MotorHAT.BREAK)
                return True #ready    

    def stepper_worker(self, steps, direction, rpm):
        self.port_name.setSpeed(rpm)
        self.port_name.step(steps, direction, Adafruit_MotorHAT.DOUBLE)

    def rotate(self, direction, rpm, thread_step_size:int=100):    #Threads #step_size default=100 #todo:variable  
        while(True):        
            if not self.port_thread.isAlive(): 
                if direction in ['forward', 'fw', 'f', 1]:
                    direction=Adafruit_MotorHAT.FORWARD
                elif direction in ['backward', 'bw', 'b', 0]:
                    direction=Adafruit_MotorHAT.BACKWARD
                else:
                    direction=Adafruit_MotorHAT.BREAK   #error hold on
                self.port_thread=threading.Thread(target=stepper_worker, args=(self.port_name,thread_step_size,direction, rpm)) 
                self.port_thread.start()
                logging.info(f"create and start Thread {self.port_name} in {self.port_thread}")
            time.sleep(0.1)  # Small delay to stop from constantly polling threads       

    async def motor_stop(self, port_number):
        if port_number == 1:
            self._station.getMotor(1).run(Adafruit_MotorHAT.BREAK)
            self._station.getMotor(2).run(Adafruit_MotorHAT.BREAK)
            logging.info(f"Port {self.port_number} stop")    
        elif port_number == 2:
            self._station.getMotor(3).run(Adafruit_MotorHAT.BREAK)
            self._station.getMotor(4).run(Adafruit_MotorHAT.BREAK)
            logging.info(f"Port {self.port_number} stop")  
        else:
            logging.info(f"Port {self.port_number} don´t stop")          

    async def turn_off_motor(self):
        """
            Auto-disabling motors on shutdown   
        """
        self._station.getMotor(1).run(Adafruit_MotorHAT.RELEASE) 
        self._station.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self._station.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self._station.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
        logging.info(f"Both ports release")

    async def close(self):
        #should only be controlled via the GameSDK
        #mqtt.client.disconnect()  #close tower mqtt connection 
        pass


class EncoderHAL():
    pass  

if __name__ == "__main__":
    Stepper1= StepperHAL("myStepper1",int:1,int:10) #port_name, port_number, rpm_init 
    myStepper1.set_position(15)             #target position
