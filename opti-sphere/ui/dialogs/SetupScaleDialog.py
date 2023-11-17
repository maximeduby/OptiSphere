from PySide6.QtCore import Qt, QLineF, QRectF
from PySide6.QtGui import QIcon, QPen, QPainter
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDoubleSpinBox, QComboBox, \
    QGraphicsItem
from ui.widgets.ImageViewer import ImageViewer


class SetupScaleDialog(QDialog):  # window to set the scale ratio (pixel per mm)
    def __init__(self, frame):
        super().__init__()
        self.setFixedSize(900, 700)
        self.setWindowTitle("Setup Scale Bar")
        self.setCursor(Qt.CursorShape.ArrowCursor)

        layout = QVBoxLayout()
        self.save_button = QPushButton('Save', objectName="accept-btn")
        self.save_button.setMinimumWidth(80)
        self.save_button.setEnabled(False)
        cancel_button = QPushButton('Cancel', objectName="reject-btn")
        cancel_button.setMinimumWidth(80)
        self.instrument_button = QPushButton(icon=QIcon("resources/icons/rulers-icon.svg"), objectName="icon-btn")
        length_legend = QLabel(text="Value", objectName="legend")
        self.length_spinbox = QDoubleSpinBox()
        self.length_spinbox.setMinimum(0)
        self.length_spinbox.setMaximum(1000)
        self.length_spinbox.setValue(4)
        self.length_spinbox.setDecimals(3)
        self.length_units = QComboBox()
        self.length_units.addItems(["mm", "µm", "nm", "pm"])
        self.length_units.view().parentWidget().setStyleSheet(
            'background-color: #151415; border-radius: 5px; padding: 1px 0px;')
        self.length_units.update()

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.instrument_button)
        bottom_layout.addWidget(length_legend)
        bottom_layout.addWidget(self.length_spinbox)
        bottom_layout.addWidget(self.length_units)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(cancel_button)
        self.iv = ImageViewer()
        self.iv.gv.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.iv.gv.max_zoom = 1
        self.iv.gv.set_image(frame)
        self.iv.is_scale_bar_visible = False
        self.iv.gv.update()

        layout.addWidget(self.iv)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.reject)
        self.instrument_button.clicked.connect(self.measure)

        self.ruler_start = None
        self.ruler = None
        self.ruler_length = None

    def save(self):  # save values
        self.accept()

    def get_ratio(self):  # return the number of pixels per mm (pixels of the image not the screen)
        if not self.ruler_length:
            return 0
        return self.ruler_length / (self.length_spinbox.value() / 10**(self.length_units.currentIndex()*3))

    def measure(self):  # start the measurement on the image
        self.instrument_button.setFocus()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.iv.is_measuring = True

    def mousePressEvent(self, event):
        if self.iv.underMouse() and self.iv.is_measuring:
            if self.ruler:
                self.iv.gv.scene.removeItem(self.ruler)
                self.ruler = None
            self.ruler_start = self.iv.gv.image.mapToItem(self.iv.gv.image, self.iv.gv.mapToScene(event.pos()))
            self.ruler = RulerItem(self.ruler_start, self.ruler_start)
            self.iv.gv.scene.addItem(self.ruler)

    def mouseMoveEvent(self, event):
        if self.iv.underMouse() and self.iv.is_measuring and self.ruler and self.ruler_start:
            p = self.iv.gv.image.mapToItem(self.iv.gv.image, self.iv.gv.mapToScene(event.pos()))
            self.ruler.update_end(p)

    def mouseReleaseEvent(self, event):
        if self.iv.underMouse() and self.iv.is_measuring and self.ruler:
            self.iv.is_measuring = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.ruler_length = self.ruler.length()
            self.instrument_button.clearFocus()
            self.save_button.setEnabled(True)


class RulerItem(QGraphicsItem):  # line drawn when selecting distance on the image
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end

    def boundingRect(self):
        rect = QRectF(self.start, self.end).normalized()
        rect.adjust(-10, -10, 10, 10)
        return rect

    def length(self):  # return the length of the line drawn
        return QLineF(self.start, self.end).length()

    def update_end(self, p):  # update the end position of the line drawn
        self.end = p
        self.prepareGeometryChange()
        self.update()

    def paint(self, painter, option, widget=...):
        pen = QPen(Qt.red, 6.0, Qt.PenStyle.DashDotLine)
        painter.setPen(pen)
        painter.drawEllipse(self.start, 2, 2)
        painter.drawLine(self.start, self.end)
        painter.drawEllipse(self.end, 2, 2)

