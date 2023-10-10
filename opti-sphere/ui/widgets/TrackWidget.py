from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, \
    QTableWidget, QTableWidgetItem, QAbstractItemView, QComboBox


class TrackWidget(QWidget):
    update_signal = Signal(str)

    def __init__(self, track):
        super().__init__()
        self.setObjectName("widget-container")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.track = track

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 15, 20, 15)

        # header
        header = QLabel(text='Track', objectName="header")
        header.setAlignment(Qt.Alignment.AlignCenter)

        # track name
        name_layout = QHBoxLayout()
        name_legend = QLabel(text="Name", objectName="legend")
        self.name = QLineEdit(objectName="name")
        self.name.setPlaceholderText("Enter the track name")
        self.name.setText(self.track.title)
        self.name.returnPressed.connect(lambda: self.save_name(self.name.text()))
        name_layout.addWidget(name_legend)
        name_layout.addWidget(self.name)

        # track details
        details_widget = QWidget(objectName="details")
        details_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        details_layout = QHBoxLayout()
        details_layout.setAlignment(Qt.Alignment.AlignCenter)
        details_layout.setSpacing(20)
        details_layout.setContentsMargins(10, 3, 10, 3)
        distance = QLabel(self.calculate_dist())
        mode = QLabel(self.track.info[1])
        details_layout.addWidget(distance)
        details_layout.addWidget(mode)
        details_widget.setLayout(details_layout)

        # description
        desc_layout = QVBoxLayout()
        desc_layout.setSpacing(5)
        desc_legend = QLabel(text="Description", objectName="legend")
        description = QTextEdit(objectName="desc")
        description.setReadOnly(True)
        description.setTextColor("#8c8c8c")
        description.setText(self.track.info[2] if self.track.info[2] else "No description")
        desc_layout.addWidget(desc_legend)
        desc_layout.addWidget(description)

        # data table
        table_layout = QVBoxLayout()
        table_layout.setSpacing(5)
        data_layout = QHBoxLayout()
        table_legend = QLabel(text="Data", objectName="legend")
        table_legend.setFixedWidth(100)
        self.data_format= QComboBox()
        self.data_format.view().parentWidget().setStyleSheet(
            'background-color: #151415; border-radius: 5px; padding: 1px 0px;')
        self.data_format.update()
        self.data_format.addItems(["Spherical format (R,θ,φ)", "Cartesian format (x,y,z)"])
        self.data_format.currentTextChanged.connect(self.update_format)
        data_layout.addWidget(table_legend)
        data_layout.addWidget(self.data_format)
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["R (cm)", "θ (deg)", "φ (deg)", "Time"])
        self.table.selectionModel().selectionChanged.connect(self.select_cells)
        self.load_data(self.track.track, spherical_format=True)
        table_layout.addLayout(data_layout)
        table_layout.addWidget(self.table)

        layout.addWidget(header)
        layout.addLayout(name_layout)
        layout.addWidget(details_widget)
        layout.addLayout(desc_layout)
        layout.addLayout(table_layout)
        layout.addStretch()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def save_name(self, new_name):
        self.track.title = new_name
        self.update_signal.emit(new_name)
        self.name.clearFocus()

    def calculate_dist(self):
        dist = 0
        for i in range(1, len(self.track.track)):
            dist += self.track.track[i].get_distance(self.track.track[i-1])
        return "%0.2f cm" % dist

    def load_data(self, track, spherical_format=True):
        self.table.setRowCount(len(track))
        for i, data in enumerate(track):
            a, b, c = data.coords if spherical_format else data.get_cartesian()
            d = data.time
            self.table.setItem(i, 0, QTableWidgetItem("{:0.1f}".format(a)))
            self.table.setItem(i, 1, QTableWidgetItem("{:0.3f}".format(b)))
            self.table.setItem(i, 2, QTableWidgetItem("{:0.3f}".format(c)))
            self.table.setItem(i, 3, QTableWidgetItem(str(d)))

    @Slot()
    def select_cells(self):
        self.track.spatial_tracking.sel_points = set([i.row() for i in self.table.selectedItems()])
        self.track.spatial_tracking.update()

    @Slot()
    def update_format(self):
        if self.data_format.currentIndex() == 0:
            self.table.setHorizontalHeaderLabels(["R (cm)", "θ (deg)", "φ (deg)", "Time"])
            self.load_data(self.track.track, spherical_format=True)
        else:
            self.table.setHorizontalHeaderLabels(["x (cm)", "y (cm)", "z (cm)", "Time"])
            self.load_data(self.track.track, spherical_format=False)

