from PySide6.QtCore import Signal, QObject


class Sphere(QObject):
    update_rot = Signal(float, float, float)

    def __init__(self):
        super().__init__()
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.prev_rot = (0, 0, 0)

    def get_rotation(self):
        return self.roll, self.pitch, self.yaw

    def set_rotation(self, rot):
        self.prev_rot = (self.get_rotation())
        self.roll, self.pitch, self.yaw = rot
        self.update_rot.emit(*rot)

    def undo_rot(self):
        self.set_rotation(self.prev_rot)
