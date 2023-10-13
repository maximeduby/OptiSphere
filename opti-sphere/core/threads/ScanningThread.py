import os
import time
from configparser import ConfigParser
from datetime import datetime

import cv2
from PySide6.QtCore import QThread, Slot, Signal
from PySide6.QtWidgets import QMessageBox




class ScanningThread(QThread):
    scan_signal = Signal(object, object)
    progress_signal = Signal(str, int)

    def __init__(self, wnd, progress, method, axis, angle=0.0, is_auto=False):
        super().__init__()
        self.running = True
        self.wnd = wnd
        self.progress = progress

        self.method = method
        self.axis = axis
        self.delta_angle = angle
        self.is_auto = is_auto

        self.frames = []
        self.current_angle = 0
        self.directory = "empty"
        self.done = False

    def run(self):
        self.wnd.threads.append(self)
        self.generate_recovery_directory()
        while self.running and self.current_angle <= 360:
            if not self.is_auto:
                dlg = QMessageBox.question(self.wnd, "Scanning", "Ready to save frame?", QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.Cancel)
                if dlg == QMessageBox.StandardButton.Yes:
                    self.progress_signal.emit("Scanning...", int(self.current_angle / 3.6))
                    self.add_frame(self.wnd.main_tab.th.frame)
                    self.current_angle += self.delta_angle
                else:
                    print("oops")
            else:
                self.rotate(self.axis)
                self.progress_signal.emit("Scanning...", int(self.current_angle / 3.6))
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
            self.wnd.ser.send_instruction((self.wnd.sphere.roll + self.current_angle + 180) % 360 - 180, 0, 0)
            self.wnd.sphere.set_rotation(((self.wnd.sphere.roll + self.current_angle + 180) % 360 - 180, 0, 0))
        elif axis == "Pitch":
            self.wnd.ser.send_instruction(0, (self.wnd.sphere.pitch + self.current_angle + 180) % 360 - 180, 0)
            self.wnd.sphere.set_rotation((0, (self.wnd.sphere.pitch + self.current_angle + 180) % 360 - 180, 0))
        self.__waiting_loop()

    @Slot()
    def add_frame(self, frame):
        self.frames.append(frame)
        cv2.imwrite("recovery/" + self.directory + "/frames/" + self.__get_title(), frame)

    def generate_recovery_directory(self):
        self.directory = "scan_" + datetime.now().strftime("%Y%m%d_%H-%M-%S")
        try:
            location = os.path.join("resources", self.directory)
            os.mkdir(os.path.join(location))
            os.mkdir(os.path.join(location, "frames"))
            config = ConfigParser()
            config['SCAN'] = {
                'name': self.directory,
                'nb_frames': str(int(360/self.delta_angle + 1)),
                'method': self.method,
                'axis': self.axis,
                'delta_angle': str(self.delta_angle),
            }
            with open(f'{location}/CONFIG.INI', 'w') as configfile:
                config.write(configfile)
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
        print("Done received")

    def __waiting_loop(self):
        while self.running:
            if self.wnd.ser.is_done:
                self.wnd.ser.is_done = False
                return

    def stop(self):
        self.running = False
        self.wait()
