from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox


class TimelapseWidget(QWidget):
    def __init__(self, timelapse):
        super().__init__()
        self.timelapse = timelapse

        layout = QVBoxLayout()

        # header
        header = QLabel(text='Timelapse', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # timelapse name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name:", objectName="legend")
        self.name = QLabel(text=self.timelapse.title, objectName="name")
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # timelapse dimensions
        dim_layout = QHBoxLayout()
        dim_legend = QLabel(text="Dimensions:", objectName="legend")
        self.dimensions = QLabel(text=self.timelapse.get_dimensions(), objectName="property")
        dim_layout.addWidget(dim_legend)
        dim_layout.addWidget(self.dimensions)

        # video duration
        dur_layout = QHBoxLayout()
        dur_legend = QLabel(text="Duration:", objectName="legend")
        self.duration = QLabel(text=self.timelapse.get_duration(), objectName="property")
        dur_layout.addWidget(dur_legend)
        dur_layout.addWidget(self.duration)

        # timelapse fps
        fps_layout = QHBoxLayout()
        fps_legend = QLabel(text="FPS:", objectName="legend")
        self.fps = QSpinBox()
        self.fps.valueChanged.connect(self.update_fps)
        self.fps.setValue(self.timelapse.fps)
        self.fps.setMinimum(0)
        self.fps.setMaximum(1000)
        fps_layout.addWidget(fps_legend)
        fps_layout.addWidget(self.fps)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addLayout(dim_layout)
        layout.addLayout(fps_layout)
        layout.addLayout(dur_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def update_fps(self, value):
        self.timelapse.fps = value
        self.duration.setText(self.timelapse.get_duration())
        self.timelapse.timestamp.setText(self.timelapse.get_timestamp())