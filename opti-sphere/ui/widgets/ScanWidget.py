import cv2
import imageio
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog


class ScanWidget(QWidget):
    update_signal = Signal(str)

    def __init__(self, scan):
        super().__init__()
        self.setObjectName("widget-container")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.scan = scan

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 15, 20, 15)

        # header
        header = QLabel(text='Scan', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # scan name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name", objectName="legend")
        self.name = QLineEdit(objectName="name")
        self.name.setPlaceholderText("Enter the scan name")
        self.name.setText(self.scan.title)
        self.name.returnPressed.connect(lambda: self.save_name(self.name.text()))
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # scan details
        details_widget = QWidget(objectName="details")
        details_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        details_layout = QVBoxLayout()
        details_layout_top = QHBoxLayout()
        details_layout_top.setAlignment(Qt.Alignment.AlignCenter)
        details_layout_top.setSpacing(20)
        details_layout_top.setContentsMargins(10, 3, 10, 3)
        details_layout_bottom = QHBoxLayout()
        details_layout_bottom.setAlignment(Qt.Alignment.AlignCenter)
        details_layout_bottom.setSpacing(20)
        details_layout_bottom.setContentsMargins(10, 3, 10, 3)

        dimensions = QLabel(self.scan.get_dimensions())
        frames_amount = QLabel(f"{len(self.scan.frames)} Frames")
        details_layout_top.addWidget(dimensions)
        details_layout_top.addWidget(frames_amount)

        method = QLabel(self.scan.info[1])
        axis = QLabel(f"{self.scan.info[2]} Axis")
        angle = QLabel(f"{self.scan.info[3]}° Delta Angle")
        details_layout_bottom.addWidget(method)
        details_layout_bottom.addWidget(axis)
        details_layout_bottom.addWidget(angle)

        details_layout.addLayout(details_layout_top)
        details_layout.addLayout(details_layout_bottom)
        details_widget.setLayout(details_layout)

        # export to gif button
        export_gif_btn = QPushButton(text="Export GIF", objectName="accept-btn")
        export_gif_btn.clicked.connect(self.export_gif)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addWidget(details_widget)
        layout.addWidget(export_gif_btn)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def save_name(self, new_name):
        self.scan.title = new_name
        self.update_signal.emit(new_name)
        self.name.clearFocus()

    @Slot()
    def export_gif(self):
        filename = QFileDialog.getSaveFileName(None, "Save GIF", self.scan.title, "Image (*.gif)")
        if filename[0] == '':
            return

        with imageio.get_writer(filename[0], mode='I') as writer:
            for frame in self.scan.frames:
                writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

