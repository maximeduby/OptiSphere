from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QStackedLayout, QWidget

from ui.widgets.CustomGraphicsView import CustomGraphicsView
from ui.widgets.ImageScale import ImageScale


class ImageViewer(QWidget):  # image renderer
    box_signal = Signal(tuple)
    is_scale_bar_visible = False

    def __init__(self):
        super().__init__()

        layout = QStackedLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStackingMode(QStackedLayout.StackAll)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.gv = CustomGraphicsView(self)
        self.image_scale = ImageScale(self)

        layout.addWidget(self.gv)
        layout.addWidget(self.image_scale)
        self.setLayout(layout)

    @classmethod
    def toggle_scale_bar(cls, v):
        cls.is_scale_bar_visible = v

    def wheelEvent(self, event):
        self.gv.wheelEvent(event)

    def mousePressEvent(self, event):
        self.gv.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.gv.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.gv.mouseReleaseEvent(event)
