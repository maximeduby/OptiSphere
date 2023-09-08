class Sphere:
    roll = 0
    pitch = 0
    yaw = 0

    def get_rotation(self):
        return self.roll, self.pitch, self.yaw

    def set_rotation(self, rot):
        self.roll, self.pitch, self.yaw = rot
