from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QFontMetricsF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit, QTextEdit
from serial import SerialException
from unidecode import unidecode


class ControlWidget(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd
        self.mode = "r"

        layout = QVBoxLayout()
        section_header = QLabel("Control")
        section_header.setAlignment(Qt.Alignment.AlignCenter)
        section_header.setFont(QFont('Arial', 20))

        h_layout = QHBoxLayout()
        self.roll_btn = QPushButton("Roll")
        self.pitch_btn = QPushButton("Pitch")
        self.yaw_btn = QPushButton("Yaw")

        self.yaw_btn.setEnabled(False)

        self.roll_btn.clicked.connect(lambda: self.set_axis("Roll"))
        self.pitch_btn.clicked.connect(lambda: self.set_axis("Pitch"))
        self.yaw_btn.clicked.connect(lambda: self.set_axis("Yaw"))

        h_layout.addWidget(self.roll_btn)
        h_layout.addWidget(self.pitch_btn)
        h_layout.addWidget(self.yaw_btn)

        serial_layout = QVBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter serial command")
        self.input_box.returnPressed.connect(lambda: self.send_command(self.input_box.text()))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setTabStopDistance(20)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.console.clear)

        serial_layout.addWidget(self.console)
        serial_layout.addWidget(self.input_box)
        serial_layout.addWidget(clear_btn)

        layout.addWidget(section_header)
        layout.addLayout(h_layout)
        layout.addLayout(serial_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def set_axis(self, axis):
        match axis:
            case "Roll":
                self.roll_btn.setEnabled(False)
                if self.mode != "r":
                    try:
                        self.wnd.ser.write(b'%s-CW\n' % bytes(self.mode, "utf-8"))
                        self.mode = "r"
                        self.wnd.ser.write(b'ROLL-CCW\n')
                    except SerialException:
                        print("Error: Could not write to serial port")
                        # Alert box to warn writing failed (later)
                        pass
                self.roll_btn.setEnabled(True)

            case "Pitch":
                self.pitch_btn.setEnabled(False)
                if self.mode != "p":
                    try:
                        self.wnd.ser.write(b'%s-CW\n' % bytes(self.mode, "ascii"))
                        self.mode = "p"
                        self.wnd.ser.write(b'PITCH-CCW\n')
                    except SerialException:
                        print("Error: Could not write to serial port")
                        # Alert box to warn writing failed (later)
                        pass

                self.pitch_btn.setEnabled(True)
            case "Yaw":
                pass

    @Slot()
    def send_command(self, command):
        self.input_box.clear()
        command = unidecode(command)
        # self.wnd.ser.write(b'%s\n' % command)
        self.wnd.ser.write(b'%s\n' % bytes(command, "ascii"))
        try:
            data = self.wnd.ser.read_until("\n").decode('ascii').strip()
            self.console.append(data.strip("\n"))
            print(data)
        except SerialException:
            print("Error with serial connection")
