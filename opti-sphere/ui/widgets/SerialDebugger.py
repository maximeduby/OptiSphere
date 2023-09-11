from PySide6.QtCore import Slot, Signal
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
        if command == "":
            return
        self.input.clear()
        self.console.setTextColor("blue")
        self.console.append(">>> " + command)
        self.wnd.ser.send_command(command)

    @Slot(bytes, bytes)
    def handle_print_signal(self, category, response):
        if category == self.wnd.ser.ALL_DONE:
            self.console.setTextColor("white")
            self.console.append("[STATUS: Finished]")
        else:
            self.console.setTextColor("white" if category == self.wnd.ser.RESPONSE else "red")
            self.console.append(response)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.wnd.tools_menu.actions()[0].setEnabled(True)
