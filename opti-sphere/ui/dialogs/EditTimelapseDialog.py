from PySide6.QtWidgets import QFormLayout, QSpinBox, QDialog, QDialogButtonBox

from ui.widgets.HMSTimeWidget import HMSTimeWidget


class EditTimelapseDialog(QDialog):
    def __init__(self, duration, delta_time):
        super().__init__()
        self.setWindowTitle("Edit Timelapse Settings")

        self.prev_duration = duration
        self.prev_delta_time = delta_time

        layout = QFormLayout(self)
        self.duration = HMSTimeWidget(self.prev_duration)
        self.delta_time = QSpinBox()
        self.delta_time.setMinimum(0)
        self.delta_time.setValue(self.prev_delta_time)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        layout.addRow("Recording Duration:", self.duration)
        layout.addRow("Delta Time (seconds):", self.delta_time)
        layout.addWidget(button_box)
        self.setLayout(layout)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def get_duration(self):
        return self.duration.get_value()

    def get_delta_time(self):
        return self.delta_time.value()