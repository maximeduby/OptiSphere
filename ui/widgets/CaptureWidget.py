from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox

from core.threads.SnapshotThread import SnapshotThread
from core.threads.VideoThread import VideoThread
from core.threads.TimelapseThread import TimelapseThread
from ui.widgets.CaptureButton import CaptureButton


class CaptureWidget(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.device_index = 0
        self.isVideoRecording = False
        self.isTimelapseRecording = False
        self.wnd = wnd
        self.fps = 30
        self.delta_time = 1
        self.tl_duration = 90

        self.ss_th = SnapshotThread(self.device_index)
        self.vid_th = VideoThread(self.device_index, self.fps, self.wnd.vid_counter)

        layout = QVBoxLayout()

        section_header = QLabel("Capture")
        section_header.setAlignment(Qt.Alignment.AlignCenter)
        section_header.setFont(QFont('Arial', 20))
        h_layout = QHBoxLayout()

        self.ss_btn = CaptureButton(self, "Snapshot", "snapshot_icon.png")
        self.vid_btn = CaptureButton(self, 'Video', "video_icon.png")
        self.tl_btn = CaptureButton(self, 'Timelapse', "timelapse_icon.png")

        h_layout.addWidget(self.ss_btn)
        h_layout.addWidget(self.vid_btn)
        h_layout.addWidget(self.tl_btn)

        # vid_setting_label = QLabel("Video Setting")
        # vid_setting = QComboBox()
        # vid_setting.addItems(["1920x1080, 30fps", "3840x2160, 15fps"])

        tl_settings_label = QLabel("Timelapse Settings")
        tl_delta_time = QSpinBox()
        tl_delta_time.setValue(1)
        tl_delta_time.setMinimum(0)
        tl_delta_time.setSuffix(" seconds between frames")
        tl_delta_time.valueChanged.connect(self.update_delta_time)
        tl_duration = QSpinBox()
        tl_duration.setValue(self.tl_duration)
        tl_duration.setMinimum(0)
        tl_duration.setSuffix(" seconds of recording")
        tl_duration.valueChanged.connect(self.update_duration)

        layout.addWidget(section_header)
        layout.addLayout(h_layout)
        layout.addWidget(tl_settings_label)
        layout.addWidget(tl_delta_time)
        layout.addWidget(tl_duration)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def update_delta_time(self, value):
        self.delta_time = value

    @Slot()
    def update_duration(self, value):
        self.tl_duration = value

    @Slot()
    def capture(self, btn, capture_type):
        btn.setEnabled(False)
        match capture_type:
            case "Snapshot":
                self.ss_th = SnapshotThread(self.device_index)
                self.ss_th.ss_signal.connect(self.wnd.add_tab)
                self.ss_th.start()
                self.ss_th.wait()
                btn.setEnabled(True)
            case "Video":
                btn.setEnabled(True)
                if not self.isVideoRecording:
                    # start recording
                    self.isVideoRecording = True
                    btn.setText("Stop")
                    btn.setStyleSheet("color: red")
                    self.vid_th = VideoThread(self.device_index, self.fps, self.wnd.vid_counter)
                    self.vid_th.vid_signal.connect(self.wnd.add_tab)
                    self.vid_th.start()
                else:
                    self.isVideoRecording = False
                    self.vid_th.running = False
                    self.vid_th.wait()
                    btn.setText("Video")
                    btn.setStyleSheet("")
            case "Timelapse":
                btn.setEnabled(True)
                if not self.isTimelapseRecording:
                    # start recording
                    self.isTimelapseRecording = True
                    btn.setText("Stop")
                    btn.setStyleSheet("color: red")
                    self.tl_th = TimelapseThread(self.device_index, self.delta_time, self.tl_duration,
                                                 self.wnd.tl_counter)
                    self.tl_th.tl_signal.connect(self.wnd.add_tab)
                    self.tl_timer = QTimer(self)
                    self.tl_timer.moveToThread(self.tl_th)

                    self.tl_timer.timeout.connect(lambda: self.capture(btn, "Timelapse"))

                    self.tl_th.start()
                    self.tl_timer.start(1000* self.tl_duration)
                else:
                    self.isTimelapseRecording = False
                    self.tl_timer.stop()
                    self.tl_th.running = False
                    self.tl_th.wait()
                    btn.setText("Timelapse")
                    btn.setStyleSheet("")
