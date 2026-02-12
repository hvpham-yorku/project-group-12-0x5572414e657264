import dearpygui.dearpygui as dpg
from src.themes.themes import *
from src.pages import cameraFeed

TOP_RATIO = 0.75  # top row = 35% of viewport height
GAP = 0  # optional spacing between rows (px)


def on_resize(sender, app_data):
    vh = dpg.get_viewport_client_height()
    top_h = max(50, int(vh * TOP_RATIO))  # min height safety

    dpg.configure_item("top_row", height=top_h)
    # bottom_row uses height=-1 so it fills whatever remains


def mainWindow(tag: str):
    """
    Docstring for mainWindow
    Initializes the main background window

    :param tag: The global tag name for this page
    :type tag: str
    """
    dpg.set_viewport_resize_callback(on_resize)  # does automatic reflow

    with dpg.window(tag=tag):

        # TOP
        with dpg.child_window(tag="top_row", width=-1, height=450, border=True):
            with dpg.table(resizable=True, policy=dpg.mvTable_SizingStretchProp):
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    with dpg.table_cell():  # LEFT PANEL
                        with dpg.child_window(border=True):
                            dpg.add_text("Camera Feed")
                        cameraFeed.create_camera_feed_window()
                    with dpg.table_cell():  # RIGHT PANEL
                        with dpg.child_window(border=True):
                            dpg.add_text("Import Data")
        # BOTTOM
        with dpg.child_window(tag="bottom_row", width=-1, height=-1, border=True):
            dpg.add_text("Logs")
