from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout


class VideoWidget(QWidget):
    def __init__(self, video):
        super().__init__()
        self.video = video

        layout = QVBoxLayout()

        # header
        header = QLabel(text='Video', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # video name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name:", objectName="legend")
        self.name = QLabel(text=self.video.title, objectName="name")
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # video dimensions
        dim_layout = QHBoxLayout()
        dim_legend = QLabel(text="Dimensions:", objectName="legend")
        self.dimensions = QLabel(text=self.video.get_dimensions(), objectName="property")
        dim_layout.addWidget(dim_legend)
        dim_layout.addWidget(self.dimensions)

        # video fps
        fps_layout = QHBoxLayout()
        fps_legend = QLabel(text="FPS:", objectName="legend")
        self.fps = QLabel(text=str(self.video.fps), objectName="property")
        fps_layout.addWidget(fps_legend)
        fps_layout.addWidget(self.fps)

        # video duration
        dur_layout = QHBoxLayout()
        dur_legend = QLabel(text="Duration:", objectName="legend")
        self.duration = QLabel(text=self.video.get_duration(), objectName="property")
        dur_layout.addWidget(dur_legend)
        dur_layout.addWidget(self.duration)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addLayout(dim_layout)
        layout.addLayout(fps_layout)
        layout.addLayout(dur_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

