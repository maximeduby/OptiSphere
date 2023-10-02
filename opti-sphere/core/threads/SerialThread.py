from PySide6.QtCore import QThread, Signal
from serial import SerialException


class SerialThread(QThread):
    response_signal = Signal(bytes, bytes)

    def __init__(self, serial, packet, threads):
        super().__init__()
        self.ser = serial
        self.packet = packet
        self.reading = True
        self.threads = threads

    def run(self):
        try:
            self.threads.append(self)
            if not self.ser.isOpen():
                print("Serial Not opened")
                return
            print("Packet sent:", self.packet)
            self.ser.write(self.packet)
            self.ser.is_done = False
            while self.reading:
                if self.ser.read(1) == self.ser.SOP:
                    category = self.ser.read(1)
                    content = self.ser.read_until(self.ser.EOP)[:-1]  # removing EOP byte
                    print(f"Packet Received:\n\tCategory: {category}\n\tContent: {content}")
                    self.response_signal.emit(category, content)
                    self.ser.signal_holder.print_signal.emit(category, content)
                    if category == self.ser.ALL_DONE:
                        self.ser.is_done = True
                        self.reading = False
                        print("[Done]")
        except Exception as e:
            print("Error with the serial Exception", e)
        self.threads.remove(self)
        print(self.threads)

    def stop(self):
        self.reading = False
        self.wait()
