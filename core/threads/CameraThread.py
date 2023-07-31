import cv2
from PySide6.QtCore import QThread, Signal


class CameraThread(QThread):
    cam_signal = Signal(object)

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.running = True

    def run(self):
        cam = cv2.VideoCapture(self.device_id)
        while self.running:
            ret, frame = cam.read()
            if ret:
                self.cam_signal.emit(frame)
        cam.release()

    def stop(self):
        self.running = False
        self.wait()
