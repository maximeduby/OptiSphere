import cv2
from PySide6.QtCore import QThread, Signal

from ui.tabs.SnapshotTab import SnapshotTab


class SnapshotThread(QThread):
    ss_signal = Signal(object)
    def __init__(self, device_index, tabs, btn):
        super().__init__()
        self.device_index = device_index
        self.tabs = tabs
        self.btn = btn

    def run(self):
        cam = cv2.VideoCapture(self.device_index)
        ret, frame = cam.read()
        if ret:
            snapshot_tab = SnapshotTab(frame)
            self.tabs.addTab(snapshot_tab, "snapshot1.png")
            snapshot_tab.set_image()
        self.btn.setEnabled(True)
        cam.release()
