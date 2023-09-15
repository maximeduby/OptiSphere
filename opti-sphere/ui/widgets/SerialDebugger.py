from PySide6.QtCore import Slot
from PySide6.QtGui import QScreen, QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QLineEdit, QApplication, QWidget
from serial import SerialException

from core.models.SerialCom import SerialCom


class SerialDebugger(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.setWindowTitle("Serial Communication Tool")
        self.setGeometry(0, 0, 400, 500)
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        self.wnd = wnd
        self.wnd.ser.print_signal_holder.print_signal.connect(self.handle_print_signal)

        layout = QVBoxLayout()

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setTabStopDistance(20)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command here")
        self.input.returnPressed.connect(lambda: self.return_input(self.input.text()))

        layout.addWidget(self.console)
        layout.addWidget(self.input)
        self.setLayout(layout)

    def return_input(self, command):
        if command == "" or (self.wnd.ser.th and self.wnd.ser.th.isRunning()):
            return
        self.input.clear()
        self.console.setTextColor("#105BF6")
        self.console.append(">>> " + command)
        try:
            self.wnd.ser.send_command(command)
        except SerialException:
            self.console.setTextColor("red")
            self.console.append("Error when sending the command")

    @Slot(bytes, bytes)
    def handle_print_signal(self, category, response):
        if category == self.wnd.ser.ALL_DONE:
            self.console.setTextColor("#10F65B")
            self.console.append("[STATUS: Finished]")
        else:
            self.console.setTextColor("white" if category == self.wnd.ser.RESPONSE else "red")
            self.console.append(response.decode('utf-8'))

    def closeEvent(self, event: QCloseEvent) -> None:
        self.wnd.tools_menu.actions()[0].setEnabled(True)
