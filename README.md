## Autonomous drone for delivery 

This is the source for my autonomous drone for a simple delivery task project.

It makes use of Stereo Vision from two RPi camera v2 modules for detecting objects with depth using the YOLOv8 model and then uses a subsumption architecture to send control signals via **MAVLink** to a drone to perform simple delivery missions and avoid obstacles or land automatically on the landing pad.

The full project is intended to run on a Raspberry Pi 5 but should work on any platform connecting to 2 cameras simultaneously and talking via **MAVLink**.

- INFO: This project was built in 6 months, it includes many stages and complex knowledge. But basically, it works well, and be prepared with enough knowledge to dive into the code and fix things.
- **WARNING**: I take no responsibility for  any problems if you run any of this code on your own drone. You need to have everything ready to avoid dangerous situations

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
  
- To test the performance, continue running the `test.py` with NCNN model `yolov8n_ncnn_model`.

### Stereo Vision

Let's start by connecting two Cameras with **RPi 5**, fixing them, and taking pictures of the **Chessboard** at many different angles and positions, do the following:

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
  
  - Additionally, you can adjust the **Depth Map** by running the program `tune.py` or changing the parameters set in the file `3dmap_set.txt`
  - **Reference**: more information from https://github.com/realizator/stereopi-tutorial or [OpenCV](https://docs.opencv.org/3.4/d2/d85/classcv_1_1StereoSGBM.html)
  
- Distance Measurement: Now, let's try measuring the distance of objects using the `yolov8n.pt` or `yolov8n_ncnn_model` model with a simple program, you can run.

  ```bash
  cd camera
  python test.py
  ```
Below are the results obtained from the stereo camera in this project, including building a difference map and measuring the actual distance of the landing_pad at each different distance.

<img src="/StereoVision/results.jpg"/>

### Templates

Instead of using a Ground Station Control like [MissionPlanner](https://ardupilot.org/planner/), I built a simple control website combined with a **4G IoT** system equipped on the Drone. To connect the Website to your drone, you need to add your **adminsdk** in `your-gcs-gg-firebase-adminsdk.json` and your **API_URL** in `Key_API.py` and install `firebase_admin` library, you can run:

```bash
pip install firebase_admin
pip install retrying
```

We can remotely control drones via the internet, data will be stored and retrieved on the [Firebase](https://firebase.google.com/) Database, Realtime Database parameters are configured in `firbase_parameters_export.json`

Let's enter **GOOGLE_MAP_KEY_API** in `index.html` and **FIREBASE_KEY_API** in `firebase.js`, and open the website on your PC , the website will have the interface as shown below

<img src="/templates_view.jpg"/>

### Simulation

Before starting the actual testing, we need a simulation to make sure all the code works correctly through the `SITL` library and install dependent packages on **RPi 5**:

```bash
pip install dronkit
pip install dronekit-sitl 
pip install pymavlink
pip install mavproxy
```

Then, open [MissionPlanner](https://ardupilot.org/planner/) on your PC and run a simple example `test.py` on **RPi 5**. You need to change your TCP address to connect **RPi 5** to [MissionPlanner](https://ardupilot.org/planner/) in `vehicle = connect('tcp:192.168.1.125:5762', wait_ready=True)` and run:

```bash
cd copter
python test.py
```

Now, Let's open the web console and test the main program, do the following:

```bash
python main.py --vehicle_port your_tcp --model_path /path/to/your/model
```

Set up a flight trajectory, monitor, and control your drone via the website or [MissionPlanner](https://ardupilot.org/planner/). If **SITL** doesn't set mode auto through your code, maybe the problem is resolved [here](https://github.com/ArduPilot/pymavlink/pull/466/commits/b500f5fdf0dad868e554ab80e56c039363e3bfb3):

### Testing

Now, move to a large area to conduct an outdoor test flight.

- **WARNING**: You need to check everything works well before doing this:
  
```bash
python main.py --vehicle_port your_port --model_path /path/to/your/model
```

Below are some outdoor test images from my project.

<img src="/actual_results.jpg"/>

