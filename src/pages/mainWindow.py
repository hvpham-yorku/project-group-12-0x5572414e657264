import dearpygui.dearpygui as dpg
from src.themes.themes import *


def mainWindow(tag: str):
    """
    Docstring for mainWindow
    Initializes the main background window

    :param tag: The global tag name for this page
    :type tag: str
    """
    with dpg.window(tag=tag):
        dpg.add_text("Main Content")
        with dpg.child_window(
            width=-1,  # -1 = fill parent width
            height=-1,  # -1 = fill parent height
            border=True,
        ):
            dpg.add_text("This fills the parent")
        with dpg.group(horizontal=True):

            # Left panel
            with dpg.child_window(width=200, height=-1, border=True):
                dpg.add_text("Left Panel")

            # Right panel (fills remaining space)
            with dpg.child_window(width=-1, height=-1, border=True):
                dpg.add_text("Right Panel")
