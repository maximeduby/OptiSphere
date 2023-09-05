from PySide6.QtGui import QScreen, QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QLineEdit, QApplication, QWidget
from serial import SerialException
from unidecode import unidecode


class SerialTool(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.setWindowTitle("Serial Communication Tool")
        self.setGeometry(0, 0, 400, 500)
        geometry = self.frameGeometry()
        geometry.moveCenter(QScreen.availableGeometry(QApplication.primaryScreen()).center())
        self.move(geometry.topLeft())

        self.wnd = wnd

        layout = QVBoxLayout()

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setTabStopDistance(20)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command here")
        self.input.returnPressed.connect(lambda: self.send_command(self.input.text()))

        layout.addWidget(self.console)
        layout.addWidget(self.input)
        self.setLayout(layout)

    def send_command(self, command):
        if command == "":
            return
        self.input.clear()
        command = unidecode(command)
        self.wnd.ser.write(b'%s\n' % bytes(command, "ascii"))
        try:
            data = self.wnd.ser.read_until("\n").decode('ascii').strip()
            self.console.append(data.strip("\n"))
            print(data)
        except SerialException:
            print("Error with serial connection")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.wnd.tools_menu.actions()[0].setEnabled(True)