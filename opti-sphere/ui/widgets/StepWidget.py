from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class StepWidget(QWidget):
    def __init__(self, step, text):
        super().__init__()
        self.setFixedSize(200, 200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.Alignment.AlignCenter)

        digit = QLabel(text=str(step), objectName="digit")
        digit.setAlignment(Qt.Alignment.AlignCenter)

        description = QLabel(text=text, objectName="legend")
        description.setWordWrap(True)
        description.setAlignment(Qt.Alignment.AlignCenter)

        layout.addStretch()
        layout.addWidget(digit)
        layout.addWidget(description)
        layout.addStretch()
        self.setLayout(layout)
