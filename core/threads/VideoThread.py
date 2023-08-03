import cv2
from PySide6.QtCore import QThread, Signal


class VideoThread(QThread):
    vid_signal = Signal(object)
    def __init__(self, device_index, fps , counter):
        super().__init__()
        self.device_index = device_index
        self.cam = cv2.VideoCapture(self.device_index)
        self.running = True
        self.recorded_frames = []

    def run(self) -> None:
        while self.running:
            ret, frame = self.cam.read()
            if not ret:
                break
            self.recorded_frames.append(frame)
        self.vid_signal.emit(self)
        self.cam.release()

