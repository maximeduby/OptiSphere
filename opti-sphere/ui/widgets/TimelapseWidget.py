from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QLineEdit


class TimelapseWidget(QWidget):
    update_signal = Signal(str)

    def __init__(self, timelapse):
        super().__init__()
        self.setObjectName('widget-container')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.timelapse = timelapse

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 15, 20, 15)

        # header
        header = QLabel(text='Timelapse', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # timelapse name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name", objectName="legend")
        self.name = QLineEdit(objectName="name")
        self.name.setPlaceholderText("Enter the timelapse name")
        self.name.setText(self.timelapse.title)
        self.name.returnPressed.connect(lambda: self.save_name(self.name.text()))
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # timelapse details
        details_widget = QWidget(objectName="details")
        details_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        details_layout = QHBoxLayout()
        details_layout.setAlignment(Qt.Alignment.AlignCenter)
        details_layout.setSpacing(20)
        details_layout.setContentsMargins(10, 3, 10, 3)
        dimensions = QLabel(self.timelapse.get_dimensions())
        nb_frames = QLabel(f"{len(self.timelapse.frames)} frames")
        self.duration = QLabel(self.timelapse.get_duration())
        details_layout.addWidget(dimensions)
        details_layout.addWidget(nb_frames)
        details_layout.addWidget(self.duration)
        details_widget.setLayout(details_layout)

        # timelapse fps
        fps_layout = QHBoxLayout()
        fps_legend = QLabel(text="FPS", objectName="legend")
        self.fps = QSpinBox()
        self.fps.valueChanged.connect(self.update_fps)
        self.fps.setValue(self.timelapse.fps)
        self.fps.setMinimum(0)
        self.fps.setMaximum(1000)
        fps_layout.addWidget(fps_legend)
        fps_layout.addWidget(self.fps)
        fps_layout.addStretch(1)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addWidget(details_widget)
        layout.addLayout(fps_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def update_fps(self, value):  # update frequency of timelapse's video playback
        self.timelapse.fps = value
        self.duration.setText(self.timelapse.get_duration())
        self.timelapse.timestamp.setText(self.timelapse.get_timestamp())

    def save_name(self, new_name):  # update timelapse name in tab bar
        self.timelapse.title = new_name
        self.update_signal.emit(new_name)
        self.name.clearFocus()
