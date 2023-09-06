import sys
import glob

import serial
from PySide6.QtCore import Qt

from PySide6.QtGui import QScreen, QActionGroup, QAction
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QTabWidget, QTabBar, QMessageBox

from config import WINDOW_WIDTH, WINDOW_HEIGHT, BAUD_RATE
from ui.widgets.SerialTool import SerialTool
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

        # serial connection
        self.ser = serial.Serial(
            port=self.available_port()[0],
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        # tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tab_changed)
        self.main_tab = MainTab(self)
        self.tabs.addTab(self.main_tab, "Home")
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.LeftSide, None)
        self.tabs.tabBar().setUsesScrollButtons(True)

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

        # variables
        self.fps = 30

    def available_port(self):
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
        return result

    def close_tab(self, index):
        if index != 0:
            confirm = QMessageBox.question(self,
                                           "Close Tab",
                                           "Are you sure you want to close this tab?",
                                           QMessageBox.StandardButton.Yes,
                                           QMessageBox.StandardButton.Cancel)
            if confirm == QMessageBox.StandardButton.Yes:
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
            self.main_tab.th.stop()
            event.accept()
        else:
            event.ignore()

    def init_menu_bar(self):
        # file menu
        self.file_menu.addAction('Open', lambda: self.open_file())
        self.file_menu.addAction('Save', lambda: self.tabs.currentWidget().save())
        self.file_menu.addAction('Quit', QApplication.instance().quit())
        self.file_menu.actions()[1].setEnabled(False)

        # camera menu
        self.cam_devices_group.setExclusive(True)
        self.update_camera_menu()
        self.cam_devices_group.triggered.connect(self.main_tab.select_camera_source)
        self.cam_devices_group.actions()[0].setChecked(True)

        # tools menu
        self.tools_menu.addAction('Serial Communication', lambda: self.open_serial_tool())

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

    def open_file(self):
        pass

    def open_serial_tool(self):
        self.tools_menu.actions()[0].setEnabled(False)
        dialog = SerialTool(self)
        dialog.show()
