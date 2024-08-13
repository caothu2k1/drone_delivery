from copter.mission import myServo
import time
from copter.constants import *

servo = myServo(13)

while True:
    angle = int(input("Enter angle: "))
    if angle == 1:
        servo.move(OPEN_ANGLE_LID)
        time.sleep(1)
    if angle == 0:
        servo.move(CLOSED_ANGLE_LID)
        time.sleep(1)
    
