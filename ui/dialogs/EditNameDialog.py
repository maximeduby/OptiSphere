from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout


class EditNameDialog(QDialog):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.setWindowTitle("Edit Name")

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(self.name)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.name_edit)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def get_name(self):
        return self.name_edit.text()