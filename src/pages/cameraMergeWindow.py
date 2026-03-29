import os
import shutil
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np

import dearpygui.dearpygui as dpg
from src.actions import videoImportDialog
from src.logic import singleton
from src.pages import logWindow
from src.logic import mediaEditor
from src.database.model_managers import get_all_stores, add_camera
from src.database.models import Camera
from src.utils.paths import get_resource_path

SINGLETON = singleton.Singleton()
MERGED_PREVIEW_PATH = os.path.join(
    SINGLETON.get_tempFolderPictures(), "merged_preview.png"
)
PREVIEW_TEXTURE_TAG = "camera_merge_preview_texture"
PREVIEW_TEXTURE_REGISTRY_TAG = "camera_merge_texture_registry"
PREVIEW_IMAGE_WIDGET_TAG = "camera_merge_preview_image"
DATABASE_VIDEOS_DIR = SINGLETON.get_databaseVideoFolder()
STORE_DROPDOWN_TAG = "camera_merge_store_dropdown"
STORE_PLACEHOLDER = "-- Select Store --"
STORE_LABEL_TO_ID: dict[str, int] = {}
PREVIEW_TEX_WIDTH = 1280
PREVIEW_TEX_HEIGHT = 720
PREVIEW_TEX_DATA = [0.0, 0.0, 0.0, 1.0] * (PREVIEW_TEX_WIDTH * PREVIEW_TEX_HEIGHT)
_PREVIEW_PENDING_DATA = None
_PREVIEW_UPDATE_SCHEDULED = False


def feature_not_implemented(sender):
    print(f"Menu Item: {sender}")
    logWindow.addLog(0, "THIS FEATURE IS NOT YET IMPLEMENTED")


def callback_select_video_files(sender, app_data, user_data):
    SINGLETON.set_selectedVideo(user_data, app_data)
    refreshMergedImage()


def callback_delete_video_file(sender, app_data, user_data):
    SINGLETON.delete_video(user_data)
    callback_refresh_table_entries(sender, app_data, user_data)
    refreshMergedImage()


def _get_file_states():
    file_states = SINGLETON.get_selectedVideos()
    if not isinstance(file_states, dict):
        return {}
    return file_states


def _add_table_row(file, file_states):
    file_states = file_states if isinstance(file_states, dict) else {}
    file_state = file_states.get(file)
    if not isinstance(file_state, dict):
        file_state = {"state": False, "coor": [0, 0]}

    with dpg.table_row(parent="videoFiles"):
        dpg.add_text(os.path.basename(str(file)))
        dpg.add_checkbox(
            callback=callback_select_video_files,
            default_value=bool(file_state.get("state", False)),
            user_data=file,
        )
        for label, direction in [("Up","up"),("Down","down"),("Left","left"),("Right","right")]:
            dpg.add_button(label=label, user_data=[direction, file], callback=callback_moveCoord)
        dpg.add_button(label="Delete", user_data=file, callback=callback_delete_video_file)

def callback_refresh_table_entries(sender, app_data, user_data):
    file_states = _get_file_states()

    table_rows = dpg.get_item_children("videoFiles", 1) or []
    for row in table_rows:
        dpg.delete_item(row)

    for file in SINGLETON.get_all_temp_files():
        _add_table_row(file, file_states)


def callback_video_import_dialog(sender, app_data, user_data):
    videoImportDialog.open_video_import_dialog(sender, app_data, user_data)


def _get_store_options() -> list[str]:
    stores = get_all_stores()
    STORE_LABEL_TO_ID.clear()
    options = [STORE_PLACEHOLDER]
    for store in stores:
        label = f"{store.store_id} - {store.name or 'Unnamed Store'}"
        options.append(label)
        STORE_LABEL_TO_ID[label] = store.store_id
    return options


def _get_selected_store_id() -> int | None:
    if not dpg.does_item_exist(STORE_DROPDOWN_TAG):
        return None
    label = dpg.get_value(STORE_DROPDOWN_TAG)
    return STORE_LABEL_TO_ID.get(label)


def refresh_store_dropdown() -> None:
    if not dpg.does_item_exist(STORE_DROPDOWN_TAG):
        return
    options = _get_store_options()
    current = dpg.get_value(STORE_DROPDOWN_TAG)
    dpg.configure_item(STORE_DROPDOWN_TAG, items=options)
    dpg.set_value(
        STORE_DROPDOWN_TAG,
        current if current in options else STORE_PLACEHOLDER,
    )


def callback_merge_selected_videos(sender, app_data, user_data):
    store_id = _get_selected_store_id()
    if store_id is None:
        logWindow.addLog(1, "Please select a store before pressing Done.")
        return

    file_states = SINGLETON.get_selectedVideos()
    selected = [
        (path, state["coor"]) for path, state in file_states.items() if state["state"]
    ]

    if not selected:
        logWindow.addLog(1, "No videos selected to merge.")
        return

    video_paths = [p for p, _ in selected]
    coordinates = [tuple(coor) for _, coor in selected]

    os.makedirs(DATABASE_VIDEOS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATABASE_VIDEOS_DIR, f"merged_{timestamp}.mp4")

    try:
        mediaEditor.merge_and_blend_videos(video_paths, coordinates, output_path)
        persisted_path = os.path.normpath(os.path.abspath(output_path))
        add_camera(Camera(store_id=store_id, relative_file_path=persisted_path))
        logWindow.addLog(0, f"Merged video saved to {output_path}")
    except Exception as exc:
        logWindow.addLog(2, f"Failed to merge videos: {exc}")


def _resize_preview_to_window() -> None:
    if not dpg.does_item_exist("camera_merge_window"):
        return
    if not dpg.does_item_exist(PREVIEW_IMAGE_WIDGET_TAG):
        return

    width = dpg.get_item_width("camera_merge_window")
    height = dpg.get_item_height("camera_merge_window")
    new_width = max(1, int(width) - 20)
    new_height = max(1, int(height) - 20)
    dpg.set_item_width(PREVIEW_IMAGE_WIDGET_TAG, new_width)
    dpg.set_item_height(PREVIEW_IMAGE_WIDGET_TAG, new_height)


def _set_preview_texture(image_path: str) -> None:
    if not dpg.does_item_exist(PREVIEW_TEXTURE_REGISTRY_TAG):
        return

    data = _load_image_rgba(image_path)
    if data is None:
        return

    _queue_preview_update(data)


def refreshMergedImage():

    file_states = _get_file_states()
    out_dir = SINGLETON.get_tempFolderPictures()
    os.makedirs(out_dir, exist_ok=True)

    image_paths = []
    image_coords = []
    for file_path in file_states.keys():
        if file_states[file_path]["state"]:
            base = Path(file_path).stem
            output_path = os.path.join(out_dir, f"{base}_frame.png")
            mediaEditor.extract_first_frame(file_path, output_path)
            image_paths.append(output_path)
            image_coords.append(file_states[file_path]["coor"])

    merged_output_path = os.path.join(out_dir, "merged_preview.png")
    if len(image_paths):
        blended = mediaEditor.merge_and_blend_images(
            image_paths,
            image_coords,
            # [file_states[key]["coor"] for key in file_states.keys()],
            merged_output_path,
        )
        if blended is not None:
            _queue_preview_update(_bgr_to_texture_data(blended))
        else:
            _set_preview_texture(merged_output_path)
    else:
        _set_preview_texture(_ensure_preview_image_file())


def callback_moveCoord(sender, app_data, user_data):
    direction = user_data[0]
    file = user_data[1]
    file_states = _get_file_states()

    if file in file_states and file_states[file]["state"]:
        SINGLETON.update_selectedVideoCoordinates(file, direction)
    callback_refresh_table_entries(sender, app_data, user_data)
    refreshMergedImage()
    # print(image_paths)
    # print()
    # print(SINGLETON.get_selectedVideos())


def create_camera_merge_window():
    if dpg.does_item_exist("camera_merge_window"):
        dpg.show_item("camera_merge_window")
        callback_refresh_table_entries(None, None, None)
        return

    if not dpg.does_item_exist(PREVIEW_TEXTURE_REGISTRY_TAG):
        with dpg.texture_registry(tag=PREVIEW_TEXTURE_REGISTRY_TAG):
            pass

    initial_preview = (
        MERGED_PREVIEW_PATH
        if os.path.exists(MERGED_PREVIEW_PATH)
        else _ensure_preview_image_file()
    )
    if not dpg.does_item_exist(PREVIEW_TEXTURE_TAG):
        data = _load_image_rgba(initial_preview)
        if data is None:
            data = PREVIEW_TEX_DATA
        dpg.add_dynamic_texture(
            width=PREVIEW_TEX_WIDTH,
            height=PREVIEW_TEX_HEIGHT,
            default_value=data,
            tag=PREVIEW_TEXTURE_TAG,
            parent=PREVIEW_TEXTURE_REGISTRY_TAG,
        )

    with dpg.window(
        tag="camera_merge_window",
        label="Camera Feeds Setup",
        width=900,
        height=450,
    ):
        dpg.add_text("Camera Video Feed Setup")
        store_options = _get_store_options()
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Import Video File",
                callback=videoImportDialog.open_video_import_dialog,
            )
            dpg.add_text("Store:")
            dpg.add_combo(
                items=store_options,
                default_value=STORE_PLACEHOLDER,
                tag=STORE_DROPDOWN_TAG,
                width=220,
            )
            dpg.add_button(
                label="Done",
                callback=callback_merge_selected_videos,
            )
        refresh_store_dropdown()
        with dpg.table(
            tag="videoFiles",
            show=True,
            header_row=True,
            resizable=True,
            borders_innerV=True,
            borders_outerV=True,
        ):
            dpg.add_table_column(label="File Name", init_width_or_weight=0.80)
            dpg.add_table_column(label="Merge?", init_width_or_weight=0.10)
            dpg.add_table_column(label="Up", init_width_or_weight=0.10)
            dpg.add_table_column(label="Down", init_width_or_weight=0.10)
            dpg.add_table_column(label="Left", init_width_or_weight=0.10)
            dpg.add_table_column(label="Right", init_width_or_weight=0.10)
            dpg.add_table_column(label="Delete", init_width_or_weight=0.10)
        callback_refresh_table_entries(None, None, None)

        dpg.add_spacer(height=10)
        dpg.add_image(PREVIEW_TEXTURE_TAG, tag=PREVIEW_IMAGE_WIDGET_TAG)

        with dpg.item_handler_registry() as handler:
            dpg.add_item_resize_handler(
                callback=lambda s, a, u: _resize_preview_to_window()
            )
        dpg.bind_item_handler_registry("camera_merge_window", handler)
        _resize_preview_to_window()
        _set_preview_texture(_ensure_preview_image_file())


def _ensure_preview_image_file() -> str:
    data_path = os.path.join(SINGLETON.get_tempFolderPictures(), "refPic.png")
    if os.path.exists(data_path):
        return data_path

    resource_path = get_resource_path("assets", "pictures", "refPic.png")
    if os.path.exists(resource_path):
        try:
            shutil.copy2(resource_path, data_path)
            return data_path
        except Exception:
            pass

    # Fallback: generate a simple black placeholder
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    placeholder = np.zeros((64, 64, 3), dtype=np.uint8)
    cv2.imwrite(data_path, placeholder)
    return data_path


def _load_image_rgba(image_path: str):
    if not os.path.exists(image_path):
        return None
    img = cv2.imread(image_path)
    if img is None:
        return None
    img = _resize_for_preview(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    data = (img.astype("float32") / 255.0).reshape(-1).tolist()
    return data


def _resize_for_preview(img):
    h, w = img.shape[:2]
    if w < PREVIEW_TEX_WIDTH or h < PREVIEW_TEX_HEIGHT:
        interp = cv2.INTER_LINEAR
    else:
        interp = cv2.INTER_AREA
    return cv2.resize(img, (PREVIEW_TEX_WIDTH, PREVIEW_TEX_HEIGHT), interpolation=interp)


def _bgr_to_texture_data(img):
    img = _resize_for_preview(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    return (img.astype("float32") / 255.0).reshape(-1).tolist()


def _queue_preview_update(data) -> None:
    global _PREVIEW_PENDING_DATA, _PREVIEW_UPDATE_SCHEDULED
    _PREVIEW_PENDING_DATA = data
    if _PREVIEW_UPDATE_SCHEDULED:
        return
    _PREVIEW_UPDATE_SCHEDULED = True
    frame = dpg.get_frame_count() + 1
    dpg.set_frame_callback(frame, _apply_pending_preview)


def _apply_pending_preview(sender=None, app_data=None):
    global _PREVIEW_PENDING_DATA, _PREVIEW_UPDATE_SCHEDULED
    _PREVIEW_UPDATE_SCHEDULED = False
    if _PREVIEW_PENDING_DATA is None:
        return
    if dpg.does_item_exist(PREVIEW_TEXTURE_TAG):
        if len(_PREVIEW_PENDING_DATA) == len(PREVIEW_TEX_DATA):
            PREVIEW_TEX_DATA[:] = _PREVIEW_PENDING_DATA
            dpg.set_value(PREVIEW_TEXTURE_TAG, PREVIEW_TEX_DATA)
    _PREVIEW_PENDING_DATA = None
