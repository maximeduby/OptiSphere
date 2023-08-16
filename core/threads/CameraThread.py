import cv2
from PySide6.QtCore import QThread, Signal


class CameraThread(QThread):
    cam_signal = Signal(object)

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.running = True

        self.mouse = None # in [0,1]
        self.dim = None
        self.zoom = 1
        self.f_coords = (0,0) # coordinates of the zoom frame relative to the captured frame

    def run(self):
        cam = cv2.VideoCapture(self.device_id)
        self.dim = (cam.get(cv2.CAP_PROP_FRAME_WIDTH), cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(self.dim)
        while self.running:
            ret, frame = cam.read()
            if ret:
                frame = self.adjust(frame)
                self.cam_signal.emit(frame)
        cam.release()

    def stop(self):
        self.running = False
        self.wait()

    def adjust(self, frame):
        if self.zoom > 1.0:
            new_dim = (int(frame.shape[1] / self.zoom), int(frame.shape[0] / self.zoom))

            anchor_x = int(self.mouse[0] * self.dim[0] + self.f_coords[0])
            anchor_x = int(max(anchor_x, new_dim[0] * self.mouse[0]))
            anchor_x = int(min(anchor_x, frame.shape[1] - (new_dim[0] * (1 - self.mouse[0]))))

            anchor_y = int(self.mouse[1] * self.dim[1] + self.f_coords[1])
            anchor_y = int(max(anchor_y, new_dim[1] * self.mouse[1]))
            anchor_y = int(min(anchor_y, frame.shape[0] - (new_dim[1] * (1 - self.mouse[1]))))

            start_x = int(anchor_x - new_dim[0] * self.mouse[0])
            end_x = int(anchor_x + new_dim[0] * (1 - self.mouse[0]))
            start_y = int(anchor_y - new_dim[1] * self.mouse[1])
            end_y = int(anchor_y + new_dim[1] * (1 - self.mouse[1]))

            image = frame[start_y:end_y, start_x:end_x]

            self.dim = new_dim
            self.f_coords = (start_x + 1, start_y + 1)


            return image


        else:
            return frame

