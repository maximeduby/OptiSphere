import cv2
from PySide6.QtCore import Qt, Slot, QRect, QSize
from PySide6.QtGui import QWheelEvent, QImage, QPixmap
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame, QRubberBand


class CustomGraphicsView(QGraphicsView):
    def __init__(self, iv):
        super().__init__()
        self.iv = iv
        self.zoom = 1
        self.max_zoom = 5
        self.scene = QGraphicsScene(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.im_dim = (1, 1)
        self.image = QGraphicsPixmapItem()
        self.image.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.scene.addItem(self.image)
        self.setScene(self.scene)
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

        self.selection_origin, self.selection_destination = None, None
        self.selection = None
        self.is_selecting, self.selection_mode = False, False

    def wheelEvent(self, event: QWheelEvent):  # zoom on image when mouse wheel triggered
        zoom_factor = event.angleDelta().y() / 1800
        new_zoom = min(self.max_zoom, max(1, self.zoom + zoom_factor))  # zoom between [1, 5]
        scale_factor = new_zoom / self.zoom
        self.scale(scale_factor, scale_factor)
        self.zoom = new_zoom
        if self.zoom == 1.0:  # disable dragging when zoom is 1.0 (default)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.fitInView(self.image.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    @Slot()
    def set_image(self, frame):  # update image with frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # reverse colors order BGR --> RGB
        image = QImage(frame.tostring(),  # frame
                       frame.shape[1],  # width
                       frame.shape[0],  # height
                       frame.shape[2] * frame.shape[1],  # bytes per line
                       QImage.Format.Format_RGB888)  # image format
        self.image.setPixmap(QPixmap.fromImage(image))  # update image
        self.im_dim = (frame.shape[1], frame.shape[0])  # update image dimensions

    def mousePressEvent(self, event):  # triggered when clicking on image
        if self.selection_mode:  # when selecting tracking ROI, draw selection on image
            if self.selection:
                self.selection.hide()
            self.is_selecting = True
            self.selection_origin = event.pos()
            self.selection = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self.selection.setGeometry(QRect(self.selection_origin, QSize()))
            self.selection.show()
        else:
            super().mousePressEvent(event)
            print(f"Coordinates: "
                  f"({int(event.x()/(self.image.scale()*self.zoom))}, {int(event.y()/(self.image.scale()*self.zoom))})")

    def mouseMoveEvent(self, event):  # triggered when mouse moves on image
        if self.selection_mode and self.is_selecting and self.selection:
            self.selection_destination = event.pos()
            self.selection.setGeometry(QRect(self.selection_origin, event.pos()).normalized())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # triggered when mouse release click on image
        if self.selection_mode and self.is_selecting and self.selection:
            self.is_selecting = False
            x1 = self.mapToScene(self.selection_origin).x() / self.image.scale()
            y1 = self.mapToScene(self.selection_origin).y() / self.image.scale()
            x2 = self.mapToScene(self.selection_destination).x() / self.image.scale()
            y2 = self.mapToScene(self.selection_destination).y() / self.image.scale()

            box = (  # create tracking box with mouse-selected area
                int(min(x1, x2)),
                int(min(y1, y2)),
                int(abs(x2 - x1)),
                int(abs(y2 - y1))
            )
            if box[2] < 10 or box[3] < 10:
                return
            self.iv.box_signal.emit(box)

        else:
            super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        self.fitInView(self.image.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom = 1
        self.update()

