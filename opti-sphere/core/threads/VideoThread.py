from PySide6.QtCore import QThread, Signal, QTimer, Slot


class VideoThread(QThread):
    vid_signal = Signal(object)
    stop_signal = Signal()

    def __init__(self, cam_thread, threads):
        super().__init__()
        self.source = cam_thread
        self.threads = threads
        self.frames = []
        self.running = True

        self.timer = QTimer()  # timer interval between to frames' capture
        self.timer.setInterval(1000/self.source.fps)
        self.timer.timeout.connect(self.get_frame)
        self.timer.start()

        self.stop_signal.connect(self.stop_timer)

    def run(self):
        self.threads.append(self)
        while self.running:
            if not self.timer.isActive():
                self.timer.start()
        self.stop_signal.emit()
        if self.frames:
            self.vid_signal.emit(self.frames)
        else:
            raise Exception("No frames to create a video")
        self.threads.remove(self)

    @Slot()
    def get_frame(self):  # add current camera feed frame to video frames
        self.frames.append(self.source.frame)

    @Slot()
    def stop_timer(self):
        self.timer.stop()

    def stop(self):
        self.running = False
        self.timer.stop()
        self.wait()
