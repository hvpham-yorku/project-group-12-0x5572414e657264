"""
Docstring for logic.cameraManager

This file contains the camera manager to manage live feed
"""

import threading
import cv2

from src.config.config import MAX_CAMERAS
from src.config.config import FRAME_HEIGHT
from src.config.config import FRAME_WIDTH
from src.config.config import TRACK_UPDATE_SECONDS


class CameraManager:
    """
    Docstring for CameraManager
    """

    def __init__(self):
        self.capture = None
        self.camera_index = None
        self.lock = threading.Lock()

    def list_cameras(self, max_index=MAX_CAMERAS):
        available = []
        for index in range(max_index):
            cap = cv2.VideoCapture(index)
            if cap is not None and cap.isOpened():
                available.append(index)
                cap.release()
        return available

    def open(self, index):
        with self.lock:
            if self.capture is not None:
                self.capture.release()
                self.capture = None
            self.camera_index = index
            if index is None:
                return False
            self.capture = cv2.VideoCapture(index)
            if self.capture is None or not self.capture.isOpened():
                self.capture = None
                return False
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return True

    def read(self):
        with self.lock:
            if self.capture is None:
                return None
            ok, frame = self.capture.read()
            if not ok:
                return None
            return frame

    def close(self):
        with self.lock:
            if self.capture is not None:
                self.capture.release()
                self.capture = None
