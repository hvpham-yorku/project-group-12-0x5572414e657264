import os

import cv2
import numpy as np
import dearpygui.dearpygui as dpg

from src.database.model_managers import get_aisles_by_store, get_all_stores
from src.database.model_managers import add_aisle, delete_aisle
from src.database.models import Aisle
from src.pages import logWindow
from src.logic import singleton

SINGLETON = singleton.Singleton()
DATABASE_VIDEOS_DIR = SINGLETON.get_databaseVideoFolder()

WINDOW_TAG = "camera_zone_window"
VIDEO_DROPDOWN_TAG = "camera_zone_video_dropdown"
STORE_DROPDOWN_TAG = "camera_zone_store_dropdown"
ZONE_LIST_TAG = "camera_zone_list"

PREVIEW_TEXTURE_TAG = "camera_zone_preview_texture"
PREVIEW_TEXTURE_REGISTRY_TAG = "camera_zone_texture_registry"
PREVIEW_IMAGE_WIDGET_TAG = "camera_zone_preview_image"

DEFAULT_ZONE_SIZE = (120, 90)
MOVE_STEP = 10
RESIZE_STEP = 10

ZONES: list[dict[str, int]] = []
SELECTED_ZONE_INDEX = 0
SELECTED_VIDEO_PATH: str | None = None
STORE_LABEL_TO_ID: dict[str, int] = {}


def _list_database_videos() -> list[str]:
    if not os.path.isdir(DATABASE_VIDEOS_DIR):
        return []
    allowed = {".mp4", ".mov", ".avi", ".mkv"}
    files = [
        f
        for f in os.listdir(DATABASE_VIDEOS_DIR)
        if os.path.splitext(f)[1].lower() in allowed
    ]
    return sorted(files)


def _get_store_options() -> list[str]:
    stores = get_all_stores()
    if not stores:
        return []
    options: list[str] = []
    STORE_LABEL_TO_ID.clear()
    for store in stores:
        label = f"{store.store_id} - {store.name or 'Unnamed Store'}"
        options.append(label)
        STORE_LABEL_TO_ID[label] = store.store_id
    return options


def refresh_store_dropdowns() -> None:
    store_options = _get_store_options()
    default_store = store_options[0] if store_options else ""

    if dpg.does_item_exist(STORE_DROPDOWN_TAG):
        current = dpg.get_value(STORE_DROPDOWN_TAG)
        dpg.configure_item(STORE_DROPDOWN_TAG, items=store_options)
        dpg.set_value(
            STORE_DROPDOWN_TAG,
            current if current in store_options else default_store,
        )


def _get_selected_store_id() -> int | None:
    if not dpg.does_item_exist(STORE_DROPDOWN_TAG):
        return None
    label = dpg.get_value(STORE_DROPDOWN_TAG)
    return STORE_LABEL_TO_ID.get(label)


def _get_selected_video_path() -> str | None:
    return SELECTED_VIDEO_PATH


def _set_selected_video_by_name(name: str | None) -> None:
    global SELECTED_VIDEO_PATH
    if not name:
        SELECTED_VIDEO_PATH = None
        return
    SELECTED_VIDEO_PATH = os.path.join(DATABASE_VIDEOS_DIR, name)


def _zone_label(idx: int, zone: dict[str, int]) -> str:
    return f"Zone {idx + 1}: x={zone['x']} y={zone['y']} w={zone['w']} h={zone['h']}"


def _refresh_zone_list() -> None:
    if not dpg.does_item_exist(ZONE_LIST_TAG):
        return

    items = [_zone_label(i, z) for i, z in enumerate(ZONES)]
    dpg.configure_item(ZONE_LIST_TAG, items=items)

    if not items:
        return

    global SELECTED_ZONE_INDEX
    if SELECTED_ZONE_INDEX >= len(items):
        SELECTED_ZONE_INDEX = len(items) - 1

    dpg.set_value(ZONE_LIST_TAG, items[SELECTED_ZONE_INDEX])


def _get_selected_zone() -> dict[str, int] | None:
    if not ZONES:
        return None
    if SELECTED_ZONE_INDEX < 0 or SELECTED_ZONE_INDEX >= len(ZONES):
        return None
    return ZONES[SELECTED_ZONE_INDEX]


def _ensure_texture_registry() -> None:
    if not dpg.does_item_exist(PREVIEW_TEXTURE_REGISTRY_TAG):
        with dpg.texture_registry(tag=PREVIEW_TEXTURE_REGISTRY_TAG):
            pass


def _ensure_preview_texture() -> None:
    _ensure_texture_registry()
    if dpg.does_item_exist(PREVIEW_TEXTURE_TAG):
        return
    dpg.add_dynamic_texture(
        width=1,
        height=1,
        default_value=[0.0, 0.0, 0.0, 1.0],
        tag=PREVIEW_TEXTURE_TAG,
        parent=PREVIEW_TEXTURE_REGISTRY_TAG,
    )


def _set_preview_texture_from_frame(frame: np.ndarray) -> None:
    _ensure_preview_texture()

    frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    height, width = frame_rgba.shape[:2]
    data = (frame_rgba.astype("float32") / 255.0).reshape(-1)

    if dpg.does_item_exist(PREVIEW_TEXTURE_TAG):
        config = dpg.get_item_configuration(PREVIEW_TEXTURE_TAG)
        current_w = config.get("width", width)
        current_h = config.get("height", height)
        if current_w != width or current_h != height:
            parent = (
                dpg.get_item_parent(PREVIEW_IMAGE_WIDGET_TAG)
                if dpg.does_item_exist(PREVIEW_IMAGE_WIDGET_TAG)
                else None
            )
            if dpg.does_item_exist(PREVIEW_IMAGE_WIDGET_TAG):
                dpg.delete_item(PREVIEW_IMAGE_WIDGET_TAG)
            dpg.delete_item(PREVIEW_TEXTURE_TAG)
            dpg.add_dynamic_texture(
                width=width,
                height=height,
                default_value=data,
                tag=PREVIEW_TEXTURE_TAG,
                parent=PREVIEW_TEXTURE_REGISTRY_TAG,
            )
            if parent is not None:
                dpg.add_image(
                    PREVIEW_TEXTURE_TAG,
                    tag=PREVIEW_IMAGE_WIDGET_TAG,
                    parent=parent,
                )
                _resize_preview_to_window()
        else:
            dpg.set_value(PREVIEW_TEXTURE_TAG, data)
    else:
        dpg.add_dynamic_texture(
            width=width,
            height=height,
            default_value=data,
            tag=PREVIEW_TEXTURE_TAG,
            parent=PREVIEW_TEXTURE_REGISTRY_TAG,
        )


def _resize_preview_to_window() -> None:
    if not dpg.does_item_exist(WINDOW_TAG):
        return
    if not dpg.does_item_exist(PREVIEW_IMAGE_WIDGET_TAG):
        return

    width = dpg.get_item_width(WINDOW_TAG)
    height = dpg.get_item_height(WINDOW_TAG)
    new_width = max(1, int(width) - 20)
    new_height = max(1, int(height) - 260)
    dpg.set_item_width(PREVIEW_IMAGE_WIDGET_TAG, new_width)
    dpg.set_item_height(PREVIEW_IMAGE_WIDGET_TAG, new_height)


def _get_first_frame(video_path: str) -> np.ndarray | None:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return frame


def _update_preview() -> None:
    frame = None
    video_path = _get_selected_video_path()
    if video_path and os.path.exists(video_path):
        frame = _get_first_frame(video_path)

    if frame is None:
        frame = np.zeros((360, 640, 3), dtype=np.uint8)

    for idx, zone in enumerate(ZONES):
        x = max(0, int(zone["x"]))
        y = max(0, int(zone["y"]))
        w = max(1, int(zone["w"]))
        h = max(1, int(zone["h"]))
        color = (0, 255, 0) if idx != SELECTED_ZONE_INDEX else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    _set_preview_texture_from_frame(frame)
    _resize_preview_to_window()


def _set_selected_zone_index_from_label(label: str) -> None:
    global SELECTED_ZONE_INDEX
    items = [_zone_label(i, z) for i, z in enumerate(ZONES)]
    if label in items:
        SELECTED_ZONE_INDEX = items.index(label)


def callback_select_video(sender, app_data, user_data):
    _set_selected_video_by_name(app_data)
    _update_preview()


def callback_select_zone(sender, app_data, user_data):
    if not app_data:
        return
    _set_selected_zone_index_from_label(app_data)
    _update_preview()


def callback_load_zones(sender, app_data, user_data):
    store_id = _get_selected_store_id()
    if store_id is None:
        return

    aisles = get_aisles_by_store(store_id)
    ZONES.clear()
    for aisle in aisles:
        width = max(1, int(aisle.top_right_x - aisle.bottom_left_x))
        height = max(1, int(aisle.top_right_y - aisle.bottom_left_y))
        ZONES.append(
            {
                "x": int(aisle.bottom_left_x),
                "y": int(aisle.bottom_left_y),
                "w": width,
                "h": height,
            }
        )

    global SELECTED_ZONE_INDEX
    SELECTED_ZONE_INDEX = 0 if ZONES else 0
    _refresh_zone_list()
    _update_preview()
    silent = isinstance(user_data, dict) and user_data.get("silent")
    if not silent:
        logWindow.addLog(0, f"Loaded {len(ZONES)} zones from store {store_id}.")


def callback_add_zone(sender, app_data, user_data):
    ZONES.append({"x": 0, "y": 0, "w": DEFAULT_ZONE_SIZE[0], "h": DEFAULT_ZONE_SIZE[1]})
    global SELECTED_ZONE_INDEX
    SELECTED_ZONE_INDEX = len(ZONES) - 1
    _refresh_zone_list()
    if store_options:
        dpg.set_value(STORE_DROPDOWN_TAG, default_store)
        callback_load_zones(None, None, {"silent": True})
    else:
        _update_preview()


def callback_remove_zone(sender, app_data, user_data):
    if not ZONES:
        return
    ZONES.pop(SELECTED_ZONE_INDEX)
    _refresh_zone_list()
    _update_preview()


def _move_zone(dx: int, dy: int) -> None:
    zone = _get_selected_zone()
    if not zone:
        return
    zone["x"] = max(0, zone["x"] + dx)
    zone["y"] = max(0, zone["y"] + dy)
    _refresh_zone_list()
    _update_preview()


def _resize_zone(dw: int, dh: int) -> None:
    zone = _get_selected_zone()
    if not zone:
        return
    zone["w"] = max(1, zone["w"] + dw)
    zone["h"] = max(1, zone["h"] + dh)
    _refresh_zone_list()
    _update_preview()


def callback_done(sender, app_data, user_data):
    if not ZONES:
        logWindow.addLog(1, "No zones to save.")
        return

    store_id = _get_selected_store_id()
    if store_id is None:
        logWindow.addLog(1, "No store selected. Cannot save zones.")
        return

    # Replace existing zones for the store
    for aisle in get_aisles_by_store(store_id):
        delete_aisle(aisle.aisle_id)

    for zone in ZONES:
        add_aisle(
            Aisle(
                store_id=store_id,
                bottom_left_x=int(zone["x"]),
                bottom_left_y=int(zone["y"]),
                top_right_x=int(zone["x"] + zone["w"]),
                top_right_y=int(zone["y"] + zone["h"]),
                vertical=False,
            )
        )

    logWindow.addLog(0, f"Saved {len(ZONES)} zones to store {store_id}.")


def create_camera_zone_window():
    if dpg.does_item_exist(WINDOW_TAG):
        dpg.show_item(WINDOW_TAG)
        _refresh_zone_list()
        _update_preview()
        return

    _ensure_preview_texture()

    videos = _list_database_videos()
    default_video = videos[0] if videos else ""
    store_options = _get_store_options()
    default_store = store_options[0] if store_options else ""
    _set_selected_video_by_name(default_video if default_video else None)

    with dpg.window(
        tag=WINDOW_TAG,
        label="Camera Zones Setup",
        width=900,
        height=600,
    ):
        dpg.add_text("Camera Zone Setup")

        with dpg.group(horizontal=True):
            dpg.add_text("Merged Video:")
            dpg.add_combo(
                items=videos,
                default_value=default_video,
                tag=VIDEO_DROPDOWN_TAG,
                callback=callback_select_video,
                width=300,
            )
            dpg.add_text("Store:")
            dpg.add_combo(
                items=store_options,
                default_value=default_store,
                tag=STORE_DROPDOWN_TAG,
                callback=callback_load_zones,
                width=220,
            )
            dpg.add_button(label="Done", callback=callback_done)

        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_listbox(
                items=[],
                tag=ZONE_LIST_TAG,
                num_items=5,
                width=250,
                callback=callback_select_zone,
            )
            with dpg.group():
                dpg.add_button(label="Add Zone", callback=callback_add_zone)
                dpg.add_button(label="Remove Zone", callback=callback_remove_zone)
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Up", callback=lambda s, a, u: _move_zone(0, -MOVE_STEP)
                    )
                    dpg.add_button(
                        label="Down", callback=lambda s, a, u: _move_zone(0, MOVE_STEP)
                    )
                    dpg.add_button(
                        label="Left", callback=lambda s, a, u: _move_zone(-MOVE_STEP, 0)
                    )
                    dpg.add_button(
                        label="Right", callback=lambda s, a, u: _move_zone(MOVE_STEP, 0)
                    )
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Wider",
                        callback=lambda s, a, u: _resize_zone(RESIZE_STEP, 0),
                    )
                    dpg.add_button(
                        label="Narrower",
                        callback=lambda s, a, u: _resize_zone(-RESIZE_STEP, 0),
                    )
                    dpg.add_button(
                        label="Taller",
                        callback=lambda s, a, u: _resize_zone(0, RESIZE_STEP),
                    )
                    dpg.add_button(
                        label="Shorter",
                        callback=lambda s, a, u: _resize_zone(0, -RESIZE_STEP),
                    )

        dpg.add_spacer(height=10)
        dpg.add_image(PREVIEW_TEXTURE_TAG, tag=PREVIEW_IMAGE_WIDGET_TAG)

        with dpg.item_handler_registry() as handler:
            dpg.add_item_resize_handler(
                callback=lambda s, a, u: _resize_preview_to_window()
            )
        dpg.bind_item_handler_registry(WINDOW_TAG, handler)

    _refresh_zone_list()
    _update_preview()
