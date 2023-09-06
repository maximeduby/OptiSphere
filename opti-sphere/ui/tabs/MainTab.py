from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTabWidget

from core.threads.CameraThread import CameraThread
from ui.tabs.RotationTab import RotationTab
from ui.tabs.ScanningTab import ScanningTab
from ui.tabs.Tab import Tab
from ui.tabs.TrackingTab import TrackingTab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.CaptureWidget import CaptureWidget


class MainTab(Tab):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.camera_feed = ImageViewer()
        self.capture = CaptureWidget(self.wnd)
        self.control = QTabWidget(objectName="control-tabs")
        self.rotation = RotationTab()
        self.tracking = TrackingTab()
        self.scanning = ScanningTab()

        self.control.tabBar().setDocumentMode(True)
        self.control.tabBar().setExpanding(True)
        self.control.addTab(self.rotation, "Rotation")
        self.control.addTab(self.tracking, "Tracking")
        self.control.addTab(self.scanning, "Scanning")

        self.scene_layout.addWidget(self.camera_feed)
        self.sidebar_layout.addWidget(self.capture)
        self.sidebar_layout.addWidget(self.control)

        self.th = CameraThread(0)
        self.th.cam_signal.connect(self.camera_feed.set_image)
        self.th.start()

    @Slot()
    def select_camera_source(self):
        device_index = self.wnd.cam_devices_group.checkedAction().data()
        self.th.stop()
        self.th = CameraThread(device_index)
        self.th.cam_signal.connect(self.camera_feed.set_image)
        self.th.start()
