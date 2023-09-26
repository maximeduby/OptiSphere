import cv2
from PySide6.QtCore import QThread, Signal


class CameraThread(QThread):
    cam_signal = Signal(object)

    def __init__(self, device_id, threads):
        super().__init__()
        self.device_id = device_id
        self.running = True
        self.frame = None
        self.fps = 30
        self.threads = threads

    def run(self):
        self.threads.append(self)
        cam = cv2.VideoCapture(self.device_id)
        self.fps = int(cam.get(5))
        while self.running:
            ret, self.frame = cam.read()
            if ret:
                self.cam_signal.emit(self.frame)
        cam.release()
        self.threads.remove(self)

    def stop(self):
        self.running = False
        self.wait()
