from PySide6.QtCore import Qt, Slot
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
        self.model.itemChanged.connect(self.update_selected_data)

        for string in items:
            item = QStandardItem(string)
            item.setCheckable(True)
            item.setEditable(False)
            self.model.appendRow(item)
        self.listView.setModel(self.model)

        self.open_button = QPushButton(text='Open', objectName="accept-btn")
        self.open_button.setEnabled(False)
        self.open_button.setMinimumWidth(100)
        self.discard_button = QPushButton(text='Discard', objectName="reject-btn")
        self.discard_button.setMinimumWidth(100)
        self.select_all_button = QPushButton(text='Select All', objectName="reject-btn")
        self.select_all_button.setMinimumWidth(100)
        self.unselect_all_button = QPushButton(text='Unselect All', objectName="reject-btn")
        self.unselect_all_button.setMinimumWidth(100)

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

    def open_selection(self):  # get all items checked
        self.choices = [self.model.item(i).text()
                        for i in range(self.model.rowCount())
                        if self.model.item(i).checkState() == Qt.CheckState.Checked]
        self.accept()

    def select_all(self):  # check all items available
        for i in range(self.model.rowCount()):
            self.model.item(i).setCheckState(Qt.CheckState.Checked)

    def unselect_all(self):  # uncheck all items available
        for i in range(self.model.rowCount()):
            self.model.item(i).setCheckState(Qt.CheckState.Unchecked)

    @Slot()
    def update_selected_data(self):
        for index in range(self.model.rowCount()):
            if self.model.item(index).checkState() == Qt.CheckState.Checked:
                self.open_button.setEnabled(True)
                return
        self.open_button.setEnabled(False)

