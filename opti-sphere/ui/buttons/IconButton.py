from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QPushButton




class IconButton(QPushButton):
    def __init__(self, icon_path):
        super().__init__()
        self.icon_path = icon_path
        self.set_icon_color("#FFFFFF")

    def set_icon_color(self, color):
        renderer = QSvgRenderer(self.icon_path)
        aspect_ratio = renderer.viewBox().size().width() / renderer.viewBox().size().height()

        pixmap_width = self.width()
        pixmap_height = int(pixmap_width / aspect_ratio)

        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        renderer.render(painter, QRectF(0, 0, pixmap_width, pixmap_height))
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()

        icon = QIcon(pixmap)
        self.setIcon(icon)
