import math

from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from OpenGL.GLUT import glutWireSphere, glutSolidCone
from PySide6.QtCore import Qt, Signal
from PySide6.QtOpenGLWidgets import QOpenGLWidget


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
            self.pitch_angle += dy
            self.roll_angle += dx
            self.yaw_angle += 0
            self.update()
            self.drag_x = event.x()
            self.drag_y = event.y()
            print(self.roll_angle, self.pitch_angle, self.yaw_angle)
            self.update_rot.emit(self.roll_angle, self.pitch_angle, self.yaw_angle)
