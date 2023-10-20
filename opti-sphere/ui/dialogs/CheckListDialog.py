from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QPushButton, QHBoxLayout, \
    QListView, QVBoxLayout


class CheckListDialog(QDialog):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle("Edit Timelapse Settings")

        self.items = items

        self.model = QStandardItemModel()
        self.listView = QListView()

        for string in items:
            item = QStandardItem(string)
            item.setCheckable(True)
            item.setEditable(False)
            self.model.appendRow(item)
        self.listView.setModel(self.model)

        self.open_button = QPushButton('Open')
        self.discard_button = QPushButton('Discard')
        self.select_all_button = QPushButton('Select All')
        self.unselect_all_button = QPushButton('Unselect All')

        hl = QHBoxLayout()
        hl.addStretch(1)
        hl.addWidget(self.open_button)
        hl.addWidget(self.discard_button)
        hl.addWidget(self.select_all_button)
        hl.addWidget(self.unselect_all_button)

        vl = QVBoxLayout(self)
        vl.addWidget(self.listView)
        vl.addStretch(1)
        vl.addLayout(hl)

        self.setWindowTitle("Recover Unsaved Files")

        self.open_button.clicked.connect(self.open_selection)
        self.discard_button.clicked.connect(self.reject)
        self.select_all_button.clicked.connect(self.select_all)
        self.unselect_all_button.clicked.connect(self.unselect_all)

    def open_selection(self):
        self.choices = [self.model.item(i).text()
                        for i in range(self.model.rowCount())
                        if self.model.item(i).checkState() == Qt.CheckState.Checked]
        self.accept()

    def select_all(self):
        for i in range(self.model.rowCount()):
            self.model.item(i).setCheckState(Qt.CheckState.Checked)

    def unselect_all(self):
        for i in range(self.model.rowCount()):
            self.model.item(i).setCheckState(Qt.CheckState.Unchecked)
