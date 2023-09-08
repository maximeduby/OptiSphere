from PySide6.QtWidgets import QWidget


class TrackingTab(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
