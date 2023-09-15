import cv2
from PySide6.QtWidgets import QFileDialog

from ui.tabs.Tab import Tab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.SnapshotWidget import SnapshotWidget


class SnapshotTab(Tab):
    def __init__(self, frame, title):
        super().__init__()
        self.frame = frame
        self.title = title

        self.snapshot = ImageViewer()
        self.snapshot.set_image(self.frame)

        self.ss_widget = SnapshotWidget(self)

        self.scene_layout.addWidget(self.snapshot)
        self.sidebar_layout.addWidget(self.ss_widget)

    def save(self):
        filename = QFileDialog.getSaveFileName(None, "Save Image", self.title, "Image (*.jpg *.png)")
        if filename[0] == '':
            return
        cv2.imwrite(filename[0], self.frame)

    def get_dimensions(self):
        w = self.frame.shape[1]
        h = self.frame.shape[0]
        return f"{w} × {h}"
