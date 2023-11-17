from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QStackedLayout, QWidget

from ui.widgets.CustomGraphicsView import CustomGraphicsView
from ui.widgets.ImageScale import ImageScale


class ImageViewer(QWidget):  # image renderer
    box_signal = Signal(tuple)
    is_scale_bar_visible = False

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QStackedLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStackingMode(QStackedLayout.StackAll)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.gv = CustomGraphicsView(self)
        self.image_scale = ImageScale(self)

        layout.addWidget(self.gv)
        layout.addWidget(self.image_scale)
        self.setLayout(layout)

        self.is_measuring = False
        self.measure_pos = (-1, -1)

    @classmethod
    def toggle_scale_bar(cls, v):  #show/hide the scale bar
        cls.is_scale_bar_visible = v

    def wheelEvent(self, event):
        self.gv.wheelEvent(event)

    def mousePressEvent(self, event):
        if self.is_measuring:
            self.parent().mousePressEvent(event)
        else:
            self.gv.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_measuring:
            self.parent().mouseMoveEvent(event)
        else:
            self.gv.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_measuring:
            self.parent().mouseReleaseEvent(event)
        else:
            self.gv.mouseReleaseEvent(event)