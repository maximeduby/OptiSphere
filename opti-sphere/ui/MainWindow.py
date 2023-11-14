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
                               QTabWidget, QTabBar, QMessageBox, QInputDialog, QDialog, QFileDialog, QMenu)

from config import WINDOW_WIDTH, WINDOW_HEIGHT

from core.models.TrackingData import TrackingData
from core.models.SerialCom import SerialCom
from core.models.Sphere import Sphere
from ui.dialogs.CheckListDialog import CheckListDialog
from ui.tabs.ScanTab import ScanTab
from ui.tabs.SnapshotTab import SnapshotTab
from ui.tabs.TrackTab import TrackTab
from ui.tabs.VideoTab import VideoTab
from ui.widgets.ImageViewer import ImageViewer, ImageScale
from ui.widgets.SerialTerminal import SerialTerminal
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
        self.terminal = SerialTerminal(self)

        # recovery
        self.fetch_recovery()

    def close_tab(self, index):  # close triggered tab
        if index != 0:
            # ask for confirmation
            confirm = QMessageBox.question(self,
                                           "Close Tab",
                                           "Are you sure you want to close this tab?",
                                           QMessageBox.StandardButton.Yes,
                                           QMessageBox.StandardButton.Cancel)
            if confirm == QMessageBox.StandardButton.Yes:
                tab = self.tabs.widget(index)
                if tab.__class__.__name__ in ["ScanTab", "TrackTab"]:  # remove recovery folder if tab is closed
                    shutil.rmtree(os.path.join("recovery"), tab.info[0])
                    if not os.path.exists("recovery"):
                        os.makedirs("recovery")
                self.tabs.removeTab(index)
                self.tabs.setCurrentWidget(self.main_tab)

    def closeEvent(self, event):  # close the app
        # ask for confirmation
        confirm = QMessageBox.question(self,
                                       "Close App",
                                       "Are you sure you want to close?",
                                       QMessageBox.StandardButton.Cancel,
                                       QMessageBox.StandardButton.Close)
        if confirm == QMessageBox.StandardButton.Close:
            for window in QApplication.topLevelWidgets():
                window.close()
            for th in reversed(self.threads):  # make sure all threads close properly before quitting
                th.stop()
            event.accept()
        else:
            event.ignore()

    def init_menu_bar(self):  # initialize menu bar actions
        # file menu
        self.file_menu.addAction("Import", lambda: self.import_data())
        self.file_menu.addAction('Export', lambda: self.tabs.currentWidget().export())
        self.file_menu.actions()[1].setEnabled(False)

        # camera menu
        self.cam_devices_group.setExclusive(True)
        self.update_camera_menu()
        self.cam_devices_group.triggered.connect(self.main_tab.select_camera_source)
        self.cam_devices_group.actions()[0].setChecked(True)

        # tools menu
        self.tools_menu.addAction('Connect to serial', self.open_serial_setup)
        self.tools_menu.addAction('Serial Terminal', self.open_serial_terminal)
        self.tools_menu.addAction('Calibrate System', self.main_tab.start_calibration)
        scale_menu = QMenu("Scale Bar")
        toggle_scale_action = QAction("Show/Hide Scale Bar", scale_menu, checkable=True)
        toggle_scale_action.triggered.connect(
            lambda: classmethod(ImageViewer.toggle_scale_bar(toggle_scale_action.isChecked())))
        scale_menu.addAction(toggle_scale_action)
        scale_menu.addAction("Setup Scale Bar", lambda: classmethod(ImageScale.setup_scale_bar()))
        self.tools_menu.addMenu(scale_menu)

    def update_camera_menu(self):  # update camera sources with available sources
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

    def tab_changed(self, index):  # allow export tool if current tab is not the MainTab
        if self.tabs.widget(index).__class__.__name__ == "MainTab":
            try:
                self.file_menu.actions()[1].setEnabled(False)
            except AttributeError:
                pass
        else:
            self.file_menu.actions()[1].setEnabled(True)

    @Slot()
    def update_name(self, new_name):  # update tab name with new_name
        self.tabs.setTabText(self.tabs.currentIndex(), new_name)

    def open_serial_terminal(self):  # show Serial Terminal
        if self.ser.isOpen():
            self.tools_menu.actions()[0].setEnabled(False)
            self.terminal.show()

    def open_serial_setup(self):  # select serial port
        ports = ['--None--'] + self.ser.available_port()
        port, ok = QInputDialog().getItem(self, "Select Port", "Port:", ports, -1, False)
        if ok and port:
            if port == "--None--":
                print("Port chosen: None")
            else:
                print(f"Port chosen: {port}")
                self.setup_serial_connection(port)

    def setup_serial_connection(self, port=None):  # setup new Serial Communication with selected port
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

    def fetch_recovery(self):  # recover Scans and Tracks from recovery folder
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
                        return
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

    def import_data(self):  # import data to software (image, video, scan, track)
        files = QFileDialog.getOpenFileNames(self,
                                             "Select one or more files to open",
                                             "/",
                                             "Images (*.png *.tiff *.jpg);;Videos (*.mp4 *.avi);;Config Files (*.INI)")
        for data in files[0]:
            if files[1].startswith("Images"):
                img = cv2.imread(data)
                title = os.path.splitext(os.path.basename(data))[0]
                snapshot_tab = SnapshotTab(img, title)
                snapshot_tab.ss_widget.update_signal.connect(self.update_name)
                self.tabs.addTab(snapshot_tab, title)
                self.tabs.setCurrentWidget(snapshot_tab)
            elif files[1].startswith("Videos"):
                title = os.path.splitext(os.path.basename(data))[0]
                vid = cv2.VideoCapture(data)
                frames = []
                ret = 1
                while ret:
                    ret, frame = vid.read()
                    if ret:
                        frames.append(frame)
                video_tab = VideoTab(frames, title, self.fps)
                video_tab.vid_widget.update_signal.connect(self.update_name)
                self.tabs.addTab(video_tab, title)
                self.tabs.setCurrentWidget(video_tab)
            elif files[1].startswith("Config Files"):
                config = ConfigParser()
                config.read(data)
                if config.sections()[0] == "SCAN":
                    frame_folder = os.path.join(os.path.dirname(data), "frames")
                    if not os.path.exists(frame_folder):
                        print("Frames folder not found")
                        QMessageBox(self).critical(self, "Error", "The folder containing the frames was not found")
                        return
                    options = ["name", "nb_frames", "method", "axis", "delta_angle"]
                    for option in options:
                        if not config.has_option('SCAN', option):
                            print("Cannot read Configuration file")
                            QMessageBox(self).critical(self, "Error", "Cannot read Configuration file")
                            return
                    nb_frames = int(config['SCAN']['nb_frames'])
                    frames = []
                    frames_files = []
                    for filename in os.listdir(frame_folder):
                        if filename.startswith("."):
                            continue
                        f = os.path.join(frame_folder, filename)
                        print(f)
                        if os.path.isfile(f):
                            frames_files.append(f)
                    print(len(frames_files), "AND", nb_frames)
                    if len(frames_files) != nb_frames or nb_frames == 0:
                        print("Error when loading data: Incorrect number of frames")
                        QMessageBox(self).critical(self, "Error", "Error when loading data: Incorrect number of frames")
                        return
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
                    data_CSV = os.path.join(os.path.dirname(data), "data.csv")
                    if not os.path.exists(data_CSV):
                        print("CSV file not found")
                        QMessageBox(self).critical(self, "Error", "CSV file containing data not found")
                        return
                    with open(data_CSV, 'r') as file:
                        reader = csv.reader(file)
                        next(reader)
                        for row in reader:
                            track.append(TrackingData(
                                tuple([float(i) for i in row[:3]]),
                                datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S.%f'))
                            )
                    options = ["name", "nb_points", "mode", "description"]
                    for option in options:
                        if not config.has_option('TRACK', option):
                            print("Cannot read Configuration file")
                            QMessageBox(self).critical(self, "Error", "Cannot read Configuration file")
                            return
                    if int(config['TRACK']["nb_points"]) != len(track):
                        print("Error when loading data: Incorrect number of track points")
                        QMessageBox(self).critical(
                            self,
                            "Error",
                            "Error when loading data: Incorrect number of track points"
                        )
                        return
                    info = (
                        config['TRACK']['name'],
                        config['TRACK']['mode'],
                        config['TRACK']['description']
                    )
                    track_tab = TrackTab(track, info[0], info)
                    track_tab.track_widget.update_signal.connect(self.update_name)
                    self.tabs.addTab(track_tab, info[0])
                    self.tabs.setCurrentWidget(track_tab)

                else:
                    QMessageBox(self).critical(self, "Error", f"Could not read the file {data}")
            else:
                print("File(s) format not recognized")
                QMessageBox(self).critical(self, "Error", "File(s) format not recognized")
