import cv2
import random
from ultralytics import YOLO
import random
import numpy as np

class ObjectDectection:

    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.model.names]

    def coordinates(self, right_point, left_point, frame):
        # Stereo camera parameters
        baseline = 6.24  # Distance between the two cameras
        alpha = 62.2     # Field of view of the camera lens in degrees
        frame_height, frame_width, _ = frame.shape
        f_pixel = (frame_width * 0.5) / np.tan(alpha * 0.5 * np.pi / 180)  # Focal length in pixels

        # Extract coordinates from points
        x_right = right_point[0]
        x_left = left_point[0]
        y_right = right_point[1]
        y_left = left_point[1]

        # Calculate disparity
        disparity = x_right - x_left
        if disparity == 0:
            return [0, 0, 0]
        else:
            Z = ((f_pixel * baseline) / disparity) / 100
        # Calculate real-world coordinates (X, Y)
        # Convert pixel coordinates to normalized image coordinates
        x_center = (x_left + x_right) / 2
        y_center = (y_left + y_right) / 2
        x_normalized = (x_center - frame_width / 2) / f_pixel
        y_normalized = (y_center - frame_height / 2) / f_pixel

        # Calculate real-world X and Y coordinates in meters
        X = x_normalized * Z
        Y = y_normalized * Z

        return [X, Y, Z]

    @staticmethod
    def plot_one_box(position, frame, c, color=None, label=None, line_thickness=2):
        # Plots one bounding box on the image frame
        tl = line_thickness or round(0.002 * (frame.shape[0] + frame.shape[1]) / 2) + 1  # line/font thickness
        color = color or [random.randint(0, 255) for _ in range(3)]
        c1, c2 = (int(position[0]), int(position[1])), (int(position[2]), int(position[3]))
        # Draw the bounding box
        cv2.rectangle(frame, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        # Calculate text sizes and positions
        tf = max(tl - 1, 1)  # font thickness
        label_text = f"{label}"
        xyz_texts = [f"X:{c[0]:.2f}", f"Y:{c[1]:.2f}", f"Z:{c[2]:.2f}"]
        
        label_size = cv2.getTextSize(label_text, 0, fontScale=tl / 3, thickness=tf)[0]
        xyz_sizes = [cv2.getTextSize(text, 0, fontScale=tl / 3, thickness=tf)[0] for text in xyz_texts]
        # Draw filled rectangle for the label
        c2_label = c1[0] + label_size[0], c1[1] - label_size[1] - 3
        cv2.rectangle(frame, c1, c2_label, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(frame, label_text, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
        
        # Calculate the starting position for the xyz texts
        y_offset = c1[1] + label_size[1] - 10
        
        # Draw each coordinate on a new line
        for i, xyz_text in enumerate(xyz_texts):
            y_pos = y_offset + (xyz_sizes[i][1] + 10) * (i + 1)
            cv2.putText(frame, xyz_text, (c1[0], y_pos), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    def detect(self, frameR, frameL):
        datalist = []
        resultsR = self.model.predict(frameR,imgsz = (416,416), verbose=False)
        resultsL = self.model.predict(frameL,imgsz = (416,416), verbose=False)
        for r, l in zip(resultsR, resultsL):
            boxesR = r.boxes# Boxes object for bbox outputs
            boxesL = l.boxes# Boxes object for bbox outputs
            for boxR , boxL in zip(boxesR, boxesL):
                if boxR.cls == boxL.cls:
                    xminR, xminL = boxR.data[0][0], boxL.data[0][0]
                    yminR, yminL = boxR.data[0][1], boxL.data[0][1]
                    xmaxR, xmaxL = boxR.data[0][2], boxL.data[0][2]
                    ymaxR, ymaxL = boxR.data[0][3], boxL.data[0][3]
                    # Calculate center coordinates
                    center_point_R = [(xminR + xmaxR) / 2,(yminR + ymaxR) / 2]
                    center_point_R = center_point_R[0].item(), center_point_R[1].item()
                    center_point_L = [(xminL + xmaxL) / 2,(yminL + ymaxL) / 2]
                    center_point_L = center_point_L[0].item(), center_point_L[1].item()
                    c = self.coordinates(center_point_R,center_point_L, frameR)
                    if c[2] > 0 and c[2] < 8:
                        labelR = f"{self.model.names[int(boxR.cls)]}"
                        datalist.append([labelR, c])
                        self.plot_one_box([xminR, yminR, xmaxR, ymaxR], frameR, c, self.colors[int(boxR.cls)], labelR)
                        self.plot_one_box([xminL, yminL, xmaxL, ymaxL], frameL, c, self.colors[int(boxR.cls)], labelR)
        combine = np.hstack((frameL,frameR))
        # return frameR,frameL, datalist
        return combine, datalist
    
       