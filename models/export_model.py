from ultralytics import YOLO

# Load a YOLOv8n PyTorch model
model = YOLO("./models/bestYolov8.pt")
# Export the model to NCNN format
model.export(format="ncnn", imgsz = 416)  # creates 'yolov8n_ncnn_model'
