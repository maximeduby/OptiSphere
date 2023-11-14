import cv2

from PySide6.QtCore import Slot, Qt, Signal
from PySide6.QtGui import QShortcut
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog

from core.threads.CameraThread import CameraThread
from ui.dialogs.CalibrationDialog import CalibrationDialog
from ui.tabs.RotationTab import RotationTab
from ui.tabs.ScanningTab import ScanningTab
from ui.tabs.Tab import Tab
from ui.tabs.TrackingTab import TrackingTab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.CaptureWidget import CaptureWidget


class MainTab(Tab):
    box_signal = Signal(tuple)

    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.camera_feed = ImageViewer()
        self.capture = CaptureWidget(self.wnd)
        self.control = QTabWidget(objectName="control-tabs")
        self.rotation = RotationTab(self.wnd)
        self.tracking = TrackingTab(self.wnd)
        self.scanning = ScanningTab(self.wnd)

        self.control.addTab(self.rotation, "Rotation")
        self.control.addTab(self.tracking, "Tracking")
        self.control.addTab(self.scanning, "Scanning")
        self.control.setHidden(True)

        self.calibration = QWidget(objectName='widget-container')
        self.calibration.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        calib_layout = QVBoxLayout()
        calib_layout.setAlignment(Qt.Alignment.AlignCenter)
        calib_icon_layout = QHBoxLayout()
        calib_icon = QSvgWidget("resources/icons/calibration-icon.svg")
        calib_icon.setFixedSize(50, 50)
        calib_icon_layout.addStretch()
        calib_icon_layout.addWidget(calib_icon)
        calib_icon_layout.addStretch()
        calib_icon_layout.setContentsMargins(0, 0, 0, 15)
        calib_legend = QLabel(text="Start by calibrating the system", objectName="legend")
        calib_legend.setAlignment(Qt.Alignment.AlignCenter)
        btn_layout = QHBoxLayout()
        calib_btn = QPushButton(text="Calibrate", objectName="accept-btn")
        pass_calib_btn = QPushButton(text="Pass", objectName="reject-btn")
        calib_btn.clicked.connect(self.start_calibration)
        pass_calib_btn.clicked.connect(self.pass_calibration)
        btn_layout.addWidget(calib_btn)
        btn_layout.addWidget(pass_calib_btn)
        calib_layout.addStretch()
        calib_layout.addLayout(calib_icon_layout)
        calib_layout.addWidget(calib_legend)
        calib_layout.addLayout(btn_layout)
        calib_layout.addStretch()
        self.calibration.setLayout(calib_layout)

        self.scene_layout.addWidget(self.camera_feed)
        self.sidebar_layout.addWidget(self.capture)
        self.sidebar_layout.addWidget(self.calibration)
        self.sidebar_layout.addWidget(self.control)

        self.th = CameraThread(0, self.wnd.threads)
        self.th.cam_signal.connect(self.handle_camera_feed)
        self.th.start()

        self.is_tracking_on = False
        self.tracker = None
        self.selection_origin, self.selection_destination, self.selection, self.is_selecting = None, None, None, False
        QShortcut(Qt.Key.Key_Escape, self, self.release_tracking)

    @Slot()
    def select_camera_source(self):  # update camera feed to selected camera source
        device_index = self.wnd.cam_devices_group.checkedAction().data()
        self.th.stop()
        self.th = CameraThread(device_index, self.wnd.threads)
        self.th.cam_signal.connect(self.handle_camera_feed)
        self.th.start()

    @Slot()
    def handle_camera_feed(self, frame):  # set current frame to camera feed widget with or without tracking box
        if self.is_tracking_on:  # if tracking is activated --> draw tracking box on top of frame
            ok, box = self.tracker.update(self.th.get_monochrome())
            if ok:
                self.box_signal.emit(box)
                cv2.rectangle(
                    frame,
                    (int(box[0]), int(box[1])),
                    (int(box[0] + box[2]), int(box[1] + box[3])),
                    (255, 255, 0),
                    8,
                    2
                )

        self.camera_feed.gv.set_image(frame)

    def release_tracking(self):  # stop tracking
        if self.is_tracking_on:
            self.tracking.init_tracking()
        if self.camera_feed.gv.selection_mode:
            self.tracking.roi_selection()

    def set_action(self, action):  # disable other control tabs when one is running to avoid intertwined threads
        if action == "rotation":
            self.tracking.setEnabled(False)
            self.scanning.setEnabled(False)
        elif action == "tracking":
            self.rotation.setEnabled(False)
            self.scanning.setEnabled(False)
        elif action == "scanning":
            self.rotation.setEnabled(False)
            self.tracking.setEnabled(False)
        elif action == "none":
            self.rotation.setEnabled(True)
            self.tracking.setEnabled(True)
            self.scanning.setEnabled(True)

    @Slot()
    def start_calibration(self):  # show calibration instructions and calibrate system
        calib = CalibrationDialog(self.wnd)
        ready = calib.exec()
        if ready == QDialog.DialogCode.Accepted:
            self.wnd.ser.send_command("calibrate")
            self.calibration.setHidden(True)
            self.control.setHidden(False)

    @Slot()
    def pass_calibration(self):  # pass calibration and show control tabs
        self.calibration.setHidden(True)
        self.control.setHidden(False)
