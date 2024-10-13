import cv2
import threading

class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.frame = None
        self.is_running = False
        self.lock = threading.Lock()

    def open_camera(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Camera with index {self.camera_index} could not be opened.")

    def start(self):
        if self.is_running:
            return
        self.open_camera()
        self.is_running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                self.stop()

    def get_frame(self):
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            else:
                return None

    def take_picture(self, save_path):
        frame = self.get_frame()
        frame = cv2.flip(frame, 1)
        if frame is not None:
            cv2.imwrite(save_path, frame)
            return True
        return False

    def list_cameras(max_cameras=10):
        available_cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

    def change_camera(self, camera_index):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.camera_index = camera_index
        self.start()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.cap = None
