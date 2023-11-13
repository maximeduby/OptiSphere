from PySide6.QtCore import QThread, Signal


class SnapshotThread(QThread):
    ss_signal = Signal(object)

    def __init__(self, cam_thread):
        super().__init__()
        self.source = cam_thread

    def run(self):  # get the frame from camera feed and send it to new SnapshotTab
        frame = self.source.frame
        if frame is not None:
            self.ss_signal.emit(frame)
        else:
            raise Exception("Could not get the frame for Snapshot")
