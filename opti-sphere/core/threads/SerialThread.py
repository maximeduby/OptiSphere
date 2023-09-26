from PySide6.QtCore import QThread, Signal
from serial import SerialException


class SerialThread(QThread):
    response_signal = Signal(bytes, bytes)

    def __init__(self, serial, packet, threads):
        super().__init__()
        self.ser = serial
        self.packet = packet
        self.waiting = True
        self.threads = threads

    def run(self):
        self.threads.append(self)
        if not self.ser.isOpen():
            print("Serial Not opened")
            return
        try:
            print("Packet to be sent:", self.packet)
            self.ser.write(self.packet)
        except SerialException:
            print("Error with serial communication when writing")
        while self.waiting:
            try:
                if self.ser.read(1) == self.ser.SOP:
                    category = self.ser.read(1)
                    content = self.ser.read_until(self.ser.EOP)[:-1]  # removing EOP byte
                    # print(f"Packet Received:\n\tCategory: {category}\n\tContent: {content}")
                    self.response_signal.emit(category, content)
                    self.ser.signal_holder.print_signal.emit(category, content)
            except SerialException:
                pass
                # print("Error with serial communication when reading")
                # self.waiting = False
        self.threads.remove(self)
        print(self.threads)

    def stop(self):
        self.waiting = False
        self.wait()
