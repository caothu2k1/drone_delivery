import cv2
import numpy as np
import sys
import json
from camera import Picam
sys.path.insert(0, './StereoVision')
import calibration

# Initialize camera
cameraL = Picam(1)
cameraR = Picam(0)

# Depth map default preset
SWS = 10
PFS = 12
PFC = 20
MDS = -32
NOD = 100
TTH = 92
UR = 15
SR = 20
SPWS = 76

sgbm = cv2.StereoSGBM_create(minDisparity=MDS, numDisparities=NOD, blockSize=21)

def stereo_depth_map(dmRight, dmLeft):
    disparity = sgbm.compute(dmLeft, dmRight)
    local_max = disparity.max()
    local_min = disparity.min()
    disparity_grayscale = (disparity-local_min)*(65535.0/(local_max-local_min))
    disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255.0/65535.0))
    disparity_color = cv2.applyColorMap(disparity_fixtype, cv2.COLORMAP_JET)
    return disparity_color

def load_map_settings( fName ):
    global SWS, PFS, PFC, MDS, NOD, TTH, UR, SR, SPWS, loading_settings
    print('Loading parameters from file...')
    f=open(fName, 'r')
    data = json.load(f)
    SWS=data['SADWindowSize']
    PFS=data['preFilterSize']
    PFC=data['preFilterCap']
    MDS=data['minDisparity']
    NOD=data['numberOfDisparities']
    TTH=data['textureThreshold']
    UR=data['uniquenessRatio']
    SR=data['speckleRange']
    SPWS=data['speckleWindowSize']    
    #sgbm.setSADWindowSize(SWS)
    sgbm.setPreFilterType(1)
    sgbm.setPreFilterSize(PFS)
    sgbm.setPreFilterCap(PFC)
    sgbm.setMinDisparity(MDS)
    sgbm.setNumDisparities(NOD)
    sgbm.setTextureThreshold(TTH)
    sgbm.setUniquenessRatio(UR)
    sgbm.setSpeckleRange(SR)
    sgbm.setSpeckleWindowSize(SPWS)
    f.close()
    print ('Parameters loaded from file '+fName)

load_map_settings ("./StereoVision/3dmap_set.txt")

# capture frames from the camera
while True:
    frameL= cameraL.begin()
    frameR= cameraR.begin()
    frameR = cv2.cvtColor (frameR, cv2.COLOR_BGR2GRAY)
    frameL = cv2.cvtColor (frameL, cv2.COLOR_BGR2GRAY)
    frameR, frameL = calibration.undistortRectify(frameR, frameL)
    disparity = stereo_depth_map(frameR, frameL)
    cv2.imwrite('Depth Map', disparity)
    if cv2.waitKey(1) == ord("q"):
       break
cameraL.stop()
cameraR.stop()
cv2.destroyAllWindows()



#  