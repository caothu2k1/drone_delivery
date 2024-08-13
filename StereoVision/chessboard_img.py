import cv2
import numpy as np
from camera import Picam
# Photo session settings
chessboardSize = (9,6)
frameSize = (640,480)
total_photos = 100 # Number of images to take
cameraL = Picam(1)
cameraR = Picam(0)
counter = 0
while True:
    frameL = cameraL.begin()
    frame_left = frameL.copy()
    frameR = cameraR.begin()
    frame_right = frameR.copy()
    retL, cornersL = cv2.findChessboardCorners(frameL, chessboardSize, None)
    retR, cornersR = cv2.findChessboardCorners(frameR, chessboardSize, None)
    key = cv2.waitKey(1) & 0xFF
    if (key == ord("s")):
        counter += 1
        leftName = './StereoVision/images/left_'+str(counter).zfill(2)+'.png'
        rightName = './StereoVision/images/right_'+str(counter).zfill(2)+'.png'
        cv2.imwrite(leftName, frame_left)
        cv2.imwrite(rightName, frame_right)
        print ('Pair No '+str(counter)+' saved.')
    # Draw cowntdown counter, seconds
    frameL = cv2.drawChessboardCorners(frameL, chessboardSize, cornersL, retL)
    frameR = cv2.drawChessboardCorners(frameR, chessboardSize, cornersR, retR)
    combined_frame = np.hstack((frameL, frameR))
    cv2.imshow("pair", combined_frame)
    key = cv2.waitKey(1) & 0xFF
    if (key == ord("q")) | (counter == total_photos):
      break
print ("Photo sequence finished")
cameraL.stop()
cameraR.stop()
