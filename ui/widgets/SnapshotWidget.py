from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from ui.dialogs.EditNameDialog import EditNameDialog


class SnapshotWidget(QWidget):
    def __init__(self, snapshot, wnd, tab_index):
        super().__init__()
        self.snapshot = snapshot
        self.wnd = wnd
        self.tab_index = tab_index

        layout = QVBoxLayout()

        section_header = QLabel("Snapshot")
        h_layout = QHBoxLayout()
        name_legend = QLabel("Name:")
        self.name_text = QLabel(self.snapshot.title)
        edit_name_btn = QPushButton("Edit")
        edit_name_btn.clicked.connect(self.edit_name)

        h_layout.addWidget(name_legend)
        h_layout.addWidget(self.name_text)
        h_layout.addWidget(edit_name_btn)

        layout.addWidget(section_header)
        layout.addLayout(h_layout)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    @Slot()
    def edit_name(self):
        former_name = self.snapshot.title
        dialog = EditNameDialog(former_name)
        if dialog.exec():
            new_name = dialog.get_name() if dialog.get_name() != "" else former_name
            self.snapshot.title = new_name
            self.wnd.tabs.setTabText(self.tab_index, new_name)
            self.name_text.setText(new_name)

        # else:
        #     new_name = former_name
