import cv2
from PySide6.QtCore import Slot, Qt, QRect, QPointF
from PySide6.QtGui import QImage, QPixmap, QWheelEvent
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout

from core.threads.CameraThread import CameraThread


class CameraTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window

        # camera label (widget)
        self.camera = QLabel(self)
        self.camera.setAlignment(Qt.AlignCenter)
        self.camera.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mouse_pos = QPointF(self.camera.size().width()/2, self.camera.size().height()/2)
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
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1], QImage.Format_RGB888)
        image = image.scaled(self.camera.size(), Qt.KeepAspectRatio)
        self.camera.setPixmap(QPixmap.fromImage(image))

    @Slot()
    def select_camera(self):
        device_index = self.window.cam_devices_group.checkedAction().data()
        self.window.sidebar_layout.capture.device_index = device_index
        # stop the previous camera thread and create a new one with the selected device index
        self.th.stop()
        self.th = CameraThread(device_index)
        self.th.cam_signal.connect(self.update_frame)
        self.th.start()

    def save(self):
        pass

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.camera.underMouse():
            zoom_factor = event.angleDelta().y()/1800
            self.th.zoom = min(5, max(1, self.th.zoom + zoom_factor)) # zoom between [1, 5]
            print(f"Zoom: {self.th.zoom}")
            self.th.mouse = (
                event.position().x()/self.camera.size().width(),
                event.position().y()/self.camera.size().height()
            )
