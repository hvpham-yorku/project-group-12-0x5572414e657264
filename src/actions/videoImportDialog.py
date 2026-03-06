from src.pages import logWindow
from src.logic import singleton
import platform
import subprocess
import shutil
import os

SINGLETON = singleton.Singleton()


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
