import os
import time
from configparser import ConfigParser
from datetime import datetime

import cv2
from PySide6.QtCore import QThread, Slot, Signal


class ScanningThread(QThread):  # thread processing the scanning process
    scan_signal = Signal(object, object)
    progress_signal = Signal(str, int)

    def __init__(self, wnd, progress, method, axis, angle=0.0, is_auto=False):
        super().__init__()
        self.running = True
        self.wnd = wnd
        self.progress = progress

        self.method = method  # method of scanning
        self.axis = axis  # axis to scan
        self.delta_angle = angle  # angle to rotate for every capture
        self.is_auto = is_auto  # set the scanning mode to automatic or manual

        self.frames = []  # stores the frames captured during the scanning
        self.current_angle = 0  # keep track of the angle of rotation between 0° to 360°
        self.directory = "empty"  # name of directory saving the scanning data

        # process booleans
        self.done = False
        self.ready_for_frame = False
        self.is_canceled = False

    def run(self):
        self.wnd.threads.append(self)  # add new thread to list of threads
        self.generate_recovery_directory()  # create recovery folder
        self.add_frame(self.wnd.main_tab.th.frame)  # add the first frame
        self.progress_signal.emit("Scanning...", int(100 * len(self.frames) / (360 / self.delta_angle + 1)))
        while self.running and self.current_angle < 360:
            if self.current_angle == 0:  # set the scan flag
                flag = 0
            elif self.current_angle + self.delta_angle >= 360:
                flag = 2
            else:
                flag = 1
            self.current_angle += self.delta_angle  # update next angle
            self.rotate(self.axis, flag)  # rotate to corresponding angle
            time.sleep(1)
            while self.running and not self.is_auto:  # wait for capture confirmation
                if self.ready_for_frame:
                    self.ready_for_frame = False
                    break
            self.add_frame(self.wnd.main_tab.th.frame)  # add current frame
            self.progress_signal.emit(  # update progress bar
                "Scanning...", int(100 * len(self.frames)/(360/self.delta_angle + 1))
            )
        if self.is_canceled:  # safety measure when canceling scan
            self.wnd.ser.send_command(f"release {self.axis}")
        else:
            info = (
                self.directory,
                self.method,
                self.axis,
                self.delta_angle,
                self.is_auto
            )
            self.scan_signal.emit(self.frames, info)  # send frames and info of scan to new ScanTab
        self.wnd.threads.remove(self)  # remove current thread to list of threads

    def rotate(self, axis, flag):  # send the instruction to RPi for current rotation
        if axis == "Roll":
            self.wnd.ser.send_instruction(
                self.wnd.ser.SCAN, "roll", (self.wnd.sphere.roll + self.delta_angle + 180) % 360 - 180, flag
            )
            self.wnd.sphere.set_rotation((
                (self.wnd.sphere.roll + self.delta_angle + 180) % 360 - 180,
                self.wnd.sphere.pitch,
                self.wnd.sphere.yaw)
            )
        elif axis == "Pitch":
            self.wnd.ser.send_instruction(
                self.wnd.ser.SCAN, "pitch", (self.wnd.sphere.pitch + self.delta_angle + 180) % 360 - 180, flag
            )
            self.wnd.sphere.set_rotation((
                self.wnd.sphere.roll,
                (self.wnd.sphere.pitch + self.delta_angle + 180) % 360 - 180,
                self.wnd.sphere.yaw)
            )
        self.__waiting_loop()

    @Slot()
    def add_frame(self, frame):  # store and save the frame captured from the current angle of view
        self.frames.append(frame)
        cv2.imwrite("recovery/" + self.directory + "/frames/" + self.__get_title(), frame)

    def generate_recovery_directory(self):  # generate a directory containing the frames captured and a config file
        self.directory = "scan_" + datetime.now().strftime("%Y%m%d_%H-%M-%S")
        try:
            location = os.path.join("recovery", self.directory)
            os.mkdir(os.path.join(location))
            os.mkdir(os.path.join(location, "frames"))
            config = ConfigParser()
            config['SCAN'] = {
                'name': self.directory,
                'nb_frames': str(int(360 / self.delta_angle + 1)),
                'method': self.method,
                'axis': self.axis,
                'delta_angle': str(self.delta_angle),
            }
            with open(f'{location}/CONFIG.INI', 'w') as configfile:
                config.write(configfile)
        except FileExistsError or FileNotFoundError as e:
            print(e)

    def __get_title(self):  # set a specific and indexed title for each frame
        string = "unknown.tiff"
        if self.axis == "Roll":
            string = "A{:04d}".format(len(self.frames)) + "_" + datetime.now().strftime("%Y%m%d_%H-%M-%S") + ".tiff"
        elif self.axis == "Pitch":
            string = "B{:04d}".format(len(self.frames)) + "_" + datetime.now().strftime("%Y%m%d_%H-%M-%S") + ".tiff"
        return string

    @Slot()
    def set_done(self):  # inform the current scanning angle was reached
        self.done = True
        print("Done received")

    def __waiting_loop(self): # wait for current scanning angle to be reached
        while self.running:
            if self.wnd.ser.is_done:
                self.wnd.ser.is_done = False
                return

    def stop(self):
        self.running = False
        self.wait()
