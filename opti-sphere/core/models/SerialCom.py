import glob
import sys

import serial
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QMessageBox

from config import BAUD_RATE
from core.threads.SerialThread import SerialThread


class SerialCom(serial.Serial):  # defines the properties and functions of a serial communication
    SOP = b'\x01'  # Start Of Packet
    EOP = b'\x04'  # End Of Packet
    DLE = b'\x10'  # Data Link Escape
    SEP = b'\x1f'  # DATA SEPARATOR

    INSTRUCTION = b'\x20'  # instruction to RPi
    COMMAND = b'\x21'  # command to RPi
    RESPONSE = b'\x22'  # response from RPi
    ERROR = b'\x23'  # Error from RPi
    ALL_DONE = b'\x24'  # Transmission can stop
    ROT = b'\x25'  # rotation mode for instruction
    SCAN = b'\x26'  # scan mode for instruction

    is_done = False  # set the transmission as over

    def __init__(self, wnd, port=None):
        super().__init__(
            port=port,
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        self.signal_holder = SignalHolder()
        self.wnd = wnd
        self.th = None

    def available_port(self):  # return all the available ports (USB ports) detected by the computer
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.usb*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def send_instruction(self, mode, arg1, arg2, arg3):  # send instruction to RPi according to the protocol format
        arg1, arg2, arg3 = (bytes(str(i), 'utf-8') for i in (arg1, arg2, arg3))
        packet = self.SOP + self.INSTRUCTION + mode + self.SEP + arg1 + self.SEP + arg2 + self.SEP + arg3 + self.EOP

        if self.th and self.th.isRunning():
            self.th.stop()
        self.th = SerialThread(self, packet, self.wnd.threads)
        self.th.response_signal.connect(self.handle_response)
        self.th.start()

    def send_command(self, command):  # send command to RPi
        packet = self.SOP + self.COMMAND + bytes(command, 'utf-8') + self.EOP

        if self.th and self.th.isRunning():
            self.th.stop()
        self.th = SerialThread(self, packet, self.wnd.threads)
        self.th.response_signal.connect(self.handle_response)
        self.th.start()

    def handle_response(self, category, content):  # act accordingly to the type of response from RPi
        if category == self.ALL_DONE:
            print("DONE")
        elif category == self.RESPONSE:
            response = content.decode('utf-8')
            print("Response: ", response)
        elif category == self.ERROR:
            error = content.decode('utf-8')
            print("Error:", error)
            self.th.stop()
            QMessageBox.critical(self.wnd, "Error", error, QMessageBox.StandardButton.Ok)
            self.wnd.sphere.undo_rot()
            self.reset_input_buffer()


class SignalHolder(QObject):
    print_signal = Signal(bytes, bytes)
    done_signal = Signal()
