from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit


class SnapshotWidget(QWidget):
    update_signal = Signal(str)

    def __init__(self, snapshot):
        super().__init__()
        self.setObjectName('widget-container')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.snapshot = snapshot

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 15, 20, 15)

        # header
        header = QLabel(text='Snapshot', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # snapshot name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name", objectName="legend")
        self.name = QLineEdit(objectName="name")
        self.name.setPlaceholderText("Enter the snapshot name")
        self.name.setText(self.snapshot.title)
        self.name.returnPressed.connect(lambda: self.save_name(self.name.text()))
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # snapshot details
        details_widget = QWidget(objectName="details")
        details_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        details_layout = QHBoxLayout()
        details_layout.setAlignment(Qt.Alignment.AlignCenter)
        details_layout.setSpacing(20)
        details_layout.setContentsMargins(10, 3, 10, 3)
        dimensions = QLabel(self.snapshot.get_dimensions())
        details_layout.addWidget(dimensions)
        details_widget.setLayout(details_layout)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addWidget(details_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def save_name(self, new_name):  # update snapshot name in tab bar
        self.snapshot.title = new_name
        self.update_signal.emit(new_name)
        self.name.clearFocus()
