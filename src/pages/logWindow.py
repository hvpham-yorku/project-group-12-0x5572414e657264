import dearpygui.dearpygui as dpg
from datetime import datetime
import os
import platform
import shutil
import subprocess

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

    if severityLevel == 1:
        _play_warning_sound()


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
    except Exception:
        pass
