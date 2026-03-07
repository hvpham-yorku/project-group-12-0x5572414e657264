import dearpygui.dearpygui as dpg

from src.themes.themes import *
from src.pages import cameraFeed
from src.pages import logWindow

CAMERA_SELECT_MENU_TAG = "camera_select_menu"


def feature_not_implemented(sender):
    print(f"Menu Item: {sender}")
    logWindow.addLog(0, "THIS FEATURE IS NOT YET IMPLEMENTED")


def set_dark(sender):
    dpg.bind_theme(create_theme_dark())


def set_light(sender):
    dpg.bind_theme(create_theme_light())


def set_default_theme(sender):
    dpg.bind_theme(create_theme_default())


def set_retro(sender):
    dpg.bind_theme(create_theme_retro())


def select_camera(sender, app_data, user_data):
    camera_index = int(user_data)
    cameraFeed.select_camera(camera_index)
    logWindow.addLog(0, f"CAMERA {user_data} WAS SELECTED")
    refresh_camera_list()


def refresh_camera_list(sender=None, app_data=None, user_data=None):
    logWindow.addLog(0, "REFRESHING CAMERA LIST")
    if not dpg.does_item_exist(CAMERA_SELECT_MENU_TAG):
        return

    dpg.delete_item(CAMERA_SELECT_MENU_TAG, children_only=True)

    available_cameras = cameraFeed.list_available_cameras()
    selected_index = cameraFeed.get_selected_camera_index()

    if not available_cameras:
        dpg.add_menu_item(
            parent=CAMERA_SELECT_MENU_TAG,
            label="No cameras detected",
            enabled=False,
        )
        return

    for camera in available_cameras:
        active_suffix = " (active)" if camera.index == selected_index else ""
        dpg.add_menu_item(
            parent=CAMERA_SELECT_MENU_TAG,
            label=f"{camera.label}{active_suffix}",
            callback=select_camera,
            user_data=camera.index,
        )


def menuBar():
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(
                label="Nothing Here Yet", callback=feature_not_implemented
            )
            # dpg.add_menu_item(label="Save", callback=feature_not_implemented)
            # dpg.add_menu_item(label="Save As", callback=feature_not_implemented)

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(
                    label="Nothing Here Yet", callback=feature_not_implemented
                )
                # dpg.add_menu_item(label="Setting 1", callback=feature_not_implemented, check=True)
                # dpg.add_menu_item(label="Setting 2", callback=feature_not_implemented)

        with dpg.menu(label="View"):
            with dpg.menu(label="Themes"):
                dpg.add_menu_item(label="Dark", callback=set_dark)
                dpg.add_menu_item(label="Light", callback=set_light)
                dpg.add_menu_item(label="Default", callback=set_default_theme)
                dpg.add_menu_item(label="Retro", callback=set_retro)

        # with dpg.menu(label="Camera"):
        #     dpg.add_menu_item(
        #         label="Show Live Feed",
        #         check=True,
        #         default_value=True,
        #         callback=cameraFeed.toggle_camera_feed_window,
        #     )
        #     dpg.add_menu_item(label="Refresh Cameras", callback=refresh_camera_list)
        #     with dpg.menu(label="Select Camera", tag=CAMERA_SELECT_MENU_TAG):
        #         dpg.add_menu_item(label="Scanning...", enabled=False)

        dpg.add_menu_item(label="Help", callback=feature_not_implemented)

    refresh_camera_list()
