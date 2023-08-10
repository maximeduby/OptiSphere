from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from ui.dialogs.EditNameDialog import EditNameDialog


class VideoWidget(QWidget):
    def __init__(self, video, wnd, tab_index):
        super().__init__()
        self.video = video
        self.wnd = wnd
        self.tab_index = tab_index

        layout = QVBoxLayout()

        section_header = QLabel("Video")
        section_header.setAlignment(Qt.Alignment.AlignCenter)
        section_header.setFont(QFont('Arial', 20))

        name_layout = QHBoxLayout()
        name_legend = QLabel("Name:")
        self.name_text = QLabel(self.video.title)
        edit_name_btn = QPushButton("Edit")
        edit_name_btn.clicked.connect(self.edit_name)
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name_text)
        name_layout.addWidget(edit_name_btn)

        duration_layout = QHBoxLayout()
        duration_legend = QLabel("Duration:")
        duration_text = QLabel(self.video.get_duration())
        duration_layout.addWidget(duration_legend)
        duration_layout.addWidget(duration_text)

        dim_layout = QHBoxLayout()
        dim_legend = QLabel("Dimensions:")
        dim_text = QLabel(str(self.video.get_dimensions()))
        dim_layout.addWidget(dim_legend)
        dim_layout.addWidget(dim_text)

        fps_layout = QHBoxLayout()
        fps_legend = QLabel("FPS:")
        fps_text = QLabel(str(self.video.fps))
        fps_layout.addWidget(fps_legend)
        fps_layout.addWidget(fps_text)

        layout.addWidget(section_header)
        layout.addLayout(name_layout)
        layout.addLayout(duration_layout)
        layout.addLayout(dim_layout)
        layout.addLayout(fps_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def edit_name(self):
        former_name = self.video.title
        dialog = EditNameDialog(former_name)
        if dialog.exec():
            new_name = dialog.get_name() if dialog.get_name() != "" else former_name
            self.video.title = new_name
            self.wnd.tabs.setTabText(self.tab_index, new_name)
            self.name_text.setText(new_name)
