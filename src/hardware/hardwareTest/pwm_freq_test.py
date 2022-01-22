#!/usr/bin/env python3

from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit

import board

kit = MotorKit(i2c=board.I2C())

kit.frequency=10000
step= kit.stepper1
