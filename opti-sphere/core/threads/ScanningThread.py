import os
import time
from datetime import datetime

import cv2
from PySide6.QtCore import QThread, Slot, Signal

from core.threads.SnapshotThread import SnapshotThread


class ScanningThread(QThread):
    scan_signal = Signal(object, object)

    def __init__(self, wnd, method, axis, angle=0.0, is_auto=False):
        super().__init__()
        self.running = True
        self.wnd = wnd

        self.method = method
        self.axis = axis
        self.delta_angle = angle
        self.is_auto = is_auto

        self.frames = []
        self.current_angle = -180
        self.directory = "empty"
        self.done = False

    def run(self):
        self.wnd.threads.append(self)
        self.generate_recovery_directory()
        while self.running and self.current_angle < 180:
            self.wnd.ser.signal_holder.done_signal.connect(self.set_done())
            self.rotate(self.axis)
            time.sleep(1)
            self.add_frame(self.wnd.main_tab.th.frame)
            self.current_angle += self.delta_angle
            print(self.current_angle)
        info = (
            self.directory,
            self.method,
            self.axis,
            self.delta_angle,
            self.is_auto
        )
        self.scan_signal.emit(self.frames, info)
        self.wnd.threads.remove(self)

    def rotate(self, axis):
        if axis == "Roll":
            self.wnd.ser.send_instruction(self.current_angle, 0, 0)
        elif axis == "Pitch":
            self.wnd.ser.send_instruction(0, self.current_angle, 0)
        self.__waiting_loop()

    @Slot()
    def add_frame(self, frame):
        self.frames.append(frame)
        cv2.imwrite("recovery/" + self.directory + "/" + self.__get_title(), frame)

    def generate_recovery_directory(self):
        self.directory = "scan_" + datetime.now().strftime("%Y%m%d_%H-%M-%S")
        try:
            os.mkdir(os.path.join("recovery", self.directory))
        except FileExistsError or FileNotFoundError as e:
            print(e)

    def __get_title(self):
        string = "unknown.tiff"
        if self.axis == "Roll":
            string = "A{:04d}".format(len(self.frames)) + "_" + datetime.now().strftime("%Y%m%d_%H-%M-%S") + ".tiff"
        elif self.axis == "Pitch":
            string = "B{:04d}".format(len(self.frames)) + "_" + datetime.now().strftime("%Y%m%d_%H-%M-%S") + ".tiff"
        return string

    @Slot()
    def set_done(self):
        self.done = True

    def __waiting_loop(self):
        while self.running:
            if self.done:
                self.done = False
                return

    def stop(self):
        self.running = False
        print("stopstopstopstopstopstopstopstopstopstopstopstopstop")
        self.wait()
