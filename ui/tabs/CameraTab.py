import cv2
from PySide6.QtCore import Slot, Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout

from core.threads.CameraThread import CameraThread


class CameraTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window

        # camera label (widget)
        self.camera = QLabel(self)
        self.camera.setAlignment(Qt.AlignCenter)

        # camera layout
        self.cam_layout = QVBoxLayout()
        self.cam_layout.addWidget(self.camera)
        self.setLayout(self.cam_layout)

        # Thread in charge of updating the image
        self.th = CameraThread(0)
        self.th.cam_signal.connect(self.update_frame)
        self.th.start()

    @Slot()
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = image.scaled(800, 800, Qt.KeepAspectRatio)
        print(self.cam_layout.sizeHint())
        self.camera.setPixmap(QPixmap.fromImage(image))

    @Slot()
    def select_camera(self):
        device_index = self.window.cam_devices_group.checkedAction().data()

        # stop the previous camera thread and create a new one with the selected device index
        self.th.stop()
        self.th = CameraThread(device_index)
        self.th.cam_signal.connect(self.update_frame)
        self.th.start()