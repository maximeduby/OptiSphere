from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout


class SnapshotWidget(QWidget):
    def __init__(self, snapshot):
        super().__init__()
        self.snapshot = snapshot

        layout = QVBoxLayout()

        # header
        header = QLabel(text='Snapshot', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # snapshot name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name:", objectName="legend")
        self.name = QLabel(text=self.snapshot.title, objectName="name")
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

