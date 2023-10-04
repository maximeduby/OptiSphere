import cv2
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QComboBox


class TrackingTab(QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd

        layout = QVBoxLayout()
        self.roi_btn = QPushButton("Select ROI", objectName="action-btn")
        self.roi_btn.clicked.connect(self.roi_selection)

        mode_layout = QHBoxLayout()
        mode_legend = QLabel(text='Tracking Mode', objectName='legend')
        mode_legend.setFixedWidth(100)
        self.mode = QComboBox()
        self.mode.view().parentWidget().setStyleSheet(
            'background-color: #151415; border-radius: 5px; padding: 1px 0px;')
        self.mode.update()

        self.mode.addItems(["Surface of Sphere"])
        mode_layout.addWidget(mode_legend)
        mode_layout.addWidget(self.mode)

        self.tracking_btn = QPushButton("Start Tracking", objectName="action-btn")
        self.tracking_btn.clicked.connect(self.init_tracking)

        layout.addWidget(self.roi_btn)
        layout.addLayout(mode_layout)
        layout.addWidget(self.tracking_btn)
        layout.addStretch()
        self.setLayout(layout)

        self.box = None
        self.dimension = (-1, -1)
        self.tracking_offset = 300
        self.pix_deg_ratio = 150
        self.track = []
        self.can_rotate = True

    @Slot()
    def roi_selection(self):
        if self.wnd.main_tab.camera_feed.selection_mode:
            self.wnd.main_tab.camera_feed.selection_mode = False
            self.wnd.main_tab.camera_feed.selection.hide()
            self.roi_btn.setText("Select ROI")
        else:
            self.wnd.main_tab.is_tracking_on = False
            self.wnd.main_tab.camera_feed.selection_mode = True
            self.roi_btn.setText("Cancel ROI")
            self.wnd.main_tab.camera_feed.box_signal.connect(self.set_box)

    @Slot()
    def set_box(self, box):
        self.box = box

    @Slot()
    def init_tracking(self):
        if self.wnd.main_tab.is_tracking_on:
            self.wnd.main_tab.is_tracking_on = False
            self.tracking_btn.setText("Start Tracking")
            self.box = None
        else:
            if self.box:
                self.roi_selection()
                self.wnd.main_tab.tracker = cv2.TrackerCSRT_create()
                self.wnd.main_tab.tracker.init(self.wnd.main_tab.th.frame, self.box)
                self.wnd.main_tab.is_tracking_on = True
                self.tracking_btn.setText("Stop Tracking")
                self.wnd.main_tab.box_signal.connect(self.handle_tracking)
                self.dimension = (self.wnd.main_tab.th.frame.shape[1], self.wnd.main_tab.th.frame.shape[0])
                self.tracking_offset = int(self.dimension[1] * 2/6)
                self.track = []
            else:
                print("No ROI selected")

    @Slot()
    def handle_tracking(self, box):
        x = int(box[0] + box[2]/2)
        y = int(box[1] + box[3]/2)
        self.can_rotate = self.wnd.ser.is_done
        print("Pos:", x, y)
        print(box[0], box[1])
        print("Dimensions", self.dimension)
        distance = (self.dimension[0]/2 - x, y - self.dimension[1]/2)
        print("DISTANCE", distance, "OFFSET", self.tracking_offset)
        if self.can_rotate and (abs(distance[0]) > self.tracking_offset or abs(distance[1]) > self.tracking_offset):
            print("Is offset")
            rot = self.wnd.sphere.get_rotation()
            new_rot = (
                round(rot[0] + (distance[0] / self.pix_deg_ratio), 1),
                round(rot[1] + (distance[1] / self.pix_deg_ratio), 1),
                rot[2]
            )
            self.can_rotate = False
            self.wnd.ser.send_instruction(*new_rot)
            self.wnd.sphere.set_rotation(new_rot)




