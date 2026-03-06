import os
from pathlib import Path
from datetime import datetime

import cv2

import dearpygui.dearpygui as dpg
from src.actions import videoImportDialog
from src.logic import singleton
from src.pages import logWindow
from src.logic import mediaEditor

SINGLETON = singleton.Singleton()
PREVIEW_IMAGE_PATH = os.path.join("assets", "pictures", "refPic.png")
MERGED_PREVIEW_PATH = os.path.join("assets", "pictures", "merged_preview.png")
PREVIEW_TEXTURE_TAG = "camera_merge_preview_texture"
PREVIEW_TEXTURE_REGISTRY_TAG = "camera_merge_texture_registry"
PREVIEW_IMAGE_WIDGET_TAG = "camera_merge_preview_image"
DATABASE_VIDEOS_DIR = os.path.join("assets", "databaseVideos")


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


def callback_refresh_table_entries(sender, app_data, user_data):
    table_rows = dpg.get_item_children("videoFiles", 1) or []
    for row in table_rows:
        dpg.delete_item(row)

    file_states = SINGLETON.get_selectedVideos()
    for file in SINGLETON.get_all_temp_files():
        with dpg.table_row(parent="videoFiles"):
            dpg.add_text(f"{str(file).split("/")[-1]}")
            dpg.add_checkbox(
                callback=callback_select_video_files,
                default_value=file_states.get(file, {"state": False})["state"],
                user_data=file,
            )
            dpg.add_button(
                label="Up",
                user_data=["up", file],
                callback=callback_moveCoord,
            )
            dpg.add_button(
                label="Down",
                user_data=["down", file],
                callback=callback_moveCoord,
            )
            dpg.add_button(
                label="Left",
                user_data=["left", file],
                callback=callback_moveCoord,
            )
            dpg.add_button(
                label="Right",
                user_data=["right", file],
                callback=callback_moveCoord,
            )
            dpg.add_button(
                label="Delete",
                user_data=file,
                callback=callback_delete_video_file,
            )
    # for filePath in file_states.keys():
    #     mediaEditor.extract_first_frame(filePath, SINGLETON.get_tempFolderPictures())
    # mediaEditor.merge_and_blend_images(
    #     [x for x in file_states.keys()],
    #     [file_states[key]["coor"] for key in file_states.keys()],
    #     SINGLETON.get_tempFolderPictures(),
    # )


def callback_video_import_dialog(sender, app_data, user_data):
    videoImportDialog.open_video_import_dialog(sender, app_data, user_data)


def callback_merge_selected_videos(sender, app_data, user_data):
    file_states = SINGLETON.get_selectedVideos()
    selected = [
        (path, state["coor"])
        for path, state in file_states.items()
        if state["state"]
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

    if not os.path.exists(image_path):
        return

    width, height, channels, data = dpg.load_image(image_path)
    if dpg.does_item_exist(PREVIEW_TEXTURE_TAG):
        config = dpg.get_item_configuration(PREVIEW_TEXTURE_TAG)
        current_w = config.get("width", width)
        current_h = config.get("height", height)
        if current_w != width or current_h != height:
            img = cv2.imread(image_path)
            if img is None:
                return
            target_w = max(1, int(current_w))
            target_h = max(1, int(current_h))
            img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            data = (img.astype("float32") / 255.0).reshape(-1)
        dpg.set_value(PREVIEW_TEXTURE_TAG, data)
    else:
        dpg.add_dynamic_texture(
            width=width,
            height=height,
            default_value=data,
            tag=PREVIEW_TEXTURE_TAG,
            parent=PREVIEW_TEXTURE_REGISTRY_TAG,
        )


def refreshMergedImage():

    file_states = SINGLETON.get_selectedVideos()
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
        mediaEditor.merge_and_blend_images(
            image_paths,
            image_coords,
            # [file_states[key]["coor"] for key in file_states.keys()],
            merged_output_path,
        )
        _set_preview_texture(merged_output_path)
    else:
        _set_preview_texture(PREVIEW_IMAGE_PATH)


def callback_moveCoord(sender, app_data, user_data):
    direction = user_data[0]
    file = user_data[1]
    file_states = SINGLETON.get_selectedVideos()

    if file_states[file]["state"]:
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
        else PREVIEW_IMAGE_PATH
    )
    if os.path.exists(initial_preview):
        width, height, channels, data = dpg.load_image(initial_preview)
    else:
        width, height, data = 1, 1, [0.2, 0.2, 0.2, 1.0]

    if not dpg.does_item_exist(PREVIEW_TEXTURE_TAG):
        dpg.add_dynamic_texture(
            width=width,
            height=height,
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
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Import Video File",
                callback=videoImportDialog.open_video_import_dialog,
            )
            dpg.add_button(
                label="Merge Selected Videos",
                callback=callback_merge_selected_videos,
            )
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
        file_states = SINGLETON.get_selectedVideos()
        for file in SINGLETON.get_all_temp_files():
            with dpg.table_row(parent="videoFiles"):
                dpg.add_text(f"{str(file).split("/")[-1]}")
                dpg.add_checkbox(
                    callback=callback_select_video_files,
                    default_value=file_states.get(file, {"state": False})["state"],
                    user_data=file,
                )
                dpg.add_button(
                    label="Up",
                    user_data=["up", file],
                    callback=callback_moveCoord,
                )
                dpg.add_button(
                    label="Down",
                    user_data=["down", file],
                    callback=callback_moveCoord,
                )
                dpg.add_button(
                    label="Left",
                    user_data=["left", file],
                    callback=callback_moveCoord,
                )
                dpg.add_button(
                    label="Right",
                    user_data=["right", file],
                    callback=callback_moveCoord,
                )
                dpg.add_button(
                    label="Delete",
                    user_data=file,
                    callback=callback_delete_video_file,
                )

        dpg.add_spacer(height=10)
        dpg.add_image(PREVIEW_TEXTURE_TAG, tag=PREVIEW_IMAGE_WIDGET_TAG)

        with dpg.item_handler_registry() as handler:
            dpg.add_item_resize_handler(
                callback=lambda s, a, u: _resize_preview_to_window()
            )
        dpg.bind_item_handler_registry("camera_merge_window", handler)
        _resize_preview_to_window()
        _set_preview_texture(PREVIEW_IMAGE_PATH)
