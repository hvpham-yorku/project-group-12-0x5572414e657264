import dearpygui.dearpygui as dpg
from src.actions import videoImportDialog
from src.logic import singleton
from src.pages import logWindow

SINGLETON = singleton.Singleton()


def feature_not_implemented(sender):
    print(f"Menu Item: {sender}")
    logWindow.addLog(0, "THIS FEATURE IS NOT YET IMPLEMENTED")


def callback_select_video_files(sender, app_data, user_data):
    SINGLETON.set_selectedVideo(user_data, app_data)


def callback_delete_video_file(sender, app_data, user_data):
    SINGLETON.delete_video(user_data)
    callback_refresh_table_entries(sender, app_data, user_data)


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


def callback_video_import_dialog(sender, app_data, user_data):
    videoImportDialog.open_video_import_dialog(sender, app_data, user_data)
    callback_refresh_table_entries(sender, app_data, user_data)


def callback_moveCoord(sender, app_data, user_data):
    direction = user_data[0]
    file = user_data[1]
    SINGLETON.update_selectedVideoCoordinates(file, direction)


def create_camera_merge_window():
    if dpg.does_item_exist("camera_merge_window"):
        dpg.show_item("camera_merge_window")
        callback_refresh_table_entries(None, None, None)
        return

    with dpg.window(
        tag="camera_merge_window",
        label="Camera Feeds Setup",
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        dpg.add_text("Camera Video Feed Setup")
        dpg.add_button(
            label="Import Video File",
            callback=videoImportDialog.open_video_import_dialog,
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
