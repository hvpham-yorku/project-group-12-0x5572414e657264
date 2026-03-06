import dearpygui.dearpygui as dpg
import shutil
from src.themes.themes import *
from src.pages import logWindow
import os
import tkinter as tk
from tkinter import filedialog
import platform
import subprocess
import webbrowser


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


def open_video_import_dialog(sender, app_data, user_data):
    current_os = platform.system()
    source_file_path = None

    # ---------------------------------------------------------
    # macOS PATH (AppleScript)
    # ---------------------------------------------------------
    if current_os == "Darwin":
        # Added 'of type' with standard video extensions and the Mac 'public.movie' tag
        # This will dim/disable all non-video files in the Mac Finder window
        script = 'POSIX path of (choose file of type {"public.movie", "mp4", "mov", "m4v", "avi", "mkv"} with prompt "Select a video to import:")'
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode != 0:
            logWindow.addLog(0, "Video selection cancelled")
            return

        source_file_path = result.stdout.strip()

    # ---------------------------------------------------------
    # WINDOWS / LINUX PATH (Tkinter)
    # ---------------------------------------------------------
    else:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)

        # Updated 'filetypes' to only look for common video extensions
        source_file_path = filedialog.askopenfilename(
            title="Select a video to import",
            filetypes=(
                ("Video files", "*.mp4 *.mov *.avi *.mkv *.wmv *.m4v"),
                ("All files", "*.*"),
            ),
        )

        root.destroy()

        if not source_file_path:
            logWindow.addLog(0, "Video selection cancelled")
            return

    # ---------------------------------------------------------
    # SHARED COPY LOGIC
    # ---------------------------------------------------------
    file_name = os.path.basename(source_file_path)
    destination_dir = os.path.join(os.getcwd(), "assets/databaseAssets")
    destination_file_path = os.path.join(destination_dir, file_name)

    try:
        shutil.copy2(source_file_path, destination_file_path)
        logWindow.addLog(0, f"Success: Copied video '{file_name}'!")
        print(f"[{current_os}] Copied: {source_file_path} -> {destination_file_path}")
    except Exception as e:
        logWindow.addLog(2, f"ERROR!!!!!!!!: {str(e)}")


def menuBar():
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(
                label="Nothing Here Yet", callback=feature_not_implemented
            )
            dpg.add_menu_item(
                label="Import Video Files", callback=open_video_import_dialog
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
            dpg.add_menu_item(label="DATABASE WIPE", callback=feature_not_implemented)
        with dpg.menu(label="View"):
            with dpg.menu(label="Themes"):
                dpg.add_menu_item(label="Dark", callback=set_dark)
                dpg.add_menu_item(label="Light", callback=set_light)
                dpg.add_menu_item(label="Default", callback=set_default_theme)
                dpg.add_menu_item(label="Retro", callback=set_retro)
        with dpg.menu(label="Help"):
            dpg.add_menu_item(label="Wiki/Readme", callback=open_github_page)
