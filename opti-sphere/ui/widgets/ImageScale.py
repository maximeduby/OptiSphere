from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

import ui.widgets.ImageViewer as IV


class ImageScale(QWidget):
    pix2mm = 0

    def __init__(self, iv):
        super().__init__()
        self.iv = iv

    def wheelEvent(self, event):
        self.iv.wheelEvent(event)

    def mousePressEvent(self, event):
        self.iv.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.iv.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.iv.mouseReleaseEvent(event)

    def paintEvent(self, event):
        if IV.ImageViewer.is_scale_bar_visible:
            painter = QPainter(self)
            color = QColor(255, 0, 0)
            painter.setPen(color)
            x, y = 30, 20
            scale_length, scale_value, scale_units = self.calc_scale()
            painter.drawText(x, y, scale_length, y, Qt.AlignmentFlag.AlignCenter, f"{scale_value}{scale_units}")
            painter.drawLine(x, y + 20, x + scale_length, y + 20)

    def calc_scale(self):
        scale_value, scale_length = 0, 0
        base = 100
        if self.pix2mm == 0:
            return base, "?", "??"
        base_length, scale_units = self.format_scale(base / (self.pix2mm * self.iv.gv.zoom))
        steps = [500, 200, 100, 50, 20, 10, 5, 2, 1]
        for step in steps:
            if base_length > step:
                scale_value = step
                trail = (base_length - step) * base / step
                scale_length = base + trail
                break
        return scale_length, scale_value, scale_units

    @staticmethod
    def format_scale(value):
        if value >= 1:
            return value, "mm"
        elif value >= 0.001:
            return value * 1000, "µm"
        elif value >= 1e-06:
            return value * 1e6, "nm"
        else:
            return value * 1e9, "pm"

