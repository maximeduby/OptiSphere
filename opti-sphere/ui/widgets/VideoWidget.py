from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit


class VideoWidget(QWidget):
    update_signal = Signal(str)

    def __init__(self, video):
        super().__init__()
        self.setObjectName("widget-container")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.video = video

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 15, 20, 15)

        # header
        header = QLabel(text='Video', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # video name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name", objectName="legend")
        self.name = QLineEdit(objectName="name")
        self.name.setPlaceholderText("Enter the video name")
        self.name.setText(self.video.title)
        self.name.returnPressed.connect(lambda: self.save_name(self.name.text()))
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # video details
        details_widget = QWidget(objectName="details")
        details_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        details_layout = QHBoxLayout()
        details_layout.setAlignment(Qt.Alignment.AlignCenter)
        details_layout.setSpacing(20)
        details_layout.setContentsMargins(10, 3, 10, 3)
        dimensions = QLabel(self.video.get_dimensions())
        fps = QLabel(f"{self.video.fps} FPS")
        duration = QLabel(self.video.get_duration())
        details_layout.addWidget(dimensions)
        details_layout.addWidget(fps)
        details_layout.addWidget(duration)
        details_widget.setLayout(details_layout)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addWidget(details_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def save_name(self, new_name):
        self.video.title = new_name
        self.update_signal.emit(new_name)
        self.name.clearFocus()
