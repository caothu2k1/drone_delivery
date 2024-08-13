## Autonomous drone for delivery 
This is the source for my autonomous drone for for a simple delivery task project.

It makes use Stereo Vision from two RPi camera v2 module for detecting people with depth using YOLOv8 model, and then uses a subsumption architecture to send control signals
via MAVLink to a drone to perform simple delivery missions and avoid obstacles or land automatically on the landing pad.

The full project is intended to run on an Raspberry Pi 5, but should work on any platform that can talk via MAVLink.

- INFO: This project is very much work-in-progress. It should be functional, but be prepared to dive into the code to fix things.
- **WARNING**: I take no responsibility if you run any of this code on your own drone. You do so at your own risk.

### Getting Started
First, install the ultralytics package from https://docs.ultralytics.com/guides/raspberry-pi/ into your environment.

Next step, you need to install dependency packages on your environment.In the first, open your termial and run:
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

First, export the YOLOv8 model in NCNN format, a format with pretty good FPS.
```bash
python models/export_model.py
```
Next, run the `test.py` file to test
```bash
python models/test.py
```
### Stereo Vision
<img src = "https://github.com/caothu2k1/drone_delivery/blob/master/StereoVision%2FSGBM.jpg">

### Distance measurement 
<img src="/Documentation/images/preview_proot.jpg"/> | <img src="/Documentation/images/preview_native.jpg"/>| <img src="/Documentation/images/preview_chroot.jpg"/>


