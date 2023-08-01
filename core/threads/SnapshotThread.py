import cv2
from PySide6.QtCore import QThread, Signal


class SnapshotThread(QThread):
    ss_signal = Signal(object)

    def __init__(self, device_index):
        super().__init__()
        self.device_index = device_index
        self.frame = None
        self.cam = cv2.VideoCapture(self.device_index)

    def run(self):
        ret, self.frame = self.cam.read()
        if ret:
            self.ss_signal.emit(self)
        self.cam.release()
