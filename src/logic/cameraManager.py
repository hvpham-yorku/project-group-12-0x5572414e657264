"""
Cross-platform camera enumeration and selection utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
import platform
from typing import List, Optional, Tuple

import cv2

from src.config.config import CAMERA_SCAN_MAX_INDEX, FRAME_HEIGHT, FRAME_WIDTH


@dataclass(frozen=True)
class CameraDevice:
    index: int
    label: str
    backend: int


class CameraManager:
    def __init__(
        self,
        max_probe_index: int = CAMERA_SCAN_MAX_INDEX,
        frame_width: int = FRAME_WIDTH,
        frame_height: int = FRAME_HEIGHT,
    ) -> None:
        self.max_probe_index = max_probe_index
        self.frame_width = frame_width
        self.frame_height = frame_height

        self._selected_index: Optional[int] = None
        self._selected_backend: Optional[int] = None
        self._capture: Optional[cv2.VideoCapture] = None

        self._backend_priority = self._build_backend_priority()
        self._backend_names = self._build_backend_name_map()

    @property
    def selected_index(self) -> Optional[int]:
        return self._selected_index

    @property
    def selected_backend(self) -> Optional[int]:
        return self._selected_backend

    def list_available_cameras(self) -> List[CameraDevice]:
        cameras: List[CameraDevice] = []

        for index in range(self.max_probe_index):
            if self._is_selected_camera_open(index):
                backend = self._selected_backend if self._selected_backend is not None else cv2.CAP_ANY
                cameras.append(
                    CameraDevice(
                        index=index,
                        label=self._build_label(index=index, backend=backend),
                        backend=backend,
                    )
                )
                continue

            backend = self._probe_camera(index)
            if backend is None:
                continue

            cameras.append(
                CameraDevice(
                    index=index,
                    label=self._build_label(index=index, backend=backend),
                    backend=backend,
                )
            )

        return cameras

    def select_camera(self, index: int) -> Tuple[bool, str]:
        if self._is_selected_camera_open(index):
            return True, f"{self._build_label(index, self._selected_backend)} already selected."

        capture, backend = self._open_camera(index)
        if capture is None or backend is None:
            return False, f"Could not open camera index {index}."

        if self._capture is not None:
            self._capture.release()

        self._capture = capture
        self._selected_index = index
        self._selected_backend = backend
        return True, f"Selected {self._build_label(index=index, backend=backend)}."

    def read_frame(self):
        if self._capture is None or not self._capture.isOpened():
            return None

        success, frame = self._capture.read()
        if not success:
            return None

        return frame

    def release_camera(self) -> None:
        if self._capture is not None:
            self._capture.release()

        self._capture = None
        self._selected_index = None
        self._selected_backend = None

    def _is_selected_camera_open(self, index: int) -> bool:
        return (
            self._selected_index == index
            and self._capture is not None
            and self._capture.isOpened()
        )

    def _build_backend_priority(self) -> List[int]:
        system_name = platform.system().lower()

        if system_name == "windows":
            backend_names = ["CAP_DSHOW", "CAP_MSMF", "CAP_ANY"]
        elif system_name == "darwin":
            backend_names = ["CAP_AVFOUNDATION", "CAP_ANY"]
        else:
            backend_names = ["CAP_V4L2", "CAP_GSTREAMER", "CAP_ANY"]

        backends: List[int] = []
        for name in backend_names:
            value = getattr(cv2, name, None)
            if isinstance(value, int) and value not in backends:
                backends.append(value)

        if cv2.CAP_ANY not in backends:
            backends.append(cv2.CAP_ANY)

        return backends

    def _build_backend_name_map(self) -> dict:
        mapping = {}
        label_map = {
            "CAP_ANY": "Auto",
            "CAP_DSHOW": "DirectShow",
            "CAP_MSMF": "Media Foundation",
            "CAP_AVFOUNDATION": "AVFoundation",
            "CAP_V4L2": "V4L2",
            "CAP_GSTREAMER": "GStreamer",
        }
        for backend_attr, label in label_map.items():
            backend_value = getattr(cv2, backend_attr, None)
            if isinstance(backend_value, int):
                mapping[backend_value] = label
        return mapping

    def _backend_label(self, backend: Optional[int]) -> str:
        if backend is None:
            return "Unknown"
        return self._backend_names.get(backend, f"Backend {backend}")

    def _build_label(self, index: int, backend: Optional[int]) -> str:
        return f"Camera {index} [{self._backend_label(backend)}]"

    def _probe_camera(self, index: int) -> Optional[int]:
        capture, backend = self._open_camera(index)
        if capture is None or backend is None:
            return None

        capture.release()
        return backend

    def _open_camera(self, index: int) -> Tuple[Optional[cv2.VideoCapture], Optional[int]]:
        for backend in self._backend_priority:
            capture = cv2.VideoCapture(index, backend)
            if capture is None or not capture.isOpened():
                if capture is not None:
                    capture.release()
                continue

            self._set_capture_preferences(capture)
            success, _ = capture.read()
            if not success:
                capture.release()
                continue

            return capture, backend

        return None, None

    def _set_capture_preferences(self, capture: cv2.VideoCapture) -> None:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        if hasattr(cv2, "CAP_PROP_BUFFERSIZE"):
            capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def __del__(self) -> None:
        self.release_camera()
