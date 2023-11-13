from PySide6.QtCore import QThread, Signal, QTimer


class SerialThread(QThread):  # thread processing the writing and reading of data during serial communication
    response_signal = Signal(bytes, bytes)

    def __init__(self, serial, packet, threads):
        super().__init__()
        self.ser = serial
        self.packet = packet
        self.reading = True
        self.threads = threads

        self.timer = QTimer()  # Timer for serial timeout
        self.timer.timeout.connect(lambda: [
            self.response_signal.emit(self.ser.ERROR, b"Serial communication timeout"),
            self.ser.signal_holder.print_signal.emit(self.ser.ERROR, b"Serial communication timeout")
        ])

    def run(self):
        try:
            self.threads.append(self)  # add current thread to list of threads
            if not self.ser.isOpen():  # check if serial port is open
                print("Serial Not opened")
                return
            print("Packet sent:", self.packet)
            self.ser.write(self.packet)  # send the packet to RPi
            self.ser.is_done = False
            while self.reading:  # wait for response of RPi
                if self.ser.in_waiting and self.ser.read(1) == self.ser.SOP:
                    self.timer.stop()
                    category = self.ser.read(1)
                    content = self.ser.read_until(self.ser.EOP)[:-1]  # removing EOP byte
                    print(f"Packet Received:\n\tCategory: {category}\n\tContent: {content}")
                    self.response_signal.emit(category, content)
                    self.ser.signal_holder.print_signal.emit(category, content)
                    if category == self.ser.ALL_DONE:
                        self.ser.is_done = True
                        self.reading = False
                        print("[Done]")
                    else:
                        self.timer.start(10000)
        except Exception as e:
            print("Error with the serial Exception", e)
        self.threads.remove(self)
        print(self.threads)

    def stop(self):  # stop the thread
        self.reading = False
        self.timer.stop()
        self.wait()
