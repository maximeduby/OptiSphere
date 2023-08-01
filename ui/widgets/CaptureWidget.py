from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from configuration import ROOT_DIR
from core.threads.SnapshotThread import SnapshotThread
from ui.widgets.CaptureButton import CaptureButton


class CaptureWidget(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.device_index = 0
        self.wnd = wnd

        layout = QVBoxLayout()

        section_header = QLabel("Capture")
        h_layout = QHBoxLayout()

        self.ss_btn = CaptureButton(self, "Snapshot", "snapshot_icon.png")
        self.vid_btn = CaptureButton(self, 'Video', "video_icon.png")
        self.tl_btn = CaptureButton(self, 'Timelapse', "timelapse_icon.png")

        h_layout.addWidget(self.ss_btn)
        h_layout.addWidget(self.vid_btn)
        h_layout.addWidget(self.tl_btn)

        layout.addWidget(section_header)
        layout.addLayout(h_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def capture(self, btn, capture_type):
        btn.setEnabled(False)
        match capture_type:
            case "Snapshot":
                th = SnapshotThread(self.device_index)
                th.ss_signal.connect(self.wnd.add_tab)
                th.start()
                th.wait()
                btn.setEnabled(True)
