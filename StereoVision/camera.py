from picamera2 import Picamera2
import cv2

class Picam:
    def __init__(self, camera_id=1):
        self.camera = Picamera2(camera_id)
        self.camera.configure(self.camera.create_preview_configuration(main={"format": 'RGB888', "size": (1280, 960)}))
        self.camera.start()

    def begin(self, size = (640,480)):
        frame = self.camera.capture_array()
        return cv2.resize(frame, size)
    def stop(self):
        self.camera.stop()