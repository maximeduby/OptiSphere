import cv2

from PySide6.QtCore import Qt, Slot, QRect, QSize, Signal
from PySide6.QtGui import QWheelEvent, QImage, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame, QRubberBand, \
    QStackedLayout, QWidget


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

    def toggle_scale(self):
        self.image_scale.setVisible(not self.image_scale.isVisible())


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
        if ImageViewer.is_scale_bar_visible:
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


class CustomGraphicsView(QGraphicsView):
    def __init__(self, iv):
        super().__init__()
        self.iv = iv
        self.zoom = 1
        self.max_zoom = 5
        self.scene = QGraphicsScene(self)

        # to remove
        self.setBackgroundBrush(Qt.yellow)

        self.image = QGraphicsPixmapItem()
        self.scene.addItem(self.image)
        self.setScene(self.scene)
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
        print(self.zoom)
        if self.zoom == 1.0:  # disable dragging when zoom is 1.0 (default)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
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
        self.image.setPixmap(QPixmap.fromImage(image))
        self.image.setScale(min(
            self.size().width() / image.size().width(),
            self.size().height() / image.size().height()))

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
            print(f"Coordinates: ({int(event.x()/self.image.scale())}, {int(event.y()/self.image.scale())})")

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
        self.update()
