#!/usr/bin/python3
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit 

class StepperTest():
    def __init__(self,count=0,stepstyle= Adafruit_MotorHAT.DOUBLE):
        self.stepstyle=stepstyle
        self.count=count  
       
    async def rock(self): 
        for count in range(10):
            dir_rock=Adafruit_MotorHAT.FORWARD
            count +=1
            print(f"rock forward step_count{count}!")
        for count in range (10):
            count +=1
            dir_rock=Adafruit_MotorHAT.BACKWARD
            print(f"rock backward step_count{count}!")

    async def rotate(self):
        myStepper2=Adafruit_MotorHAT.FORWARD
        print("rotate stepper 2!") 

    def turnOffMotors(self):
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

# create a default object, no changes to I2C address or frequency
#StepperTest = Adafruit_MotorHAT()

myStepper1 = StepperTest.getStepper(200, 1)      # 200 steps/rev, motor port #1
myStepper2 = StepperTest.getStepper(200, 2)      # 200 steps/rev, motor port #2
myStepper1.setSpeed(30)          # 30 RPM
myStepper2.setSpeed(60)          # 60 RPM
#stepstyles = [Adafruit_MotorHAT.SINGLE, Adafruit_MotorHAT.DOUBLE, Adafruit_MotorHAT.INTERLEAVE, Adafruit_MotorHAT.MICROSTEP]
#stepstyle = Adafruit_MotorHAT.DOUBLE

atexit.register(turnOffMotors)

if __name__ == "__main__": #called as program not as module #only for testing
    while(True):
        rock(myStepper1)
        rotate(myStepper2)







