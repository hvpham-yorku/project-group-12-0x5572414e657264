import dearpygui.dearpygui as dpg
import shutil
from src.themes.themes import *
from src.pages import logWindow
from src.pages import cameraMergeWindow
from src.logic import singleton
from src.actions import videoImportDialog
from src.pages import cameraZoneWindow
from src.pages import addStorePopup
from src.pages import wipeDatabasePopup
from src.database.model_managers import get_all_cameras
import os
import tkinter as tk
from tkinter import filedialog
import platform
import subprocess
import webbrowser
from src.logic.dataGenerator import generate_and_persist

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


def openAddStorePopup(sender, app_data, user_data):
    addStorePopup.open_add_store_popup()


def openWipeDatabasePopup(sender, app_data, user_data):
    wipeDatabasePopup.open_wipe_database_popup()


def callback_populateDataBaseWithDemoData(sender, app_data, user_data):
    generate_and_persist(include_sales_data=True)


def callback_populateDataBaseWithDemoDataNoSales(sender, app_data, user_data):
    generate_and_persist(include_sales_data=False)


def delete_orphaned_database_videos(sender, app_data, user_data):
    folder = SINGLETON.get_databaseVideoFolder()
    if not os.path.isdir(folder):
        logWindow.addLog(1, f"Database video folder not found: {folder}")
        return

    db_paths = set()
    for cam in get_all_cameras():
        if not cam.relative_file_path:
            continue
        path = cam.relative_file_path
        abs_path = path if os.path.isabs(path) else os.path.abspath(path)
        db_paths.add(os.path.normpath(abs_path))

    deleted = []
    for name in os.listdir(folder):
        file_path = os.path.join(folder, name)
        if not os.path.isfile(file_path):
            continue
        abs_path = os.path.normpath(os.path.abspath(file_path))
        if abs_path not in db_paths:
            try:
                os.remove(file_path)
                deleted.append(name)
            except Exception as exc:
                logWindow.addLog(2, f"Failed to delete {file_path}: {exc}")

    logWindow.addLog(0, f"Deleted {len(deleted)} orphaned video(s).")


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
            # dpg.add_menu_item(
            #     label="Nothing Here Yet", callback=feature_not_implemented
            # )
            # dpg.add_menu_item(
            #     label="Import Video Files",
            #     callback=videoImportDialog.open_video_import_dialog,
            # )
            # dpg.add_menu_item(label="Save", callback=feature_not_implemented)
            # dpg.add_menu_item(label="Save As", callback=feature_not_implemented)

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="DATABASE WIPE", callback=openWipeDatabasePopup)
                dpg.add_menu_item(
                    label="Add demo data to database",
                    callback=callback_populateDataBaseWithDemoData,
                )
                dpg.add_menu_item(
                    label="Add demo data to database no sales",
                    callback=callback_populateDataBaseWithDemoDataNoSales,
                )
                # dpg.add_menu_item(label="Setting 1", callback=feature_not_implemented, check=True)
                # dpg.add_menu_item(label="Setting 2", callback=feature_not_implemented)
        with dpg.menu(label="Data"):
            dpg.add_menu_item(
                label="Create merged camera video file", callback=openCameraMergeWindow
            )
            dpg.add_menu_item(label="Create aisles for store", callback=openZoneWindow)
            dpg.add_menu_item(label="Add store", callback=openAddStorePopup)

        with dpg.menu(label="View"):
            with dpg.menu(label="Themes"):
                dpg.add_menu_item(label="Dark", callback=set_dark)
                dpg.add_menu_item(label="Light", callback=set_light)
                dpg.add_menu_item(label="Default", callback=set_default_theme)
                dpg.add_menu_item(label="Retro", callback=set_retro)
        with dpg.menu(label="Help"):
            dpg.add_menu_item(label="Wiki/Readme", callback=open_github_page)
            dpg.add_menu_item(
                label="Delete Orphaned DB Videos",
                callback=delete_orphaned_database_videos,
            )
