import cv2

from PySide6.QtCore import Slot, Qt, Signal
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import QTabWidget

from core.threads.CameraThread import CameraThread
from ui.tabs.RotationTab import RotationTab
from ui.tabs.ScanningTab import ScanningTab
from ui.tabs.Tab import Tab
from ui.tabs.TrackingTab import TrackingTab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.CaptureWidget import CaptureWidget


class MainTab(Tab):
    box_signal = Signal(tuple)
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.camera_feed = ImageViewer()
        self.capture = CaptureWidget(self.wnd)
        self.control = QTabWidget(objectName="control-tabs")
        self.rotation = RotationTab(self.wnd)
        self.tracking = TrackingTab(self.wnd)
        self.scanning = ScanningTab(self.wnd)

        self.control.addTab(self.rotation, "Rotation")
        self.control.addTab(self.tracking, "Tracking")
        self.control.addTab(self.scanning, "Scanning")

        self.scene_layout.addWidget(self.camera_feed)
        self.sidebar_layout.addWidget(self.capture)
        self.sidebar_layout.addWidget(self.control)

        self.th = CameraThread(0, self.wnd.threads)
        self.th.cam_signal.connect(self.handle_camera_feed)
        self.th.start()

        self.is_tracking_on = False
        self.tracker = None
        self.selection_origin, self.selection_destination, self.selection, self.is_selecting = None, None, None, False
        QShortcut(Qt.Key.Key_Escape, self, self.release_tracking)

    @Slot()
    def select_camera_source(self):
        device_index = self.wnd.cam_devices_group.checkedAction().data()
        self.th.stop()
        self.th = CameraThread(device_index, self.wnd.threads)
        self.th.cam_signal.connect(self.handle_camera_feed)
        self.th.start()

    @Slot()
    def handle_camera_feed(self, frame):
        if self.is_tracking_on:
            ok, box = self.tracker.update(frame)
            if ok:
                self.box_signal.emit(box)
                cv2.rectangle(
                    frame,
                    (int(box[0]), int(box[1])),
                    (int(box[0] + box[2]), int(box[1] + box[3])),
                    (255, 255, 0),
                    8,
                    2
                )

        self.camera_feed.set_image(frame)

    def release_tracking(self):
        if self.is_tracking_on:
            self.tracking.init_tracking()
        if self.camera_feed.selection_mode:
            self.tracking.roi_selection()

    def set_action(self, action):
        if action == "rotation":
            self.tracking.setEnabled(False)
            self.scanning.setEnabled(False)
        elif action == "tracking":
            self.rotation.setEnabled(False)
            self.scanning.setEnabled(False)
        elif action == "scanning":
            self.rotation.setEnabled(False)
            self.tracking.setEnabled(False)
        elif action == "none":
            self.rotation.setEnabled(True)
            self.tracking.setEnabled(True)
            self.scanning.setEnabled(True)
