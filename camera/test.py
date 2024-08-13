from detection import ObjectDectection
import sys
import cv2
from dronekit import connect
import time
sys.path.insert(0, './StereoVision')
from camera import Picam
import calibration
import numpy as np
model_path = "./models/yolov8n_ncnn_model"
model = ObjectDectection(model_path)
vehicle = connect('/dev/ttyACM0', wait_ready=True)
# Initialize the camera
cameraL = Picam(0)
cameraR = Picam(1)
while True:
    frameL= cameraL.begin()
    frameR= cameraR.begin()
    frameR,frameL = calibration.undistortRectify(frameR, frameL)
    frame ,_ = model.detect(frameR, frameL)
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cv2.destroyAllWindows()

