from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpinBox

from ui.dialogs.EditNameDialog import EditNameDialog


class TimelapseWidget(QWidget):
    def __init__(self, timelapse, wnd, tab_index):
        super().__init__()
        self.timelapse = timelapse
        self.wnd = wnd
        self.tab_index = tab_index

        layout = QVBoxLayout()

        section_header = QLabel("Timelapse")
        section_header.setAlignment(Qt.Alignment.AlignCenter)
        section_header.setFont(QFont('Arial', 20))

        name_layout = QHBoxLayout()
        name_legend = QLabel("Name:")
        self.name_text = QLabel(self.timelapse.title)
        edit_name_btn = QPushButton("Edit")
        edit_name_btn.clicked.connect(self.edit_name)
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name_text)
        name_layout.addWidget(edit_name_btn)

        duration_layout = QHBoxLayout()
        duration_legend = QLabel("Duration:")
        self.duration_text = QLabel(self.timelapse.get_duration())
        duration_layout.addWidget(duration_legend)
        duration_layout.addWidget(self.duration_text)

        dim_layout = QHBoxLayout()
        dim_legend = QLabel("Dimensions:")
        dim_text = QLabel(str(self.timelapse.get_dimensions()))
        dim_layout.addWidget(dim_legend)
        dim_layout.addWidget(dim_text)

        fps_layout = QHBoxLayout()
        fps_legend = QLabel("FPS:")
        fps_spinbox = QSpinBox()
        fps_spinbox.setValue(30)
        fps_spinbox.setMinimum(0)
        fps_spinbox.setSuffix(" fps")
        fps_spinbox.valueChanged.connect(self.update_fps)

        fps_layout.addWidget(fps_legend)
        fps_layout.addWidget(fps_spinbox)

        layout.addWidget(section_header)
        layout.addLayout(name_layout)
        layout.addLayout(duration_layout)
        layout.addLayout(dim_layout)
        layout.addLayout(fps_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def edit_name(self):
        former_name = self.timelapse.title
        dialog = EditNameDialog(former_name)
        if dialog.exec():
            new_name = dialog.get_name() if dialog.get_name() != "" else former_name
            self.timelapse.title = new_name
            self.wnd.tabs.setTabText(self.tab_index, new_name)
            self.name_text.setText(new_name)

    @Slot()
    def update_fps(self, value):
        self.timelapse.fps = value
        self.duration_text.setText(self.timelapse.get_duration())
