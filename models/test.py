import cv2
from ultralytics import YOLO
import sys
sys.path.insert(0, './StereoVision')
from camera import Picam
# Initialize the Picamera2
camera = Picam()
# Load the YOLOv8 model
model = YOLO("./models/yolov8n_ncnn_model")
while True:
    # Capture frame-by-frame
    frame = camera.begin()
    # Run YOLOv8 inference on the frame
    results = model(frame, imgsz=(416, 416))
    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Display the resulting frame
    cv2.imshow("Camera", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) == ord("q"):
        break
# Release resources and close windows
cv2.destroyAllWindows()