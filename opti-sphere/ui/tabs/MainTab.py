from PySide6.QtCore import Slot

from core.threads.CameraThread import CameraThread
from ui.tabs.Tab import Tab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.CaptureWidget import CaptureWidget


class MainTab(Tab):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.camera_feed = ImageViewer()
        self.capture = CaptureWidget(self.wnd)

        self.scene_layout.addWidget(self.camera_feed)
        self.sidebar_layout.addWidget(self.capture)

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
