import os
import shutil

import cv2
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QFileDialog

from ui.tabs.Tab import Tab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.Rotation3DRender import Rotation3DRender
from ui.widgets.ScanWidget import ScanWidget
from ui.widgets.TrackWidget import TrackWidget


class TrackTab(Tab):
    def __init__(self, track, title, info):
        super().__init__()
        # self.layout().setAlignment(Qt.Alignment.AlignCenter)
        self.track = track
        self.title = title
        self.info = info

        self.spatial_tracking = Rotation3DRender(tracking_mode=True)

        self.track_widget = TrackWidget(self)

        self.scene_layout.addWidget(self.spatial_tracking)
        self.sidebar_layout.addWidget(self.track_widget)
        print(self.track)

    def save(self):
        location = QFileDialog.getExistingDirectory(None, "Choose Location")
        new_directory = os.path.join(location, self.title)
        old_directory = os.path.join("recovery", self.info[0])
        shutil.move(old_directory, new_directory)

