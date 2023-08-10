import cv2
from PySide6.QtCore import QThread, Signal, QTimer, Slot


class TimelapseThread(QThread):
    tl_signal = Signal(object)

    def __init__(self, device_index, delta_time, duration, counter):
        super().__init__()
        self.device_index = device_index
        self.cam = cv2.VideoCapture(self.device_index)
        self.running = True
        self.recorded_frames = []
        self.delta_time = delta_time
        self.duration = duration

    def run(self) -> None:
        delta_timer = QTimer(self)
        delta_timer.setInterval(1000 * self.delta_time)
        delta_timer.start()
        while self.running:
            ret, frame = self.cam.read()
            if not ret:
                break
            if delta_timer.remainingTime() == 0:
                self.recorded_frames.append(frame)
                delta_timer.start()

        self.tl_signal.emit(self)
        self.cam.release()

    @Slot()
    def end_tl(self):
        self.running = False
        self.wait()
