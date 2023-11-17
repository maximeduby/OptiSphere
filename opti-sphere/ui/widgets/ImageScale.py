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
        if self.iv.is_scale_bar_visible and IV.ImageViewer.is_scale_bar_visible:
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
        ratio = min(tuple(i / j for i, j in zip(self.iv.gv.size().toTuple(), self.iv.gv.im_dim)))
        base_length, scale_units = self.format_scale(base / (self.pix2mm * ratio * self.iv.gv.zoom))
        steps = [2, 5, 10, 20, 50, 100, 200, 500, 1000]
        for step in steps:
            if base_length < step:
                scale_value, scale_units = (1, "mm") if step == 1000 else (step, scale_units)
                scale_length = base * step / base_length
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
