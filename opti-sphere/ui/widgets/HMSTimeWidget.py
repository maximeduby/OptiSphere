from PySide6.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QLabel


class HMSTimeWidget(QWidget):  # widget to display duration with hours-minutes-seconds format
    def __init__(self, duration):
        super().__init__()
        self.duration = duration

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        self.hours = QSpinBox()
        self.hours.setValue(self.duration // 3600)
        self.duration = self.duration % 3600

        self.minutes = QSpinBox()
        self.minutes.setRange(0, 59)
        self.minutes.setValue(self.duration // 60)
        self.duration = self.duration % 60

        self.seconds = QSpinBox()
        self.seconds.setRange(0, 59)
        self.seconds.setValue(self.duration)

        layout.addWidget(self.hours)
        layout.addWidget(QLabel("h"))
        layout.addWidget(self.minutes)
        layout.addWidget(QLabel("min"))
        layout.addWidget(self.seconds)
        layout.addWidget(QLabel("s"))

        self.setLayout(layout)

    def get_value(self):  # return total seconds
        return self.seconds.value() + self.minutes.value()*60 + self.hours.value()*3600
