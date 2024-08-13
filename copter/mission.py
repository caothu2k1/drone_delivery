from dronekit import VehicleMode, LocationGlobalRelative
import time
from gpiozero import AngularServo
from copter.convert import get_distance_metres
import cv2
import sys
import datetime
from copter.commands import Command
from copter.constants import *
import os
sys.path.insert(0, './StereoVision')
import calibration

class myServo:
    def __init__(self, gpio):
        self.servo = AngularServo(gpio, min_pulse_width=0.0006, max_pulse_width=0.0023)
        self.servo.detach()
    def move(self, angle, sleep = 0.2):
        self.servo.angle = angle
        time.sleep(sleep)
        self.servo.detach()

class Mission:
    def __init__(self, vehicle, firebase, model, gimbal = None, servo_lid = None):
        self.vehicle = vehicle
        self.firebase = firebase
        self.model = model
        self.gimbal = gimbal
        self.servo_lid = servo_lid
        self.isRunning = True
        self.isEmergency = False
        self.Data = None
        self.uploadImg = None
        self.Enable = False
        self.RTL_HOME = False
        self.waypoints = None

    def arm_and_takeoff(self, aTargetAltitude):
        print("Waiting for vehicle to initialise...")
        while not self.vehicle.is_armable:
            pass
        print("Arming motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        print("Waiting for arming...")
        while not self.vehicle.armed:
            pass
        print("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)
        while True:
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break

    def avoidObstacles(self, targetLocation, speed):
        while True:
            lidar_distance = self.vehicle.rangefinder.distance
            if lidar_distance > 1 and not self.Data:
                break
            else:
                if lidar_distance < 1:
                    Command.moveUp(self.vehicle, 0.5) 
                if self.Data:
                    for obj in  self.Data:
                        label, position = obj[0], obj[1]
                        x, y, z = position
                        if z < MIN_OBJECT_Z:
                            Command.moveBackward(self.vehicle,1)
                            continue
                        if abs(x) < MIN_OBJECT_XY:
                            if x > 0:
                                Command.moveLeft(self.vehicle, 0.5)
                            else:
                                Command.moveRight(self.vehicle, 0.5)
                self.goto(targetLocation, speed)

    def TrackingLandingPad(self):
        while True:
            altitude = self.vehicle.location.global_relative_frame.alt
            if altitude <= DISTANCE_LAND:
                self.Landing()
                break
            if not self.Enable:
                self.isEmergency = True
                self.Landing()
                break
            landing_pad_detected = False
            obstacles_detected = False
            landing_pad_position = None
            closest_obstacle_position = None
            if not self.Data:
                Command.moveDown(self.vehicle, 0.5)
                print("No data")
                continue
            else:
                for obj in self.Data:
                    label, position = obj[0], obj[1]
                    if label == "landing_pad":
                        landing_pad_detected = True
                        landing_pad_position = position
                    else:
                        obstacles_detected = True
                        closest_obstacle_position = position

                if landing_pad_detected and not obstacles_detected:
                    x, y, z = landing_pad_position
                    if abs(x) > MIN_LANDING_PAD_XY:
                        if x > 0:
                            print("Move right")
                            Command.moveRight(self.vehicle, MIN_LANDING_PAD_XY, 1)
                        else:
                            print("Move left")
                            Command.moveLeft(self.vehicle, MIN_LANDING_PAD_XY, 1)
                    if abs(y) > MIN_LANDING_PAD_XY:
                        if y > 0:
                            print("Move backward")
                            Command.moveBackward(self.vehicle, MIN_LANDING_PAD_XY, 1)
                        else:
                            print("Move forward")
                            Command.moveForward(self.vehicle, MIN_LANDING_PAD_XY, 1)
                        
                    if abs(x) <= MIN_LANDING_PAD_XY and abs(y) <= MIN_LANDING_PAD_XY:
                        Command.moveDown(self.vehicle, 0.5)
                        print("move down")
                        
                if obstacles_detected:
                    x, y, z = closest_obstacle_position
                    if z < MIN_OBJECT_Z:
                        print("Move up")
                        Command.moveUp(self.vehicle, 0.5)
                    if abs(x) < MIN_OBJECT_XY:
                        if x > 0:
                            print("Move left object")
                            Command.moveLeft(self.vehicle, 0.5)
                        else:  
                            print("Move right object")
                            Command.moveRight(self.vehicle, 0.5)

    def goto(self, targetLocation, speed):
        distanceToTargetLocation = get_distance_metres(targetLocation, self.vehicle.location.global_relative_frame)
        self.vehicle.simple_goto(targetLocation, groundspeed=speed)

        while self.vehicle.mode.name == "GUIDED":
            currentDistance = get_distance_metres(targetLocation, self.vehicle.location.global_relative_frame)
            if currentDistance < distanceToTargetLocation * 0.05:
                print("Reached target waypoint.")
                break
            if not self.Enable:
                self.isEmergency = True
                self.Landing()
                break
            if self.RTL_HOME:
                self.vehicle.mode = VehicleMode("RTL")
                print("Drone is RTL....")
                self.RTL_HOME = True
                while self.vehicle.armed:
                    pass
                break
            self.avoidObstacles(targetLocation, speed)
    def Landing(self):
        self.vehicle.mode = VehicleMode("LAND")
        print("Drone is landing....")
        while self.vehicle.armed:
            pass

    def delivery(self, speed):
        self.gimbal.move(MAX_ANGLE_GIMBAL,0.1)
        self.arm_and_takeoff(self.waypoints[0].alt)
        for point in self.waypoints[1:]:
            self.goto(point, speed)
        if not self.isEmergency and not self.RTL_HOME:
            self.gimbal.move(MIN_ANGLE_GIMBAL,0.1)
            self.Landing()
            self.TrackingLandingPad()
            self.servo_lid.move(OPEN_ANGLE_LID)

    def returnHome(self, speed):
        self.gimbal.move(MAX_ANGLE_GIMBAL,0.1)
        if not self.isEmergency and not self.RTL_HOME:
            self.arm_and_takeoff(self.waypoints[-1].alt) 
            self.servo_lid.move(CLOSED_ANGLE_LID)
            for point in self.waypoints[-2::-1]:
                self.goto(point, speed)
            if not self.isEmergency and not self.RTL_HOME:
                self.gimbal.move(MIN_ANGLE_GIMBAL,0.1)
                self.TrackingLandingPad()

    def runModel(self, cameraR, cameraL):
        frameL = cameraL.begin()
        frameR = cameraR.begin()
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can also use 'MP4V' for .mp4 files
        out = cv2.VideoWriter(f'./camera/videos/{current_datetime}.avi', fourcc, 5.0, (1280, 480))  # Initial placeholder FPS
        while True:
            start_time = time.time()
            frameL = cameraL.begin()
            frameR = cameraR.begin()
            self.uploadImg = frameR
            frameR, frameL = calibration.undistortRectify(frameR, frameL)
            frame, self.Data = self.model.detect(frameR, frameL)
            elapsed_time = time.time() - start_time
            fps = 1.0 / elapsed_time
            cv2.putText(frame, f'FPS: {int(fps)}', (10,460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            out.write(frame)
            
            if not self.isRunning:
                break
        cameraL.stop()
        cameraR.stop()
        out.release()
    
    def getWaypoint(self):
        wp = []
        points = self.firebase.getData('/location/waypoints')
        Home = self.firebase.getData('/location/Home')
        if points is None:
            print("No waypoints")
            return []
        else:
            wp.append(LocationGlobalRelative(Home['lat'], Home['lng'], Home['altitude']))
            for point in points.values():
                wp.append(LocationGlobalRelative(point['lat'], point['lng'], point['altitude']))
            return wp
    
    def upLoadData(self):
        while True:
            data = {
                'mode': self.vehicle.mode.name,
                'battery': self.vehicle.battery.level,
                'altitude': self.vehicle.location.global_relative_frame.alt,
                'speed': round(self.vehicle.groundspeed),
                'target': {
                    'lat': self.vehicle.location.global_relative_frame.lat,
                    'lng': self.vehicle.location.global_relative_frame.lon,
                    'compass': self.vehicle.heading
                }
            }
            if self.uploadImg is not None:
                image_bytes = cv2.imencode('.jpg', self.uploadImg)[1].tobytes()
                self.firebase.uploadImg(image_bytes, 'images')
            self.firebase.sendData('/parameters', data)
            self.Enable = self.firebase.getData('/status/enable')
            self.RTL_HOME = self.firebase.getData('/status/RTL')
            print(self.Data)
            time.sleep(1)
            if not self.isRunning:
                break

    def start(self):
        print("Please, wait enable")
        while True:
            self.waypoints = self.getWaypoint()
            if self.Enable:
                if self.waypoints:
                    break
            time.sleep(1)
        
    def stop(self):
        self.isRunning = False
        self.firebase.sendData('/status',{
            'state': False,
            'enable': False,
            'RTL': False
        })
        print("Mission complete !!")
        self.vehicle.close()

