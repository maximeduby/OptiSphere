import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from OpenGL.GLUT import glutWireSphere, glutSolidCone
from OpenGL.raw.GLUT import glutSolidSphere, glutSolidCube
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from pyquaternion import Quaternion


class Rotation3DRender(QOpenGLWidget):
    update_rot = Signal(int, int, int)

    def __init__(self, tracking_mode=False):
        super().__init__()
        self.tracking_mode = tracking_mode

        self.roll_angle = 0
        self.pitch_angle = 0
        self.yaw_angle = 0

        self.drag_x = 0
        self.drag_y = 0

        self.quaternion = Quaternion()

        self.speed = 0.02
        self.tracking_path = []
        self.zoom = 0

        self.sel_points = []

    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)  # for proper 3D rendering and avoid plan overlapping
        glEnable(GL_CULL_FACE)  # does not render what is not visible (improve rendering performance)
        glEnable(GL_COLOR_MATERIAL)  # smooth transition between colors
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

    def paintGL(self) -> None:
        # clear scene
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width() / self.height(), 1, 1000)  # (fov, aspect ratio, nearest plan, farthest plan)

        # set scene
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -6 + self.zoom)  # move camera position

        # rotate the sphere
        glRotatef(-self.roll_angle, 1, 0, 0)
        glRotatef(-self.pitch_angle, 0, 1, 0)
        glRotatef(-self.yaw_angle, 0, 0, 1)

        # Render the sphere
        if self.tracking_mode:
            glColor3f(.85, .85, .85)
            glutSolidSphere(1.99, 50, 50)

            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
            glLineWidth(15)
            for i in range(1, len(self.tracking_path)):
                glBegin(GL_LINES)
                glColor3f(*self.tracking_path[i].get_color(self.tracking_path[i - 1]))
                glVertex3f(*self.tracking_path[i - 1].get_cartesian())
                glVertex3f(*self.tracking_path[i].get_cartesian())
                glEnd()
            glPointSize(20)
            glBegin(GL_POINTS)
            glColor3d(0, 0, 1)
            glVertex3d(*self.tracking_path[0].get_cartesian())
            glVertex3d(*self.tracking_path[-1].get_cartesian())
            glEnd()
            for i in self.sel_points:
                glBegin(GL_POINTS)
                glColor3d(1, 0, 0)
                glVertex3d(*self.tracking_path[i].get_cartesian())
                glEnd()
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)

        else:
            glColor3f(0.06, 0.36, 0.96)
            glutWireSphere(2, 50, 50)
            self.draw_bug()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            ratio = 200 / min(self.width(), self.height())
            self.drag_x = event.x() * ratio - 100
            self.drag_y = (self.height() - event.y()) * ratio - 100

    def mouseMoveEvent(self, event):
        ratio = 200 / min(self.width(), self.height())
        x = event.x() * ratio - 100
        y = (self.height() - event.y()) * ratio - 100
        if (x, y) != (self.drag_x, self.drag_y):
            vec1 = (x - self.drag_x, y - self.drag_y, 0)
            norm = np.linalg.norm(vec1)
            vec1 = vec1 * 1 / norm
            vec2 = (0, 0, 1)

            axis = np.cross(vec1, vec2)
            angle = self.speed * norm

            q = Quaternion(axis=axis, angle=angle)
            self.quaternion = self.euler_to_quaternion(self.roll_angle, self.pitch_angle, self.yaw_angle)
            q = self.quaternion * q

            self.roll_angle, self.pitch_angle, self.yaw_angle = self.quaternion_to_euler(q)

            self.update()
            self.drag_x = x
            self.drag_y = y
            self.update_rot.emit(self.roll_angle, self.pitch_angle, self.yaw_angle)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = event.angleDelta().y() / 1800
        new_zoom = min(3, max(0, self.zoom + zoom_factor))  # zoom between [0, 4]
        self.zoom = new_zoom
        self.update()

    def quaternion_to_euler(self, q):
        w, x, y, z = q

        # Calculate roll
        sr_cp = 2.0 * (w * x + y * z)
        cr_cp = 1.0 - 2.0 * (x * x + y * y)
        roll = np.arctan2(sr_cp, cr_cp)

        # Calculate pitch
        sp = 2.0 * (w * y - z * x)
        pitch = np.copysign(np.pi / 2, sp) if abs(sp) >= 1 else np.arcsin(sp)

        # Calculate the yaw (z-axis rotation).
        sy_cp = 2.0 * (w * z + x * y)
        cy_cp = 1.0 - 2.0 * (y * y + z * z)
        yaw = np.arctan2(sy_cp, cy_cp)

        return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

    def euler_to_quaternion(self, roll, pitch, yaw):
        cy = np.cos(np.deg2rad(yaw) * .5, )
        sy = np.sin(np.deg2rad(yaw) * .5)
        cr = np.cos(np.deg2rad(roll) * .5)
        sr = np.sin(np.deg2rad(roll) * .5)
        cp = np.cos(np.deg2rad(pitch) * .5)
        sp = np.sin(np.deg2rad(pitch) * .5)

        w = cy * cr * cp + sy * sr * sp
        x = cy * sr * cp - sy * cr * sp
        y = cy * cr * sp + sy * sr * cp
        z = sy * cr * cp - cy * sr * sp

        return Quaternion(x=x, y=y, z=z, w=w)

    @staticmethod
    def draw_bug():
        # Body
        glColor3f(1, 0, 0)
        glutSolidSphere(0.5, 20, 20)

        # Head
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        glColor3f(0, 1, 0)
        glutSolidSphere(0.3, 20, 20)
        glPopMatrix()

        # Legs
        glColor3f(1, 1, 0)
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                glPushMatrix()
                glTranslatef(0.2 * i, -0.2 * j, -0.3,)
                glScalef(0.1, 0.1, 0.5)
                glutSolidCube(1)
                glPopMatrix()
