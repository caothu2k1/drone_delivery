## Autonomous drone for delivery 

This is the source for my autonomous drone for a simple delivery task project.

It makes use of Stereo Vision from two RPi camera v2 modules for detecting objects with depth using the YOLOv8 model and then uses a subsumption architecture to send control signals via MAVLink to a drone to perform simple delivery missions and avoid obstacles or land automatically on the landing pad.

The full project is intended to run on a Raspberry Pi 5 but should work on any platform connecting to 2 cameras simultaneously and talking via MAVLink.

- INFO: This project is very much a work in progress. It should be functional but be prepared to dive into the code to fix things.
- **WARNING**: I take no responsibility if you run any of this code on your own drone.

### Hardware design

To start this project. Make sure you have enough hardware for your system, and you need to fully connect the hardware components, including setting up and configuring your drone to operate stably. To ensure that the project can continue in the next steps.

- **Reference**: [Ardupilot](https://ardupilot.org/copter/docs/initial-setup.html)
- **Setup Software**: [MissionPlanner](https://ardupilot.org/planner/)

Below is my entire design for this project including an overview of the connected hardware and a 3D drawing built on Solidworks software.

- NOTE: The hardware and design can be changed depending on the needs and purposes of your project.
  
    <img src = "/hardware_design.jpg"> 

### Getting Started

First, install the ultralytics package from https://docs.ultralytics.com/guides/raspberry-pi/ into your companion computer (I used Pi5 for this).

Once done, connect the Camera to the Raspberry Pi 5 and try running a simple `python` object detection program with a single camera using the `yolov8.pt` model, You can use another model if there is better performance.

```bash
pip install picamera2 
```
```bash
cd models
python test.py
```

- Next, export the `yolov8.pt` model to NCNN format to achieve better FPS performance on Raspberry Pi 5 by running the following command in your terminal.

  ```bash
  python export_model.py
  ```
  
- And then, continue running the `test.py` with NCNN model `yolov8n_ncnn_model` to test the performance.

### Stereo Vision

Let's start by connecting two Cameras with RPi 5, fixing them and taking pictures of the **Chessboard** at many different angles and positions, do the following:

```bash
cd StereoVision
python StereoVision/chessboard_img.py
```

Once completed, it is necessary to calibrate both cameras from the previously collected images by running the following command:

```bash
python stereo_calibration.py
```

After successfully calibrating the camera, we can check the accuracy of the stereo camera system using the following two methods:

- Depth Map: Let's try out an example **Depth Map** using the **Semi-Global Matching** method, you can run:
  
  ```bash
  python depth_map.py
  ```
  
  - Additionally, you can adjust the **Depth Map** by running the program `tune.py` or adjusting the parameters set in the file `3dmap_set.txt`
  - **Reference**: more information from https://github.com/realizator/stereopi-tutorial or [OpenCV](https://docs.opencv.org/3.4/d2/d85/classcv_1_1StereoSGBM.html)
  
- Distance Mesurement:


    <img src="/StereoVision/results.jpg"/>

### Templates

  <img src="/templates_view.jpg"/>

### Testing
```bash
pip install dronkit
pip install dronekit-sitl 
pip install pymavlink
pip install mavproxy
pip install firebase_admin
pip install retrying
```



