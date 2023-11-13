from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QScreen, QCloseEvent, QShortcut
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QLineEdit, QApplication, QWidget
from serial import SerialException


class SerialTerminal(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.setWindowTitle("Serial Terminal")
        self.setGeometry(0, 0, 400, 500)
        self.setObjectName("ser-debugger")
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        self.wnd = wnd
        self.wnd.ser.signal_holder.print_signal.connect(self.handle_print_signal)

        layout = QVBoxLayout()

        self.console = QTextEdit(objectName="console")
        self.console.setReadOnly(True)
        self.console.setTabStopDistance(20)

        self.input = QLineEdit(objectName="command")
        self.input.setPlaceholderText("Enter command here")
        self.input.returnPressed.connect(lambda: self.return_input(self.input.text()))

        layout.addWidget(self.console)
        layout.addWidget(self.input)
        self.setLayout(layout)

        self.last_commands = []
        self.command_index = 0

        QShortcut(Qt.Key_Up, self, self.up)
        QShortcut(Qt.Key_Down, self, self.down)

    def return_input(self, command):  # triggered when 'Enter' key is pressed
        if command == "stop":  # stop the current serial thread
            self.wnd.ser.th.stop()
            self.input.clear()
            return
        if command == "" or (self.wnd.ser.th and self.wnd.ser.th.isRunning()):  # empty data not sent
            return
        self.input.clear()
        self.console.setTextColor("#3C7BFF")
        self.console.append(">>> " + command)
        if command == "clear":  # clear console
            self.console.clear()
            return
        self.last_commands.append(command)
        self.command_index = 0
        try:
            self.wnd.ser.send_command(command)  # send command to RPi
        except SerialException:
            self.console.setTextColor("#FF4E4E")
            self.console.append("Error when sending the command")

    @Slot(bytes, bytes)
    def handle_print_signal(self, category, response):  # change text color according to data received from RPi
        if category == self.wnd.ser.ALL_DONE:
            self.console.setTextColor("#7A7A7A")
            self.console.append("[Done]")
        else:
            self.console.setTextColor("white" if category == self.wnd.ser.RESPONSE else "#FF4E4E")
            self.console.append(response.decode('utf-8'))

    def closeEvent(self, event: QCloseEvent) -> None:
        self.wnd.tools_menu.actions()[0].setEnabled(True)
        self.hide()

    def up(self):  # navigate to previous sent commands
        if self.last_commands:
            self.command_index = min(self.command_index + 1, len(self.last_commands))
            i = len(self.last_commands) - self.command_index
            self.input.clear()
            self.input.setText(self.last_commands[i])

    def down(self):  # navigate back to latest sent commands
        if self.last_commands:
            self.command_index = max(self.command_index - 1, 0)
            i = len(self.last_commands) - self.command_index
            self.input.clear()
            if i != len(self.last_commands):
                self.input.setText(self.last_commands[i])

