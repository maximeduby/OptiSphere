import os
import shutil

from PySide6.QtWidgets import QFileDialog

from ui.tabs.Tab import Tab
from ui.widgets.Rotation3DRender import Rotation3DRender
from ui.widgets.TrackWidget import TrackWidget


class TrackTab(Tab):
    def __init__(self, track, title, info):
        super().__init__()
        self.track = track
        self.title = title
        self.info = info

        self.spatial_tracking = Rotation3DRender(tracking_mode=True)  # 3D render of sphere with track path drawn on it
        self.spatial_tracking.tracking_path = track

        self.track_widget = TrackWidget(self)  # sidebar widget

        self.scene_layout.addWidget(self.spatial_tracking)
        self.sidebar_layout.addWidget(self.track_widget)

    def export(self):  # export scan to chosen location
        location = QFileDialog.getExistingDirectory(None, "Choose Location")
        new_directory = os.path.join(location, self.title)
        old_directory = os.path.join("recovery", self.info[0])
        shutil.move(old_directory, new_directory)

