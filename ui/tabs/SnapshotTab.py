import cv2
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFileDialog, QMessageBox


class SnapshotTab(QWidget):
    def __init__(self, frame, title):
        super().__init__()
        self.frame = frame
        self.title = title
        layout = QVBoxLayout()
        self.snapshot = QLabel()
        self.snapshot.setAlignment(Qt.AlignCenter)
        self.snapshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.snapshot)

        self.setLayout(layout)

    @Slot()
    def set_image(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = image.scaled(self.snapshot.size(), Qt.KeepAspectRatio)
        self.snapshot.setPixmap(QPixmap.fromImage(image))

    def save(self):
        print("Save file")
        filename = QFileDialog.getSaveFileName(None, "Save Image", self.title, "Image (*.jpg *.png)")
        if filename[0] == '':
            return
        cv2.imwrite(filename[0], self.frame)
