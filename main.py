import argparse
from FireBase.firebase import FireBase
from FireBase.Key_API import path, URL 
from dronekit import connect
from camera.detection import ObjectDectection
from copter.mission import Mission, myServo
from threading import Thread
from copter.constants import SPEED, CLOSED_ANGLE_LID
import time
from StereoVision.camera import Picam


def main(vehicle_port, model_path):
    # Connect to the Vehicle
    vehicle = connect(vehicle_port, wait_ready=True)
    # Initialize Firebase Database
    firebase = FireBase(path, URL)
    # Initialize YoLO Detection Model
    model = ObjectDectection(model_path)
    # Initialize servo
    gimbal = myServo(18)
    Servo_Lid = myServo(13)
    # Initialize dronekit Vehicle
    copter = Mission(vehicle, firebase, model, gimbal)
    # Initialize cameram
    cameraL = Picam(0)
    cameraR = Picam(1)
    Servo_Lid.move(CLOSED_ANGLE_LID)
    firebase.sendData('/location/Home', {
        'lat': vehicle.location.global_frame.lat,
        'lng': vehicle.location.global_frame.lon,
        'altitude': vehicle.location.global_relative_frame.alt,
        })
    firebase.sendData('/status/state', True)
    detect = Thread(target=copter.runModel, args=(cameraR,cameraL))
    loadData = Thread(target=copter.upLoadData)
    loadData.start()    
    detect.start()
    copter.start()
    copter.delivery(SPEED)
    time.sleep(5)
    copter.returnHome(SPEED)
    copter.stop()
    loadData.join()
    detect.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle_port", help="Vehicle port", default='/dev/ttyACM0')
    parser.add_argument("--model_path", help="Model path", default='./models/yolov8n_ncnn_model')
    args = parser.parse_args()

    main(args.vehicle_port, args.model_path)


