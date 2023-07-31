from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SnapshotTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("snapshot tab")
        layout.addWidget(label)

        self.setLayout(layout)
