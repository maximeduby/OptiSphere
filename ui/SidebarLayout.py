from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.widgets.CaptureWidget import CaptureWidget


class SidebarLayout(QVBoxLayout):
    def __init__(self, tabs):
        super().__init__()
        self.tabs = tabs
        self.capture = CaptureWidget(self.tabs)
        self.addWidget(self.capture)
        self.update_sidebar(0)

    @Slot()
    def update_sidebar(self, index):
        # for i in reversed(range(self.count())):
        #     self.itemAt(i).widget().setParent(None)

        current_tab = self.tabs.widget(index).__class__.__name__
        match current_tab:
            case "CameraTab":
                self.capture.show()
            case "SnapshotTab":
                print("SnapshotTab")
                self.capture.hide()