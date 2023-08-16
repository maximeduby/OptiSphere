from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem


class CameraFeed(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.zoom = 1
        self.scene = QGraphicsScene(self)
        self.feed = QGraphicsPixmapItem()
        self.scene.addItem(self.feed)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = event.angleDelta().y() / 1800
        new_zoom = min(5, max(1, self.zoom + zoom_factor))  # zoom between [1, 5]
        scale_factor = new_zoom/self.zoom
        self.scale(scale_factor, scale_factor)
        self.zoom = new_zoom
        if self.zoom == 1.0:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
