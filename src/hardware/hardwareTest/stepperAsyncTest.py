#!/usr/bin/python3
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit 
import asyncio

StepperTest=Adafruit_MotorHAT()

myStepper1 = StepperTest.getStepper(200,1)      # 200 steps/rev, motor port #1
myStepper2 = StepperTest.getStepper(200,2)      # 200 steps/rev, motor port #2
myStepper1.setSpeed(10)          # xx RPM rock
myStepper2.setSpeed(50)          # xx RPM rotate

async def rock():
    print(f"rock backward")    
    for count1 in range(100):
        myStepper1.step(1, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
        count1 +=1
        #await asyncio.sleep(0.03)
        task=asyncio.create_task(rotate())
        await task  
    print(f"rock forward")    
    for count2 in range(100):   
        myStepper1.step(1, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
        count2 +=1
        task2=asyncio.create_task(rotate())
        await task2
        #await asyncio.sleep(0.03)  

async def rotate():
    print("rotate stepper 2!")     
    myStepper2.step(5, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
    #await asyncio.sleep(0.03)

def turnOffMotors():
    StepperTest.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    StepperTest.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    StepperTest.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    StepperTest.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

if __name__ == "__main__": #called as program not as module #only for testing
    while(True):
        count2=0
        count1=0
        asyncio.run(rock())
        #asyncio.run(rotate())