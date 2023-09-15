import math

from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from OpenGL.GLUT import glutWireSphere, glutSolidCone
from PySide6.QtCore import Qt, Signal
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from pyquaternion import Quaternion


class Rotation3DRender(QOpenGLWidget):
    update_rot = Signal(int, int, int)
    def __init__(self):
        super().__init__()

        self.roll_angle = 0
        self.pitch_angle = 0
        self.yaw_angle = 0

        self.drag_x = 0
        self.drag_y = 0
        self.is_dragging = False

        self.quat = Quaternion()

    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)  # for proper 3D rendering and avoid plan overlapping
        glEnable(GL_CULL_FACE)  # does not render what is not visible (improve rendering performance)
        glEnable(GL_COLOR_MATERIAL)  # smooth transition between colors
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)


    def paintGL(self) -> None:
        # clear scene
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(30, self.width() / self.height(), 1, 1000)  # (fov, aspect ratio, nearest plan, farthest plan)

        # set scene
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -6)  # move camera position

        # rotate the sphere
        glRotatef(self.pitch_angle, 1, 0, 0)
        glRotatef(self.roll_angle, 0, 1, 0)
        glRotatef(self.yaw_angle, 0, 0, 1)

        # Render the sphere
        glColor3f(0.06, 0.36, 0.96)
        glutWireSphere(1, 50, 50)
        glColor3f(1, 0, 0)
        glutSolidCone(0.2, 0.4, 50, 50)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.drag_x = event.x()
            self.drag_y = event.y()
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            dx = event.x() - self.drag_x
            dy = event.y() - self.drag_y
            dpitch, dyaw, droll, self.quat = self.pan_to_rotation(dx, dy, self.quat)
            self.roll_angle += droll
            self.pitch_angle += dpitch
            self.yaw_angle += dyaw
            # self.pitch_angle += dy
            # self.roll_angle += dx
            # self.yaw_angle += 0
            self.update()
            self.drag_x = event.x()
            self.drag_y = event.y()
            print(self.roll_angle, self.pitch_angle, self.yaw_angle)
            self.update_rot.emit(self.roll_angle, self.pitch_angle, self.yaw_angle)

    def quaternion_to_euler(self, quaternion):
        # Convert a quaternion to Euler angles (roll, pitch, yaw) in degrees.

        # Extract the components of the quaternion.
        w, x, y, z = quaternion

        # Calculate the roll (x-axis rotation).
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Calculate the pitch (y-axis rotation).
        sinp = 2.0 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # Calculate the yaw (z-axis rotation).
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)

    def pan_to_rotation(self, dx, dy, current_quaternion):
        # Sensitivity values control how fast the sphere rotates in response to panning.
        sensitivity_x = 0.01  # Adjust this value as needed.
        sensitivity_y = 0.01  # Adjust this value as needed.

        # Calculate incremental rotation angles based on delta x and delta y.
        d_yaw = dx * sensitivity_x
        d_pitch = dy * sensitivity_y

        # Create quaternions for the incremental rotations.
        quaternion_yaw = Quaternion(axis=[0, 0, 1], angle=d_yaw)
        quaternion_pitch = Quaternion(axis=[1, 0, 0], angle=d_pitch)

        # Combine the incremental rotations (yaw and pitch) into a single quaternion.
        cumulative_quaternion = quaternion_yaw * quaternion_pitch

        # Update the current quaternion with the cumulative rotation.
        new_quaternion = cumulative_quaternion * current_quaternion

        # Calculate the incremental changes in roll, pitch, and yaw.
        current_euler = self.quaternion_to_euler(current_quaternion)
        new_euler = self.quaternion_to_euler(new_quaternion)

        droll = new_euler[0] - current_euler[0]
        dpitch = new_euler[1] - current_euler[1]
        dyaw = new_euler[2] - current_euler[2]

        return droll, dpitch, dyaw, new_quaternion
