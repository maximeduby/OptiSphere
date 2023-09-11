import glob
import sys

import serial
from PySide6.QtCore import Signal, QObject

from config import BAUD_RATE
from core.threads.SerialThread import SerialThread


class SerialCom(serial.Serial):
    SOP = b'\x01'  # Start Of Packet
    EOP = b'\x04'  # End Of Packet
    DLE = b'\x10'  # Data Link Escape
    SEP = b'\x1f'  # DATA SEPARATOR

    INSTRUCTION = b'\x20'  # instruction to RPi
    COMMAND = b'\x21'  # command to RPi
    RESPONSE = b'\x22'  # response from RPi
    ERROR = b'\x23'  # Error from RPi
    ALL_DONE = b'\x24'

    def __init__(self, port=None):
        super().__init__(
            port=port,
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        self.th = None
        self.print_signal_holder = SerialSignalHolder()

    def available_port(self):
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

    def send_instruction(self, roll, pitch, yaw):
        roll, pitch, yaw = (bytes(str(i), 'utf-8') for i in (roll, pitch, yaw))
        packet = self.SOP + self.INSTRUCTION + roll + self.SEP + pitch + self.SEP + yaw + self.EOP

        self.th = SerialThread(self, packet)
        self.th.response_signal.connect(self.handle_response)
        self.th.start()

    def send_command(self, command):
        packet = self.SOP + self.COMMAND + bytes(command, 'utf-8') + self.EOP

        self.th = SerialThread(self, packet)
        self.th.response_signal.connect(self.handle_response)
        self.th.start()

    def handle_response(self, category, content):
        self.print_signal_holder.print_signal.emit(category, content)
        if category == self.ALL_DONE:
            self.th.waiting = False
        elif category == self.RESPONSE:
            response = content.decode('utf-8')
            print(response)
        elif category == self.ERROR:
            error = content.decode('utf-8')
            print("Error:", error)


class SerialSignalHolder(QObject):
    print_signal = Signal(bytes, bytes)
