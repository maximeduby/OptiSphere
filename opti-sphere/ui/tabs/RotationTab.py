from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSlider, QPushButton, QSpinBox

from ui.widgets.Rotation3DRender import Rotation3DRender


class RotationTab(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd

        layout = QVBoxLayout()

        self.rotation_render = Rotation3DRender()
        self.rotation_render.update_rot.connect(self.handle_3d_render)

        self.apply_rot_btn = QPushButton("Apply Rotation", objectName="apply-rot-btn")
        self.apply_rot_btn.setEnabled(False)
        self.apply_rot_btn.clicked.connect(self.apply_rot)

        roll_layout = QHBoxLayout()
        roll_legend = QLabel(text="Roll Axis", objectName="legend")
        roll_legend.setFixedWidth(60)
        self.roll_slider = QSlider(Qt.Orientation.Horizontal)
        self.roll_slider.setRange(-180, 180)
        self.roll_slider.valueChanged.connect(self.handle_roll)
        self.roll_spinbox = QSpinBox()
        self.roll_spinbox.setRange(-180, 180)
        self.roll_spinbox.setSuffix("°")
        self.roll_spinbox.valueChanged.connect(self.handle_roll)
        roll_layout.addWidget(roll_legend)
        roll_layout.addWidget(self.roll_slider)
        roll_layout.addWidget(self.roll_spinbox)

        pitch_layout = QHBoxLayout()
        pitch_legend = QLabel(text="Pitch Axis", objectName="legend")
        pitch_legend.setFixedWidth(60)
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setRange(-180, 180)
        self.pitch_slider.valueChanged.connect(self.handle_pitch)
        self.pitch_spinbox = QSpinBox()
        self.pitch_spinbox.setRange(-180, 180)
        self.pitch_spinbox.setSuffix("°")
        self.pitch_spinbox.valueChanged.connect(self.handle_pitch)
        pitch_layout.addWidget(pitch_legend)
        pitch_layout.addWidget(self.pitch_slider)
        pitch_layout.addWidget(self.pitch_spinbox)

        yaw_layout = QHBoxLayout()
        yaw_legend = QLabel(text="Yaw Axis", objectName="legend")
        yaw_legend.setFixedWidth(60)
        self.yaw_slider = QSlider(Qt.Orientation.Horizontal)
        self.yaw_slider.setRange(-180, 180)
        self.yaw_slider.valueChanged.connect(self.handle_yaw)
        self.yaw_spinbox = QSpinBox()
        self.yaw_spinbox.setRange(-180, 180)
        self.yaw_spinbox.setSuffix("°")
        self.yaw_spinbox.valueChanged.connect(self.handle_yaw)
        yaw_layout.addWidget(yaw_legend)
        yaw_layout.addWidget(self.yaw_slider)
        yaw_layout.addWidget(self.yaw_spinbox)

        layout.addWidget(self.rotation_render)
        layout.addWidget(self.apply_rot_btn)
        layout.addLayout(roll_layout)
        layout.addLayout(pitch_layout)
        layout.addLayout(yaw_layout)
        self.setLayout(layout)

    @Slot()
    def handle_roll(self, value):
        self.roll_spinbox.setValue(value)
        self.roll_slider.setValue(value)
        self.rotation_render.roll_angle = value
        self.rotation_render.update()
        self.check_values()

    @Slot()
    def handle_pitch(self, value):
        self.pitch_spinbox.setValue(value)
        self.pitch_slider.setValue(value)
        self.rotation_render.pitch_angle = value
        self.rotation_render.update()

    @Slot()
    def handle_yaw(self, value):
        self.yaw_spinbox.setValue(value)
        self.yaw_slider.setValue(value)
        self.rotation_render.yaw_angle = value
        self.rotation_render.update()

    @Slot()
    def handle_3d_render(self, roll, pitch, yaw):
        self.roll_slider.setValue((roll + 180) % 360 - 180)
        self.roll_spinbox.setValue((roll + 180) % 360 - 180)

        self.pitch_slider.setValue((pitch + 180) % 360 - 180)
        self.pitch_spinbox.setValue((pitch + 180) % 360 - 180)

        self.yaw_slider.setValue((yaw + 180) % 360 - 180)
        self.yaw_spinbox.setValue((yaw + 180) % 360 - 180)

    def check_values(self):
        if ((self.rotation_render.roll_angle,
             self.rotation_render.pitch_angle,
             self.rotation_render.yaw_angle)
                != (self.wnd.sphere.get_rotation())):
            self.apply_rot_btn.setEnabled(True)
        else:
            self.apply_rot_btn.setEnabled(False)

    @Slot()
    def apply_rot(self):
        rot = (
            self.roll_spinbox.value(),
            self.pitch_spinbox.value(),
            self.yaw_spinbox.value()
        )
        self.wnd.ser.send_instruction(*rot)
        self.wnd.sphere.set_rotation(rot)
        self.apply_rot_btn.setEnabled(False)
