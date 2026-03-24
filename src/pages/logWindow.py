import dearpygui.dearpygui as dpg
from datetime import datetime
import os
import platform
import shutil
import subprocess
import random

from src.database.model_managers import add_log
from src.database.models import Log

# TODO ADD A BUTTON TO CLEAR LOGS


def createWindow(parent: str) -> None:
    with dpg.child_window(
        # label="Sales Data From POS",
        parent=parent,
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        with dpg.table(
            tag="logs",
            show=True,
            header_row=True,
            resizable=True,
            borders_innerV=True,
            borders_outerV=True,
        ):
            dpg.add_table_column(label="Date", init_width_or_weight=0.33)
            dpg.add_table_column(label="Severity", init_width_or_weight=0.33)
            dpg.add_table_column(label="Message", init_width_or_weight=0.33)


def addLog(severityLevel: int, message: str) -> None:
    """
    Docstring for addLog

    :param severityLevel: the bigger the number, the more severe
    :type severityLevel: int
    :param message: string messsage to display
    :type message: str
    """
    now = datetime.now()
    with dpg.table_row(parent="logs"):
        dpg.add_text(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        dpg.add_text(severityLevel)
        dpg.add_text(message)

    add_log(
        Log(
            store_id=1,
            action=message,
            category=str(severityLevel),
            created_at=now,
        )
    )

    match severityLevel:
        case 1:
            _play_warning_sound()
        case _:
            _play_customSound(severityLevel)


def _play_warning_sound() -> None:
    try:
        system = platform.system()
        if system == "Windows":
            import winsound

            winsound.MessageBeep(winsound.MB_ICONWARNING)
            return

        if system == "Darwin":
            sound_path = "/System/Library/Sounds/Glass.aiff"
            if os.path.exists(sound_path):
                subprocess.Popen(["afplay", sound_path])
            return

        # Linux / other UNIX
        if shutil.which("paplay"):
            sound_path = "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga"
            if os.path.exists(sound_path):
                subprocess.Popen(["paplay", sound_path])
                return
        if shutil.which("aplay"):
            sound_path = "/usr/share/sounds/alsa/Front_Center.wav"
            if os.path.exists(sound_path):
                subprocess.Popen(["aplay", sound_path])
                return
    except Exception as e:
        pass


def _play_customSound(severity: int = 0):
    try:
        # get sounds
        path = "src/assets/audio/warningSounds"
        fullPath = os.path.join(os.getcwd(), path)
        file_names = []
        if os.path.exists(fullPath):
            file_names = [
                entry.name for entry in os.scandir(fullPath) if entry.is_file()
            ]
            # print("Files found:", file_names)
        else:
            print("That folder doesn't exist yet!")

        soundPath = os.path.join(
            fullPath, file_names[random.randint(0, len(file_names) - 1)]
        )
        if os.path.exists(soundPath):
            subprocess.Popen(["afplay", soundPath])
    except Exception as e:
        print(e)
        _play_warning_sound()


# _play_customSound(1)
