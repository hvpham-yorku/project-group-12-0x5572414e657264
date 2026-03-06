import dearpygui.dearpygui as dpg
import shutil
from src.themes.themes import *
from src.pages import logWindow
from src.pages import cameraMergeWindow
from src.logic import singleton
from src.actions import videoImportDialog
from src.pages import cameraZoneWindow
import os
import tkinter as tk
from tkinter import filedialog
import platform
import subprocess
import webbrowser

SINGLETON = singleton.Singleton()


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


def openCameraMergeWindow(sender, app_data, user_data):
    cameraMergeWindow.create_camera_merge_window()


def openZoneWindow(sender, app_data, user_data):
    cameraZoneWindow.create_camera_zone_window()


def open_github_page(sender, app_data, user_data):
    """
    Opens the default web browser to a specific URL.
    The 'user_data' argument allows you to make this function reusable.
    """
    url = "https://github.com/hvpham-yorku/project-group-12-0x5572414e657264/wiki"

    # Optional: Can pass the URL via the button's user_data
    # Here if needed
    target_url = user_data if user_data else url

    print(f"Opening browser to: {target_url}")
    webbrowser.open(target_url)


def menuBar():
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(
                label="Nothing Here Yet", callback=feature_not_implemented
            )
            dpg.add_menu_item(
                label="Import Video Files",
                callback=videoImportDialog.open_video_import_dialog,
            )
            # dpg.add_menu_item(label="Save", callback=feature_not_implemented)
            # dpg.add_menu_item(label="Save As", callback=feature_not_implemented)

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(
                    label="Nothing Here Yet", callback=feature_not_implemented
                )
                # dpg.add_menu_item(label="Setting 1", callback=feature_not_implemented, check=True)
                # dpg.add_menu_item(label="Setting 2", callback=feature_not_implemented)
        with dpg.menu(label="Data"):
            dpg.add_menu_item(
                label="Create merged camera video file", callback=openCameraMergeWindow
            )
            dpg.add_menu_item(label="Create aisles for store", callback=openZoneWindow)
            dpg.add_menu_item(label="DATABASE WIPE", callback=feature_not_implemented)
        with dpg.menu(label="View"):
            with dpg.menu(label="Themes"):
                dpg.add_menu_item(label="Dark", callback=set_dark)
                dpg.add_menu_item(label="Light", callback=set_light)
                dpg.add_menu_item(label="Default", callback=set_default_theme)
                dpg.add_menu_item(label="Retro", callback=set_retro)
        with dpg.menu(label="Help"):
            dpg.add_menu_item(label="Wiki/Readme", callback=open_github_page)
