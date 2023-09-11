import cv2
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QWheelEvent, QImage, QPixmap
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 840, 640)
        self.zoom = 1
        self.scene = QGraphicsScene(self)
        self.image = QGraphicsPixmapItem()
        self.scene.addItem(self.image)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = event.angleDelta().y() / 1800
        new_zoom = min(5, max(1, self.zoom + zoom_factor))  # zoom between [1, 5]
        scale_factor = new_zoom / self.zoom
        self.scale(scale_factor, scale_factor)
        self.zoom = new_zoom
        if self.zoom == 1.0:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    @Slot()
    def set_image(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1],  # width
                       frame.shape[0],  # height
                       frame.shape[2] * frame.shape[1],  #
                       QImage.Format.Format_RGB888)  # image format
        self.image.setPixmap(QPixmap.fromImage(image))
        self.image.setScale(min(
            self.size().width() / image.size().width(),
            self.size().height() / image.size().height()))
