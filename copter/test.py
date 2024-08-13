from dronekit import connect, VehicleMode
import time
from commands import Command
import math
from convert import get_location_metres, get_distance_metres
from pymavlink import mavutil
import math
vehicle = connect('tcp:192.168.1.125:5762', wait_ready=True)

def calculate_yaw_to_target(current_position, target_position):
    north, east, _ = target_position
    current_north, current_east, _ = current_position
    delta_north = north - current_north
    delta_east = east - current_east
    yaw = math.degrees(math.atan2(delta_east, delta_north))
    return yaw

def setYaw(vehicle, heading, relative=False):

    if relative:
        is_relative = 1 #yaw relative to direction of travel
    else:
        is_relative = 0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

        
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)

def goto(dNorth, dEast, gotoFunction=vehicle.simple_goto):
    currentLocation = vehicle.location.global_relative_frame
    targetLocation = get_location_metres(currentLocation, dNorth, dEast)
    targetDistance = get_distance_metres(currentLocation, targetLocation)
    yaw = get_bearing(currentLocation, targetLocation)
    setYaw(vehicle, yaw)
    gotoFunction(targetLocation)
    
    #print "DEBUG: targetLocation: %s" % targetLocation
    #print "DEBUG: targetLocation: %s" % targetDistance

    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        #print "DEBUG: mode: %s" % vehicle.mode.name
        remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
        if remainingDistance<=targetDistance*0.05: #Just below target, in case of undershoot.
            print("Reached target")
            break


def get_bearing(aLocation1, aLocation2):
    off_x = aLocation2.lon - aLocation1.lon
    off_y = aLocation2.lat - aLocation1.lat
    bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
    if bearing < 0:
        bearing += 360.00
    return bearing

#Arm and take of to altitude of 5 meters
arm_and_takeoff(5)
goto(-20, 0)
Command.moveLeft(vehicle, 5)
time.sleep(5)
Command.moveRight(vehicle, 5)
time.sleep(5)
Command.moveForward(vehicle, 5)
time.sleep(5)
Command.moveBackward(vehicle, 5)
time.sleep(5)
Command.moveUp(vehicle, .5)
time.sleep(5)
Command.moveDown(vehicle, .5)
time.sleep(5)
goto(20, 0)
vehicle.close()





