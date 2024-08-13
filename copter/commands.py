from pymavlink import mavutil # Needed for command message definitions
import time
import math
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

def resetYaw(vehicle):
    # Create the DO_SET_ROI command to reset yaw to follow direction of travel
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
        0, #confirmation
        0, 0, 0, 0, # param 1 ~ 4 not used for resetting ROI
        0, 0, 0)    # param 5 ~ 7 are the coordinates to reset the ROI
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()

def setPositionTarget(vehicle, north, east, down):  
    ignoreVelocityMask =  0b111000
    ignoreAccelMask =  0b111000000
    ignoreYaw = 0b10000000000
    emptyMask = 0b0000000000000000
    yawRate = vehicle.heading
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # Use offset from current position
        emptyMask + ignoreAccelMask + ignoreVelocityMask + ignoreYaw, # type_mask
        north, east, down,
        0, 0, 0, # x, y, z velocity in m/s (not used)
        0, 0, 0, # x, y, z acceleration (not used)
        0, math.radians(yawRate))    # yaw, yaw_rate

    vehicle.send_mavlink(msg)

def send_ned_velocity(vehicle, velocity_x, velocity_y, velocity_z, duration):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 

    # send command to vehicle on 1 Hz cycle
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

class Command:

    # move vehicle to left in meters
    def moveLeft(vehicle, distance, sleep=2):   
        setPositionTarget(vehicle,0, -distance, 0)
        time.sleep(sleep)

    # move vehicle to right in meters
    def moveRight(vehicle, distance,sleep=2):
        setPositionTarget(vehicle,0, distance, 0)
        time.sleep(sleep)

    # move vehicle Forward in meters
    def moveForward(vehicle, distance,sleep=2):
        setPositionTarget(vehicle,distance, 0, 0)
        time.sleep(sleep)

    # move vehicle Backward in meters
    def moveBackward(vehicle, distance,sleep=2):
        setPositionTarget(vehicle,-distance, 0, 0)
        time.sleep(sleep)

    # move vehicle up in meters
    def moveUp(vehicle, distance,sleep=2):
        setPositionTarget(vehicle,0, 0, -distance)
        time.sleep(sleep)

    # move vehicle Down in meters
    def moveDown(vehicle, distance,sleep=2):
        setPositionTarget(vehicle,0, 0, distance)
        time.sleep(sleep)




