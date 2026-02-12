import dearpygui.dearpygui as dpg


def mainWindow(tag: str):
    with dpg.window(label="Camera Feed", tag="camera_window", width=700, height=540):
        dpg.add_image("camera_texture", tag="camera_image")
