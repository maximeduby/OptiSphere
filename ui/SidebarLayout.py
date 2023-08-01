from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout

from ui.widgets.CaptureWidget import CaptureWidget
from ui.widgets.SnapshotWidget import SnapshotWidget


class SidebarLayout(QVBoxLayout):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.capture = CaptureWidget(self.wnd)
        self.addWidget(self.capture)
        self.update_sidebar(0)

        self.ss_widget = None
        self.vid_widget = None
        self.tl_widget = None

    @Slot()
    def update_sidebar(self, index):
        current_tab = self.wnd.tabs.widget(index).__class__.__name__
        match current_tab:
            case "CameraTab":
                for i in range(self.count()):
                    self.itemAt(i).widget().hide()
                self.capture.show()
            case "SnapshotTab":
                for i in range(self.count()):
                    self.itemAt(i).widget().hide()
                self.ss_widget = SnapshotWidget(self.wnd.tabs.widget(index), self.wnd, index)
                self.addWidget(self.ss_widget)
            case "VideoTab":
                for i in range(self.count()):
                    self.itemAt(i).widget().hide()