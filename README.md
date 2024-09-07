## Autonomous drone for delivery 
This is the source for my autonomous drone for a simple delivery task project.

It makes use of Stereo Vision from two RPi camera v2 modules for detecting people with depth using the YOLOv8 model and then uses a subsumption architecture to send control signals
via MAVLink to a drone to perform simple delivery missions and avoid obstacles or land automatically on the landing pad.

The full project is intended to run on a Raspberry Pi 5 but should work on any platform that can talk via MAVLink.

- INFO: This project is very much a work in progress. It should be functional but be prepared to dive into the code to fix things.
- **WARNING**: I take no responsibility if you run any of this code on your own drone. You do so at your own risk.
### Hardware design
<img src = "/hardware_and_3D_design.jpg"> 

### Getting Started
First, install the ultralytics package from https://docs.ultralytics.com/guides/raspberry-pi/ into your environment.

In the next step, you need to install dependency packages on your environment. In the first, open your terminal and run:
```bash
pip install picamera2 
pip install dronkit
pip install dronekit-sitl 
pip install pymavlink
pip install mavproxy
pip install firebase_admin
pip install retrying
pip install matplotlib
```
### Object detection Using YOLOv8 
Let's start testing the YOLOv8 object detection model with a single camera.

First, export the YOLOv8 model in NCNN format with pretty good FPS.
```bash
cd models
python export_model.py
```
Next, run the `test.py` file to test
```bash
cd models
python test.py
```
### Stereo Vision
<img src = "/StereoVision/SGBM.jpg"> 

### Distance measurement
<img src="/StereoVision/results.jpg"/>

### Templates
<img src="/templates_view.jpg"/>



