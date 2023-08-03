import cv2
from PySide6.QtCore import QThread, Signal, QTimer

from configuration import ROOT_DIR


# class VideoThread(QThread):
#     vid_signal = Signal(object)
#
#     def __init__(self, device_index, fps, vid_counter):
#         super().__init__()
#         self.device_index = device_index
#         self.fps = 30
#         self.vid_counter = vid_counter
#         self.recorded_frames = []
#         self.cam = cv2.VideoCapture(self.device_index)
#         self.running = True
#         self.path = f"{ROOT_DIR}/cache/videos/video_{self.vid_counter}.avi"
#         self.width, self.height = cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT
#         (self.width, self.height) = (1280, 360)
#
#
#     def run(self):
#
#         self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
#         self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
#         self.cam.set(cv2.CAP_PROP_FPS, self.fps)
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         output = cv2.VideoWriter(self.path, fourcc, self.fps, (self.width, self.height))
#
#         while self.running:
#             ret, frame = self.cam.read()
#             if ret:
#                 output.write(frame)
#         self.vid_signal.emit(self)
#         print("end")
#         self.cam.release()
#         output.release()

class VideoThread(QThread):
    vid_signal = Signal(object)
    def __init__(self, device_index, fps , counter):
        super().__init__()
        self.device_index = device_index
        self.cam = cv2.VideoCapture(self.device_index)
        self.running = True
        self.recorded_frames = []

    def run(self) -> None:
        while self.running:
            ret, frame = self.cam.read()
            if not ret:
                break
            self.recorded_frames.append(frame)
        self.vid_signal.emit(self)
        self.cam.release()

