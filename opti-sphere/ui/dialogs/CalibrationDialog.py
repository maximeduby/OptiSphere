from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QPushButton, QHBoxLayout, \
    QListView, QVBoxLayout

from ui.widgets.StepWidget import StepWidget


class CalibrationDialog(QDialog):
    def __init__(self, wnd):
        super().__init__()
        self.setWindowTitle("Calibration")
        self.wnd = wnd

        steps_layout = QHBoxLayout()
        step_1 = StepWidget(step=1, text="Make sure the power of the system is turned off")
        step_2 = StepWidget(step=2, text="Screw both linear stage to hold the sphere tight")
        step_3 = StepWidget(step=3, text="Turn the power of the system on")
        steps_layout.addWidget(step_1)
        steps_layout.addWidget(step_2)
        steps_layout.addWidget(step_3)

        ready_button = QPushButton('Ready', objectName="accept-btn")
        ready_button.setMinimumWidth(80)
        cancel_button = QPushButton('Cancel', objectName="reject-btn")
        cancel_button.setMinimumWidth(80)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(ready_button)
        btn_layout.addWidget(cancel_button)
        btn_layout.addStretch()

        vl = QVBoxLayout(self)
        vl.addLayout(steps_layout)
        vl.addStretch(1)
        vl.addLayout(btn_layout)

        ready_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

