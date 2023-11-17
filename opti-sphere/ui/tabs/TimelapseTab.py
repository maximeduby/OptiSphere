import cv2
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QLabel, QSlider, QHBoxLayout, QFileDialog, QWidget

from ui.dialogs.SetupScaleDialog import SetupScaleDialog
from ui.tabs.Tab import Tab
from ui.widgets.ImageViewer import ImageViewer
from ui.widgets.ProgressWidget import ProgressWidget
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
        self.timelapse.gv.set_image(self.frames[self.current_frame])

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
    def toggle_play_pause(self):  # play or pause the timelapse video
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
    def update_timelapse(self):  # update displayed frame and other widgets according to current frame index
        if self.is_running:
            if self.current_frame < len(self.frames):
                self.timer.setInterval(1000 / self.fps)
                self.timelapse.gv.set_image(self.frames[self.current_frame])
                self.slider.setSliderPosition(self.current_frame)
                self.timestamp.setText(self.get_timestamp())
                self.current_frame += 1
            else:
                self.toggle_play_pause()
                self.timer.stop()

    def get_timestamp(self):  # return the timestamp of the timelapse video according to current frame index
        tot_sec = self.current_frame // self.fps
        minutes, seconds = tot_sec // 60, tot_sec % 60
        return f"{'{:02d}'.format(minutes)}:{'{:02d}'.format(seconds)}"

    @Slot()
    def set_frame(self, value):  # update displayed frame and timestamp according to slider position
        self.current_frame = value
        self.timelapse.gv.set_image(self.frames[self.current_frame])
        self.timestamp.setText(self.get_timestamp())
        self.slider.setSliderPosition(self.current_frame)

    def get_dimensions(self):  # return frame's dimensions
        vid_height, vid_width, _ = self.frames[0].shape
        dim = f"{vid_width} × {vid_height}"
        return dim

    def get_duration(self):  # return duration of timelapse
        tot_sec = len(self.frames) // self.fps
        minutes, seconds = tot_sec // 60, tot_sec % 60
        return f"{'{:02d}'.format(minutes)}:{'{:02d}'.format(seconds)}"

    def export(self):  # export timelapse as a video to chosen location
        filename = QFileDialog.getSaveFileName(None, "Export Timelapse as Video", self.title, "All files (*.*);Video files(*.*)")
        if filename[0] == '':
            return

        vid_height, vid_width, channel = self.frames[0].shape
        size = (vid_width, vid_height)
        output = cv2.VideoWriter(f"{filename[0]}.avi", cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'), self.fps, size)
        progress = ProgressWidget()
        progress.show()
        for index, frame in enumerate(self.frames):
            output.write(frame)
            progress.update_progress("Exporting...", int(index/len(self.frames) * 100))
        output.release()
        progress.close()

    def resizeEvent(self, event):  # update timelapse frame size according to window size
        self.timelapse.gv.set_image(self.frames[self.current_frame])

    def setup_scale_bar(self):  # set up the scale from the current frame of the timelapse
        dlg = SetupScaleDialog(self.frames[self.current_frame])
        if dlg.exec():
            self.timelapse.pix2mm = dlg.get_ratio()
            ImageViewer.is_scale_bar_visible = True
