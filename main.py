import sys

import cv2
from PySide6.QtGui import QScreen, QAction, QActionGroup, QImage, QPixmap
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel


class CameraThread(QThread):
    cam_signal = Signal(object)

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.running = True

    def run(self):
        cam = cv2.VideoCapture(self.device_id)
        while self.running:
            ret, frame = cam.read()
            if ret:
                self.cam_signal.emit(frame)
        cam.release()

    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QMainWindow):

    def __init__(self):
        # window shape init
        super().__init__()
        self.setWindowTitle("Name of Software")
        self.setGeometry(0, 0, 1280, 720)
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        # camera label
        self.label = QLabel(self)

        # Thread in charge of updating the image
        self.th = CameraThread(0)
        self.th.cam_signal.connect(self.update_frame)
        self.th.start()

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # menu
        self.file_menu = self.menuBar().addMenu('&File')
        self.edit_menu = self.menuBar().addMenu('&Edit')
        self.cam_menu = self.menuBar().addMenu('&Camera')
        self.help_menu = self.menuBar().addMenu('&Help')

        self.file_menu.addAction('New', lambda: print("New"))
        self.file_menu.addAction('Open', lambda: print('Open'))
        self.file_menu.addAction('Exit', QApplication.instance().quit())

        # cam_menu.addAction()

        self.cam_devices_group = QActionGroup(self)
        self.cam_devices_group.setExclusive(True)
        self.update_cameras()
        self.cam_devices_group.triggered.connect(self.select_camera)
        self.menuBar().triggered.connect(self.update_cameras)
        self.cam_devices_group.actions()[0].setChecked(True)

        self.show()

    @Slot()
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = image.scaled(640, 480, Qt.KeepAspectRatio)
        self.label.setPixmap(QPixmap.fromImage(image))

    @Slot()
    def update_cameras(self):
        for action in self.cam_devices_group.actions():
            self.cam_menu.removeAction(action)
            action.deleteLater()

        available_cameras = QMediaDevices.videoInputs()
        for index, cam in enumerate(available_cameras):
            cam_device_action = QAction(cam.description(), self.cam_devices_group)
            cam_device_action.setCheckable(True)
            cam_device_action.setActionGroup(self.cam_devices_group)
            cam_device_action.setData(index)
            self.cam_devices_group.addAction(cam_device_action)
            self.cam_menu.addAction(cam_device_action)

    @Slot()
    def select_camera(self):
        device_index = self.cam_devices_group.checkedAction().data()
        print(device_index)

        # stop the previous camera thread and create a new one with the selected device index
        self.th.stop()
        self.th = CameraThread(device_index)
        self.th.cam_signal.connect(self.update_frame)
        self.th.start()

    def closeEvent(self, event):
        self.th.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    sys.exit(app.exec())
