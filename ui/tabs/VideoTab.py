import cv2
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout, QSlider


class VideoTab(QWidget):
    # def __init__(self, vid_path, title):
    #     super().__init__()
    #     self.vid_path = vid_path
    #     self.title = title
    #     layout = QVBoxLayout()
    #     self.video = QLabel()
    #     self.video.setAlignment(Qt.AlignCenter)
    #     self.video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    #     layout.addWidget(self.video)
    #
    #     self.setLayout(layout)

    def __init__(self, recorded_frames, title):
        super().__init__()
        self.frames = recorded_frames
        self.title = title
        self.fps = 30
        self.current_frame = 0
        self.vid_running = False

        layout = QVBoxLayout()
        self.video = QLabel()
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

        layout.addWidget(self.video)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.setInterval(1000 / self.fps)
        self.timer.start()
        self.show_thumbnail()

    def set_video(self):
        print(self.frames)

    @Slot()
    def update_frame(self):
        if self.vid_running:
            if self.current_frame < len(self.frames):
                self.show_thumbnail()
                self.current_frame += 1
            else:
                self.toggle_play_pause()
                self.timer.stop()

    @Slot()
    def toggle_play_pause(self):
        if self.vid_running:
            self.vid_running = False
            self.play_pause_btn.setText("Play")
        else:
            self.vid_running = True
            self.play_pause_btn.setText("Pause")
            if not self.timer.isActive():
                # self.timer.timeout.connect(self.update_frame)
                self.timer.start()

    @Slot()
    def reset(self):
        self.current_frame = 0
        self.show_thumbnail()

    def show_thumbnail(self):
        frame = self.frames[self.current_frame]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = image.scaled(self.video.size() * 0.9, Qt.KeepAspectRatio)
        self.video.setPixmap(QPixmap.fromImage(image))
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
