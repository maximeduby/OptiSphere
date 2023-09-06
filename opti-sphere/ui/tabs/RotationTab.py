from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class RotationTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel("Test")

        layout.addWidget(label)
        self.setLayout(layout)
