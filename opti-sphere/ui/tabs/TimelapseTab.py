import cv2
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QLabel, QSlider, QHBoxLayout, QFileDialog, QWidget

from ui.tabs.Tab import Tab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.TimelapseWidget import TimelapseWidget


class TimelapseTab(Tab):
    def __init__(self, frames, title):
        super().__init__()
        self.layout().setAlignment(Qt.Alignment.AlignCenter)
        self.frames = frames
        self.title = title

        self.current_frame = 0
        self.is_running = False
        self.fps = 30

        self.timelapse = ImageViewer()
        self.timelapse.set_image(self.frames[self.current_frame])

        timelapse_player = QWidget(objectName="widget-container")
        timelapse_control = QHBoxLayout()
        self.play_btn = QPushButton(objectName='video_control_btn')
        self.play_btn.setIcon(QIcon("resources/icons/play-icon.svg"))
        self.play_btn.clicked.connect(self.toggle_play_pause)
        self.timestamp = QLabel(text="00:00", objectName='timestamp')
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.set_frame)
        self.slider.setRange(0, len(self.frames)-1)
        timelapse_control.addWidget(self.play_btn)
        timelapse_control.addWidget(self.timestamp)
        timelapse_control.addWidget(self.slider)
        timelapse_player.setLayout(timelapse_control)

        self.tl_widget = TimelapseWidget(self)

        self.scene_layout.addWidget(self.timelapse)
        self.scene_layout.addWidget(timelapse_player)
        self.sidebar_layout.addWidget(self.tl_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timelapse)
        self.timer.setInterval(1000/self.fps)
        self.timer.start()

    @Slot()
    def toggle_play_pause(self):
        if self.is_running:
            self.is_running = False
            self.play_btn.setIcon(QIcon("resources/icons/play-icon.svg"))
        else:
            self.is_running = True
            self.play_btn.setIcon(QIcon("resources/icons/pause-icon.svg"))
            if self.current_frame >= len(self.frames) - 1:
                self.current_frame = 0
            if not self.timer.isActive():
                self.timer.setInterval(1000 / self.fps)
                self.timer.start()
                self.update_timelapse()

    @Slot()
    def update_timelapse(self):
        if self.is_running:
            if self.current_frame < len(self.frames):
                self.timer.setInterval(1000 / self.fps)
                self.timelapse.set_image(self.frames[self.current_frame])
                self.slider.setSliderPosition(self.current_frame)
                self.timestamp.setText(self.get_timestamp())
                self.current_frame += 1
            else:
                self.toggle_play_pause()
                self.timer.stop()

    def get_timestamp(self):
        tot_sec = self.current_frame // self.fps
        minutes, seconds = tot_sec // 60, tot_sec % 60
        return f"{'{:02d}'.format(minutes)}:{'{:02d}'.format(seconds)}"

    @Slot()
    def set_frame(self, value):
        self.current_frame = value
        self.timelapse.set_image(self.frames[self.current_frame])
        self.timestamp.setText(self.get_timestamp())
        self.slider.setSliderPosition(self.current_frame)

    def get_dimensions(self):
        vid_height, vid_width, _ = self.frames[0].shape
        dim = f"{vid_width}x{vid_height}"
        return dim

    def get_duration(self):
        tot_sec = len(self.frames) // self.fps
        minutes, seconds = tot_sec // 60, tot_sec % 60
        return f"{'{:02d}'.format(minutes)}:{'{:02d}'.format(seconds)}"

    def save(self):
        filename = QFileDialog.getSaveFileName(None, "Save Timelapse as Video", self.title, "All files (*.*);Video files(*.*)")
        if filename[0] == '':
            return

        vid_height, vid_width, channel = self.frames[0].shape
        size = (vid_width, vid_height)
        output = cv2.VideoWriter(f"{filename[0]}.avi", cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'), self.fps, size)
        for frame in self.frames:
            output.write(frame)
        output.release()
