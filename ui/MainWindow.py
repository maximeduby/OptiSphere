from PySide6.QtGui import QScreen, QAction, QActionGroup
from PySide6.QtCore import Slot
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QMessageBox, QHBoxLayout, QVBoxLayout

from ui.SidebarLayout import SidebarLayout
from ui.tabs.CameraTab import CameraTab
from ui.tabs.SnapshotTab import SnapshotTab


class MainWindow(QMainWindow):

    def __init__(self):
        # window shape init
        super().__init__()
        self.setWindowTitle("Name of Software")
        self.setGeometry(0, 0, 1280, 720)
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        # tabs widget
        self.tabs = QTabWidget()
        self.cam_tab = CameraTab(self)
        self.tabs.addTab(self.cam_tab, "Camera")
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setTabsClosable(True)

        # central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        # self.setCentralWidget(self.tabs)

        # tabs layout
        self.tabs_layout = QVBoxLayout()
        self.tabs_layout.addWidget(self.tabs)

        # sidebar layout
        self.sidebar_layout = SidebarLayout(self.tabs)
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
        self.file_menu.addAction('New', lambda: print("New"))
        self.file_menu.addAction('Open', lambda: print('Open'))
        self.file_menu.addAction('Exit', QApplication.instance().quit())
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

    def closeEvent(self, event):
        self.cam_tab.th.stop()
        event.accept()