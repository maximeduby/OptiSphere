from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout

from ui.widgets.CaptureWidget import CaptureWidget


class SidebarLayout(QVBoxLayout):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.capture = CaptureWidget(self.wnd)
        self.addWidget(self.capture)
        self.update_sidebar(0)

    @Slot()
    def update_sidebar(self, index):
        current_tab = self.wnd.tabs.widget(index).__class__.__name__
        match current_tab:
            case "CameraTab":
                self.capture.show()
            case "SnapshotTab":
                self.capture.hide()
