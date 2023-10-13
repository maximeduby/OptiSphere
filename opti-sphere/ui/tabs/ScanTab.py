import os
import shutil

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QFileDialog

from ui.tabs.Tab import Tab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.ScanWidget import ScanWidget


class ScanTab(Tab):
    def __init__(self, frames, title, info):
        super().__init__()
        self.layout().setAlignment(Qt.Alignment.AlignCenter)
        self.frames = frames
        self.title = title
        self.info = info

        self.current_frame = 0

        self.scan = ImageViewer()
        self.scan.set_image(self.frames[self.current_frame])

        scan_control = QWidget(objectName="widget-container")
        scan_control_layout = QHBoxLayout()
        self.index = QLabel(text="Frame 0", objectName='timestamp')
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.set_frame)
        self.slider.setRange(0, len(self.frames) - 1)
        scan_control_layout.addWidget(self.index)
        scan_control_layout.addWidget(self.slider)
        scan_control.setLayout(scan_control_layout)

        self.scan_widget = ScanWidget(self)

        self.scene_layout.addWidget(self.scan)
        self.scene_layout.addWidget(scan_control)
        self.sidebar_layout.addWidget(self.scan_widget)

    @Slot()
    def set_frame(self, value):
        self.current_frame = value
        self.scan.set_image(self.frames[self.current_frame])
        self.index.setText(f"Frame {self.current_frame}")

    def get_dimensions(self):
        vid_height, vid_width, _ = self.frames[0].shape
        dim = f"{vid_width} × {vid_height}"
        return dim

    def save(self):
        location = QFileDialog.getExistingDirectory(None, "Choose Location")
        new_directory = os.path.join(location, self.title)
        old_directory = os.path.join("recovery", self.info[0])
        shutil.move(old_directory, new_directory)

