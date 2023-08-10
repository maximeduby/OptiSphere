import cv2
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout, QSlider, QFileDialog


class TimelapseTab(QWidget):
    def __init__(self, recorded_frames, title):
        super().__init__()
        self.frames = recorded_frames
        self.title = title
        self.fps = 30
        self.current_frame = 0
        self.tl_running = False

        layout = QVBoxLayout()
        self.timelapse = QLabel()
        self.timelapse.setAlignment(Qt.AlignCenter)
        self.timelapse.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h_layout = QHBoxLayout()
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.valueChanged.connect(self.set_frame)
        self.slider.setRange(0, len(self.frames)-1)
        self.timestamp = QLabel()

        h_layout.addWidget(self.play_pause_btn)
        h_layout.addWidget(self.reset_btn)
        h_layout.addWidget(self.slider)
        h_layout.addWidget(self.timestamp)

        layout.addWidget(self.timelapse)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.setInterval(1000 / self.fps)
        self.timer.start()
        self.show_thumbnail()

    def set_video(self):
        pass

    @Slot()
    def update_frame(self):
        if self.tl_running:
            if self.current_frame < len(self.frames):
                self.show_thumbnail()
                self.current_frame += 1
            else:
                self.toggle_play_pause()
                self.timer.stop()

    @Slot()
    def toggle_play_pause(self):
        if self.tl_running:
            self.tl_running = False
            self.play_pause_btn.setText("Play")
        else:
            self.tl_running = True
            self.play_pause_btn.setText("Pause")
            if not self.timer.isActive():
                # self.timer.timeout.connect(self.update_frame)
                self.timer.setInterval(1000 / self.fps)
                self.timer.start()

    @Slot()
    def reset(self):
        self.current_frame = 0
        self.show_thumbnail()

    def show_thumbnail(self):
        frame = self.frames[self.current_frame]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = image.scaled(self.timelapse.size() * 0.9, Qt.KeepAspectRatio)
        self.timelapse.setPixmap(QPixmap.fromImage(image))
        self.update_slider()
        self.timestamp.setText(self.get_timestamp())

    def update_slider(self):
        self.slider.setSliderPosition(self.current_frame)

    def set_frame(self, value):
        self.current_frame = value
        self.show_thumbnail()

    def get_timestamp(self) -> str:
        tot_sec = self.current_frame // self.fps
        min, sec = tot_sec // 60, tot_sec % 60

        timestamp = f"{'{:02d}'.format(min)}:{'{:02d}'.format(sec)}"
        return timestamp

    def save(self):
        filename = QFileDialog.getSaveFileName(None, "Save Timelapse as Video", self.title, "All files (*.*);Video files(*.*)")
        if filename[0] == '':
            return

        vid_height, vid_width, channel = self.frames[0].shape
        size = (vid_width, vid_height)
        output = cv2.VideoWriter(f"{filename[0]}.avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, size)
        for frame in self.frames:
            output.write(frame)
        output.release()

    def get_duration(self):
        tot_sec = len(self.frames) // self.fps
        min, sec = tot_sec // 60, tot_sec % 60

        timestamp = f"{'{:02d}'.format(min)}:{'{:02d}'.format(sec)}"
        return timestamp

    def get_dimensions(self):
        vid_height, vid_width, _ = self.frames[0].shape
        dim = f"{vid_width}x{vid_height}"
        return dim