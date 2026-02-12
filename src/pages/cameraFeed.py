from __future__ import annotations

from typing import List

import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from src.config.config import FRAME_HEIGHT, FRAME_WIDTH
from src.logic.cameraManager import CameraDevice, CameraManager

CAMERA_FEED_TEXTURE_REGISTRY_TAG = "camera_feed_texture_registry"
CAMERA_FEED_TEXTURE_TAG = "camera_feed_texture"
CAMERA_FEED_WINDOW_TAG = "camera_feed_window"
CAMERA_FEED_STATUS_TAG = "camera_feed_status"

_camera_manager = CameraManager()
_frame_buffer = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 4), dtype=np.float32)
_frame_buffer[:, :, 3] = 1.0

_status_message = "No camera selected."


def create_camera_feed_window() -> None:
    if not dpg.does_item_exist(CAMERA_FEED_TEXTURE_REGISTRY_TAG):
        with dpg.texture_registry(show=False, tag=CAMERA_FEED_TEXTURE_REGISTRY_TAG):
            dpg.add_raw_texture(
                width=FRAME_WIDTH,
                height=FRAME_HEIGHT,
                default_value=_frame_buffer.ravel(),
                format=dpg.mvFormat_Float_rgba,
                tag=CAMERA_FEED_TEXTURE_TAG,
            )

    if dpg.does_item_exist(CAMERA_FEED_WINDOW_TAG):
        return

    # with dpg.window(
    #     label="Live Camera Feed",
    #     tag=CAMERA_FEED_WINDOW_TAG,
    #     width=FRAME_WIDTH + 40,
    #     height=FRAME_HEIGHT + 110,
    # ):
    #     dpg.add_text(
    #         default_value=_status_message, tag=CAMERA_FEED_STATUS_TAG, wrap=FRAME_WIDTH
    #     )
    #     dpg.add_separator()
    #     dpg.add_image(CAMERA_FEED_TEXTURE_TAG, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    with dpg.child_window(
        label="Live Camera Feed",
        tag=CAMERA_FEED_WINDOW_TAG,
        parent="cameraFeedCell",
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        dpg.add_text(
            default_value=_status_message, tag=CAMERA_FEED_STATUS_TAG, wrap=FRAME_WIDTH
        )
        dpg.add_separator()
        dpg.add_image(CAMERA_FEED_TEXTURE_TAG, width=FRAME_WIDTH, height=FRAME_HEIGHT)


def list_available_cameras() -> List[CameraDevice]:
    return _camera_manager.list_available_cameras()


def get_selected_camera_index():
    return _camera_manager.selected_index


def select_camera(index: int) -> bool:
    success, message = _camera_manager.select_camera(index)
    set_status_message(message)

    if not success:
        _clear_feed_texture()

    return success


def set_status_message(message: str) -> None:
    global _status_message
    _status_message = message

    if dpg.does_item_exist(CAMERA_FEED_STATUS_TAG):
        dpg.set_value(CAMERA_FEED_STATUS_TAG, message)


def toggle_camera_feed_window(sender, app_data, user_data) -> None:
    if not dpg.does_item_exist(CAMERA_FEED_WINDOW_TAG):
        return

    dpg.configure_item(CAMERA_FEED_WINDOW_TAG, show=bool(app_data))


def update_camera_feed() -> None:
    if not dpg.does_item_exist(CAMERA_FEED_TEXTURE_TAG):
        return

    frame = _camera_manager.read_frame()
    if frame is None:
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if rgb_frame.shape[1] != FRAME_WIDTH or rgb_frame.shape[0] != FRAME_HEIGHT:
        rgb_frame = cv2.resize(
            rgb_frame, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_LINEAR
        )

    _frame_buffer[:, :, :3] = rgb_frame.astype(np.float32) / 255.0
    dpg.set_value(CAMERA_FEED_TEXTURE_TAG, _frame_buffer.ravel())


def shutdown_camera_feed() -> None:
    _camera_manager.release_camera()


def _clear_feed_texture() -> None:
    _frame_buffer[:, :, :3] = 0.0
    if dpg.does_item_exist(CAMERA_FEED_TEXTURE_TAG):
        dpg.set_value(CAMERA_FEED_TEXTURE_TAG, _frame_buffer.ravel())
