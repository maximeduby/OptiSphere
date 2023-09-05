from PySide6.QtCore import QThread, Signal, QTimer, Slot


class TimelapseThread(QThread):
    tl_signal = Signal(object)
    stop_signal = Signal()

    def __init__(self, cam_thread, delta_time):
        super().__init__()
        self.source = cam_thread
        self.frames = []
        self.running = True
        self.delta_time = delta_time

        self.timer = QTimer(self)
        self.timer.setInterval(1000 * self.delta_time)
        self.timer.timeout.connect(self.get_frame)
        self.timer.start()

        self.stop_signal.connect(self.stop_timer)

    def run(self):
        while self.running:
            if not self.timer.isActive():
                self.timer.start()
        self.stop_signal.emit()
        if self.frames:
            self.tl_signal.emit(self.frames)
        else:
            raise Exception("No frames to create a video")

    @Slot()
    def get_frame(self):
        self.frames.append(self.source.frame)

    @Slot()
    def stop_timer(self):
        self.timer.stop()

