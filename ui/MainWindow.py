import glob
import sys

import serial

from PySide6.QtGui import QScreen, QAction, QActionGroup
from PySide6.QtCore import Slot
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QMessageBox, QHBoxLayout, QVBoxLayout

from configuration import BAUD_RATE
from ui.SidebarLayout import SidebarLayout
from ui.tabs.CameraTab import CameraTab
from ui.tabs.SnapshotTab import SnapshotTab
from ui.tabs.TimelapseTab import TimelapseTab
from ui.tabs.VideoTab import VideoTab


class MainWindow(QMainWindow):

    def __init__(self):
        # window shape init
        super().__init__()
        self.setWindowTitle("OptiSphere")
        self.setGeometry(0, 0, 1280, 720)
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        # variables
        self.ss_counter = 1
        self.vid_counter = 1
        self.tl_counter = 1

        # serial connection
        self.ser = serial.Serial(
            port=self.select_port(),
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        # tabs widget
        self.tabs = QTabWidget()
        self.cam_tab = CameraTab(self)
        self.tabs.addTab(self.cam_tab, "Camera")
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setTabsClosable(True)

        # central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # tabs layout
        self.tabs_layout = QVBoxLayout()
        self.tabs_layout.addWidget(self.tabs)

        # sidebar layout
        self.sidebar_layout = SidebarLayout(self)
        self.tabs.currentChanged.connect(self.sidebar_layout.update_sidebar)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.addLayout(self.tabs_layout, 7)
        main_layout.addLayout(self.sidebar_layout, 3)

        # menu
        self.file_menu = self.menuBar().addMenu('&File')
        self.edit_menu = self.menuBar().addMenu('&Edit')
        self.cam_menu = self.menuBar().addMenu('&Camera')
        self.help_menu = self.menuBar().addMenu('&Help')
        self.file_menu.addAction('Open', lambda: self.open_file())
        self.file_menu.addAction('Save', lambda: self.tabs.currentWidget().save())
        self.file_menu.addAction('Quit', QApplication.instance().quit())
        self.cam_devices_group = QActionGroup(self)
        self.cam_devices_group.setExclusive(True)
        self.update_cameras()
        self.cam_devices_group.triggered.connect(self.cam_tab.select_camera)
        self.cam_devices_group.actions()[0].setChecked(True)

        # display the window
        self.show()

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

    def close_tab(self, index):
        if index != 0:
            confirm = QMessageBox.question(self,
                                           "Close Tab",
                                           "Are you sure you want to close this tab?",
                                           QMessageBox.StandardButton.Yes,
                                           QMessageBox.StandardButton.Cancel)
            if confirm == QMessageBox.StandardButton.Yes:
                self.tabs.removeTab(index)
                self.tabs.setCurrentWidget(self.cam_tab)

    def closeEvent(self, event):
        self.cam_tab.th.stop()
        event.accept()

    @Slot()
    def add_tab(self, thread):
        match thread.__class__.__name__:
            case "SnapshotThread":
                snapshot_tab = SnapshotTab(thread.frame, f"snapshot_{self.ss_counter}")
                snapshot_tab.set_image()
                self.tabs.addTab(snapshot_tab, snapshot_tab.title)
                self.tabs.setCurrentWidget(snapshot_tab)
                self.ss_counter += 1
            case "VideoThread":
                video_tab = VideoTab(thread.recorded_frames, f"video_{self.vid_counter}")
                video_tab.set_video()
                self.tabs.addTab(video_tab, video_tab.title)
                self.tabs.setCurrentWidget(video_tab)
                self.vid_counter += 1
            case "TimelapseThread":
                timelapse_tab = TimelapseTab(thread.recorded_frames, f"timelapse_{self.tl_counter}")
                timelapse_tab.set_video()
                self.tabs.addTab(timelapse_tab, timelapse_tab.title)
                self.tabs.setCurrentWidget(timelapse_tab)
                self.tl_counter += 1

    def open_file(self):
        pass

    def select_port(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.usb*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        if result:
            result = result[0]
        return result
