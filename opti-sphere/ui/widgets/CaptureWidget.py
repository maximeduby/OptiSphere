from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDialog

from core.threads.SnapshotThread import SnapshotThread
from core.threads.TimelapseThread import TimelapseThread
from core.threads.VideoThread import VideoThread
from ui.buttons.IconButton import IconButton
from ui.dialogs.EditTimelapseDialog import EditTimelapseDialog
from ui.tabs.SnapshotTab import SnapshotTab
from ui.tabs.TimelapseTab import TimelapseTab
from ui.tabs.VideoTab import VideoTab


class CaptureWidget(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.setObjectName('widget-container')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.wnd = wnd

        self.ss_counter, self.vid_counter, self.tl_counter = 1, 1, 1
        self.vid_th, self.tl_th, self.tl_cooldown = None, None, None
        self.tl_duration = 90
        self.tl_delta_time = 1

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # header
        header = QLabel(text='Capture', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # capture buttons
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        self.ss_btn = IconButton("resources/icons/snapshot-icon.svg")
        self.ss_btn.setObjectName("ss")
        self.ss_btn.set_icon_color("#CCCCCC")
        self.vid_btn = IconButton("resources/icons/video-icon.svg")
        self.vid_btn.setObjectName("start")
        self.vid_btn.set_icon_color("#CCCCCC")
        self.tl_btn = IconButton("resources/icons/timelapse-icon.svg")
        self.tl_btn.setObjectName("start")
        self.tl_btn.set_icon_color("#CCCCCC")

        self.ss_btn.clicked.connect(self.capture_ss)
        self.vid_btn.clicked.connect(self.capture_vid)
        self.tl_btn.clicked.connect(self.capture_tl)

        ss_layout = QVBoxLayout()
        ss_layout.setSpacing(3)
        vid_layout = QVBoxLayout()
        vid_layout.setSpacing(3)
        tl_layout = QVBoxLayout()
        tl_layout.setSpacing(3)

        ss_legend = QLabel(text="Snapshot", objectName="btn-legend")
        ss_legend.setAlignment(Qt.Alignment.AlignCenter)
        vid_legend = QLabel(text="Video", objectName="btn-legend")
        vid_legend.setAlignment(Qt.Alignment.AlignCenter)
        tl_legend = QLabel(text="Timelapse", objectName="btn-legend")
        tl_legend.setAlignment(Qt.Alignment.AlignCenter)

        ss_layout.addWidget(self.ss_btn)
        ss_layout.addWidget(ss_legend)
        vid_layout.addWidget(self.vid_btn)
        vid_layout.addWidget(vid_legend)
        tl_layout.addWidget(self.tl_btn)
        tl_layout.addWidget(tl_legend)

        h_layout.addStretch(1)
        h_layout.addLayout(ss_layout)
        h_layout.addStretch(1)
        h_layout.addLayout(vid_layout)
        h_layout.addStretch(1)
        h_layout.addLayout(tl_layout)
        h_layout.addStretch(1)

        layout.addWidget(header)
        layout.addLayout(h_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def capture_ss(self):
        self.ss_btn.setEnabled(False)
        ss_th = SnapshotThread(self.wnd.main_tab.th)
        ss_th.ss_signal.connect(self.add_ss_tab)
        ss_th.start()
        ss_th.wait()
        self.ss_btn.setEnabled(True)

    @Slot()
    def capture_vid(self):
        self.vid_btn.setEnabled(False)
        if self.vid_btn.objectName() == "start":
            self.vid_btn.setObjectName("stop")
            self.vid_btn.set_icon_color("#f61027")
            self.vid_btn.setStyleSheet('border-color: #f61027;')
            self.vid_btn.setEnabled(True)
            self.vid_th = VideoThread(self.wnd.main_tab.th)
            self.vid_th.vid_signal.connect(self.add_vid_tab)
            self.vid_th.start()
        else:
            self.vid_th.running = False
            self.vid_th.wait()
            self.vid_btn.setObjectName("start")
            self.vid_btn.set_icon_color("#CCCCCC")
            self.vid_btn.setStyleSheet('border-color: #CCCCCC;')
            self.vid_btn.setEnabled(True)

    @Slot()
    def capture_tl(self):
        self.tl_btn.setEnabled(False)
        if self.tl_btn.objectName() == "start":
            dialog = EditTimelapseDialog(self.tl_duration, self.tl_delta_time)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                self.tl_duration = dialog.get_duration()
                self.tl_delta_time = dialog.get_delta_time()
                self.tl_btn.setObjectName("stop")
                self.tl_btn.set_icon_color("#f61027")
                self.tl_btn.setStyleSheet('border-color: #f61027;')
                self.tl_th = TimelapseThread(self.wnd.main_tab.th, self.tl_delta_time)
                self.tl_th.tl_signal.connect(self.add_tl_tab)
                self.tl_cooldown = QTimer(self)
                self.tl_cooldown.timeout.connect(self.capture_tl)
                self.tl_th.start()
                self.tl_cooldown.start(1000*self.tl_duration)
            self.tl_btn.setEnabled(True)
        else:
            self.tl_cooldown.stop()
            self.tl_th.running = False
            self.tl_th.wait()
            self.tl_btn.setObjectName("start")
            self.tl_btn.set_icon_color("#CCCCCC")
            self.tl_btn.setStyleSheet('border-color: #CCCCCC;')
            self.tl_btn.setEnabled(True)

    @Slot()
    def add_ss_tab(self, frame):
        title = f"snapshot{self.ss_counter}"
        snapshot_tab = SnapshotTab(frame, title)
        self.wnd.tabs.addTab(snapshot_tab, title)
        self.wnd.tabs.setCurrentWidget(snapshot_tab)
        self.ss_counter += 1

    @Slot()
    def add_vid_tab(self, frames):
        title = f"video{self.vid_counter}"
        video_tab = VideoTab(frames, title, self.wnd.fps)
        self.wnd.tabs.addTab(video_tab, title)
        self.wnd.tabs.setCurrentWidget(video_tab)
        self.vid_counter += 1

    @Slot()
    def add_tl_tab(self, frames):
        title = f"timelapse{self.tl_counter}"
        tl_tab = TimelapseTab(frames, title)
        self.wnd.tabs.addTab(tl_tab, title)
        self.wnd.tabs.setCurrentWidget(tl_tab)
        self.tl_counter += 1
