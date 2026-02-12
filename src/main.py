import dearpygui.dearpygui as dpg

from src.themes import themes
from src.pages import mainWindow
from src.pages import menuBar
from src.pages import cameraFeed


def main():
    dpg.create_context()

    dpg.bind_theme(themes.create_theme_default())

    # Set up the viewport
    dpg.create_viewport(title="StoreFlow Analytics", width=1300, height=800)

    # Initializes camera feed window
    # cameraFeed.create_camera_feed_window()

    # Initializes the pages
    menuBar.menuBar()
    mainWindow.mainWindow("main_window")

    # sets which window is the primary window
    dpg.set_primary_window("main_window", True)

    # Show the viewport
    dpg.setup_dearpygui()
    dpg.show_viewport()

    try:
        # Run the application while updating the live camera feed.
        while dpg.is_dearpygui_running():
            cameraFeed.update_camera_feed()
            dpg.render_dearpygui_frame()
    finally:
        cameraFeed.shutdown_camera_feed()
        dpg.destroy_context()


if __name__ == "__main__":
    main()
