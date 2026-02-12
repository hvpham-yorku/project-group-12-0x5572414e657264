import dearpygui.dearpygui as dpg

from src.themes import themes
from src.pages import menuBar


def main():
    dpg.create_context()

    dpg.bind_theme(themes.create_theme_default())

    # Set up the viewport
    dpg.create_viewport(title="Temp", width=1300, height=800)

    menuBar.menuBar()

    # Show the viewport
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Run the application
    dpg.start_dearpygui()

    # Clean up
    dpg.destroy_context()


if __name__ == "__main__":
    main()
