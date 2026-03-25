import dearpygui.dearpygui as dpg
from src.themes import themes
from src.pages import mainWindow
from src.pages import menuBar
from src.pages import dataAnalyticsWindow
from src.logic import singleton

from src.pages import popupWindow


# Singleton setup
SINGLETON = singleton.Singleton()


def main():
    dpg.create_context()
    dpg.configure_app(manual_callback_management=True)

    dpg.bind_theme(themes.create_theme_default())

    # Set up the viewport
    dpg.create_viewport(title="StoreFlow Analytics", width=1300, height=800)

    # Initializes camera feed window
    # cameraFeed.create_camera_feed_window()

    # Initializes the pages
    mainWindow.mainWindow("main_window")
    menuBar.menuBar()
    popupWindow.instantiate_popup()

    # sets which window is the primary window
    dpg.set_primary_window("main_window", True)

    # Show the viewport
    dpg.setup_dearpygui()
    dpg.show_viewport()

    try:
        while dpg.is_dearpygui_running():
            dataAnalyticsWindow.pump_simulation_view()
            dpg.render_dearpygui_frame()
            dpg.run_callbacks(dpg.get_callback_queue())
    finally:
        dpg.destroy_context()


if __name__ == "__main__":
    main()
