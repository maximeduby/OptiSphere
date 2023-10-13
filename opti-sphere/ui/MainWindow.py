import csv
import datetime
import os
import shutil
from configparser import ConfigParser

import cv2
import serial
from PySide6.QtCore import Slot

from PySide6.QtGui import QScreen, QActionGroup, QAction
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout,
                               QTabWidget, QTabBar, QMessageBox, QInputDialog, QDialog)

from config import WINDOW_WIDTH, WINDOW_HEIGHT

from core.models.TrackingData import TrackingData
from core.models.SerialCom import SerialCom
from core.models.Sphere import Sphere
from ui.dialogs.CheckListDialog import CheckListDialog
from ui.tabs.ScanTab import ScanTab
from ui.tabs.TrackTab import TrackTab
from ui.widgets.SerialDebugger import SerialDebugger
from ui.tabs.MainTab import MainTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # window configuration
        self.setWindowTitle("Opti-Sphere")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        # variables
        self.fps = 30
        self.sphere = Sphere()
        self.threads = []

        # tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tab_changed)
        self.main_tab = MainTab(self)
        self.tabs.addTab(self.main_tab, "Home")
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.LeftSide, None)
        self.tabs.tabBar().setUsesScrollButtons(True)
        self.tabs.tabBar().setMovable(True)

        # main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tabs)

        # central widget
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # init menu bar
        self.file_menu = self.menuBar().addMenu('&File')
        self.cam_menu = self.menuBar().addMenu('&Camera')
        self.tools_menu = self.menuBar().addMenu('&Tools')
        self.cam_devices_group = QActionGroup(self)
        self.init_menu_bar()

        self.show()

        # serial connection
        self.ser = SerialCom(wnd=self)
        self.setup_serial_connection()

        # debugger
        self.debugger = SerialDebugger(self)

        # recovery
        self.fetch_recovery()

    def close_tab(self, index):
        if index != 0:
            confirm = QMessageBox.question(self,
                                           "Close Tab",
                                           "Are you sure you want to close this tab?",
                                           QMessageBox.StandardButton.Yes,
                                           QMessageBox.StandardButton.Cancel)
            if confirm == QMessageBox.StandardButton.Yes:
                tab = self.tabs.widget(index)
                if tab.__class__.__name__ in ["ScanTab", "TrackTab"]:
                    shutil.rmtree(os.path.join("recovery"), tab.info[0])

                self.tabs.removeTab(index)
                self.tabs.setCurrentWidget(self.main_tab)

    def closeEvent(self, event):
        confirm = QMessageBox.question(self,
                                       "Close App",
                                       "Are you sure you want to close?",
                                       QMessageBox.StandardButton.Cancel,
                                       QMessageBox.StandardButton.Close)
        if confirm == QMessageBox.StandardButton.Close:
            for window in QApplication.topLevelWidgets():
                window.close()
            for th in reversed(self.threads):
                th.stop()
            event.accept()
        else:
            event.ignore()

    def init_menu_bar(self):
        # file menu
        self.file_menu.addAction("Open", lambda: self.open_file())
        self.file_menu.addAction('Save', lambda: self.tabs.currentWidget().save())
        self.file_menu.actions()[1].setEnabled(False)

        # camera menu
        self.cam_devices_group.setExclusive(True)
        self.update_camera_menu()
        self.cam_devices_group.triggered.connect(self.main_tab.select_camera_source)
        self.cam_devices_group.actions()[0].setChecked(True)

        # tools menu
        self.tools_menu.addAction('Connect to serial', self.open_serial_setup)
        self.tools_menu.addAction('Serial Debugger', self.open_serial_debugger)
    def update_camera_menu(self):
        for action in self.cam_devices_group.actions():
            self.cam_menu.removeAction(action)
            action.deleteLater()

        available_cameras = QMediaDevices.videoInputs()
        for index, cam in enumerate(available_cameras):
            cam_device_action = QAction(cam.description(), self.cam_devices_group)
            cam_device_action.setCheckable(True)
            cam_device_action.setData(index)
            self.cam_devices_group.addAction(cam_device_action)
            self.cam_menu.addAction(cam_device_action)

    def tab_changed(self, index):
        if self.tabs.widget(index).__class__.__name__ == "MainTab":
            try:
                self.file_menu.actions()[1].setEnabled(False)
            except AttributeError:
                pass
        else:
            self.file_menu.actions()[1].setEnabled(True)

    @Slot()
    def update_name(self, new_name):
        self.tabs.setTabText(self.tabs.currentIndex(), new_name)

    def open_serial_debugger(self):
        if self.ser.isOpen():
            self.tools_menu.actions()[0].setEnabled(False)
            # debugger = SerialDebugger(self)
            self.debugger.show()

    def open_serial_setup(self):
        ports = ['--None--'] + self.ser.available_port()
        port, ok = QInputDialog().getItem(self, "Select Port", "Port:", ports, -1, False)
        if ok and port:
            if port == "--None--":
                print("Port chosen: None")
            else:
                print(f"Port chosen: {port}")
                self.setup_serial_connection(port)

    def setup_serial_connection(self, port=None):
        if not port:
            ports = self.ser.available_port()
            if ports:
                port = ports[0]
            else:
                port = None
        if port:
            try:
                self.ser = SerialCom(wnd=self, port=port)
            except serial.SerialException:
                self.raise_()
                print(f"Error: Failed to communicate with {port}")
                QMessageBox(self).critical(self, "Error", f"Failed to communicate with '{port}'")
        else:
            self.raise_()
            print("Error: Could not find any device for serial communication")
            QMessageBox(self).critical(self, "Error", f"Could not find any device for serial communication")

    def fetch_recovery(self):
        if not os.path.exists("recovery"):
            os.makedirs("recovery")
            return
        directories = next(os.walk('recovery'))[1]
        if not directories:
            print("Nothing in recovery folder")
            return
        recovery_list = []
        dialog = CheckListDialog(directories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            recovery_list = dialog.choices
        for directory in directories:
            if not (directory in recovery_list):
                shutil.rmtree(os.path.join("recovery", directory))
        for directory in recovery_list:
            try:
                location = os.path.join("recovery", directory)
                config = ConfigParser()
                config.read(os.path.join(location, "CONFIG.INI"))
                if config.sections()[0] == "SCAN":
                    nb_frames = int(config['SCAN']['nb_frames'])
                    frames = []
                    frames_files = []
                    for filename in os.listdir(os.path.join(location, "frames")):
                        f = os.path.join(os.path.join(location, "frames"), filename)
                        if os.path.isfile(f):
                            frames_files.append(f)

                    if len(frames_files) == nb_frames and nb_frames != 0:
                        frames_files.sort()
                        for file in frames_files:
                            frames.append(cv2.imread(file))
                        info = (
                            config['SCAN']['name'],
                            config['SCAN']['method'],
                            config['SCAN']['axis'],
                            float(config['SCAN']['delta_angle']),
                            False
                        )
                        scan_tab = ScanTab(frames, info[0], info)
                        scan_tab.scan_widget.update_signal.connect(self.update_name)
                        self.tabs.addTab(scan_tab, info[0])
                        self.tabs.setCurrentWidget(scan_tab)
                elif config.sections()[0] == "TRACK":
                    track = []
                    with open(f'{location}/data.csv', 'r') as file:
                        reader = csv.reader(file)
                        next(reader)
                        for row in reader:

                            track.append(TrackingData(
                                tuple([float(i) for i in row[:3]]),
                                datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S.%f'))
                            )
                        if int(config['TRACK']["nb_points"]) != len(track):
                            print("Error when loading data: Incorrect number of track points")
                    info = (
                        config['TRACK']['name'],
                        config['TRACK']['mode'],
                        config['TRACK']['description']
                    )
                    track_tab = TrackTab(track, info[0], info)
                    track_tab.track_widget.update_signal.connect(self.update_name)
                    self.tabs.addTab(track_tab, info[0])
                    self.tabs.setCurrentWidget(track_tab)

            except FileExistsError or FileNotFoundError as e:
                print(e)

    def open_file(self):
        print("open")
