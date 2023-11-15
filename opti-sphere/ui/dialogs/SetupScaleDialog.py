from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDoubleSpinBox, QComboBox

from ui.widgets.CustomGraphicsView import CustomGraphicsView
from ui.widgets.ImageViewer import ImageViewer


class SetupScaleDialog(QDialog):
    def __init__(self, frame):
        super().__init__()
        self.setFixedSize(900, 700)
        self.setWindowTitle("Setup Scale Bar")

        self.pix2mm = 0
        layout = QVBoxLayout()
        self.save_button = QPushButton('Save', objectName="accept-btn")
        self.save_button.setMinimumWidth(80)
        self.save_button.setEnabled(False)
        cancel_button = QPushButton('Cancel', objectName="reject-btn")
        cancel_button.setMinimumWidth(80)
        instrument_button = QPushButton(icon=QIcon("resources/icons/rulers-icon.svg"), objectName="icon-btn")
        length_legend = QLabel(text="Value", objectName="legend")
        length_spinbox = QDoubleSpinBox()
        length_spinbox.setMinimum(0)
        length_spinbox.setMaximum(1000)
        length_spinbox.setValue(4)
        length_spinbox.setDecimals(3)
        length_units = QComboBox()
        length_units.addItems(["mm", "µm", "nm", "pm"])
        length_units.view().parentWidget().setStyleSheet(
            'background-color: #151415; border-radius: 5px; padding: 1px 0px;')
        length_units.update()

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(instrument_button)
        bottom_layout.addWidget(length_legend)
        bottom_layout.addWidget(length_spinbox)
        bottom_layout.addWidget(length_units)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(cancel_button)
        iv = ImageViewer()
        iv.gv.max_zoom = 1
        iv.gv.set_image(frame)
        iv.is_scale_bar_visible = False
        iv.gv.update()

        layout.addWidget(iv)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save())
        cancel_button.clicked.connect(self.reject)

    def save(self):
        self.accept()