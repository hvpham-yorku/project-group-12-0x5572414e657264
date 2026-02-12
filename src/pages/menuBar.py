import dearpygui.dearpygui as dpg
from datetime import datetime
from ..themes.themes import *


def print_me(sender):
    print(f"Menu Item: {sender}")


def set_dark(sender):
    dpg.bind_theme(create_theme_dark())


def set_light(sender):
    dpg.bind_theme(create_theme_light())


def set_default_theme(sender):
    dpg.bind_theme(create_theme_default())


def set_retro(sender):
    dpg.bind_theme(create_theme_retro())


def menuBar():
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Nothing Here Yet", callback=print_me)
            # dpg.add_menu_item(label="Save", callback=print_me)
            # dpg.add_menu_item(label="Save As", callback=print_me)

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Nothing Here Yet", callback=print_me)
                # dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
                # dpg.add_menu_item(label="Setting 2", callback=print_me)

        with dpg.menu(label="View"):
            with dpg.menu(label="Themes"):
                dpg.add_menu_item(label="dark", callback=set_dark)
                dpg.add_menu_item(label="light", callback=set_light)
                dpg.add_menu_item(label="green accent", callback=set_default_theme)
                dpg.add_menu_item(label="retro?", callback=set_retro)

        dpg.add_menu_item(label="Help", callback=print_me)

        # with dpg.menu(label="Widget Items"):
        #     dpg.add_checkbox(label="Pick Me", callback=print_me)
        #     dpg.add_button(label="Press Me", callback=print_me)
        #     dpg.add_color_picker(label="Color Me", callback=print_me)
