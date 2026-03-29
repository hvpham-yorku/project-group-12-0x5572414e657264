import dearpygui.dearpygui as dpg
from datetime import datetime
import os
import platform
import shutil
import subprocess
import random

from src.database.model_managers import add_log
from src.database.models import Log
from src.utils.paths import get_resource_path

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
            _play_customSound()


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


def _play_audio_file(sound_path: str) -> bool:
    try:
        system = platform.system()
        suffix = os.path.splitext(sound_path)[1].lower()

        if system == "Windows" and suffix == ".wav":
            import winsound

            winsound.PlaySound(
                sound_path,
                winsound.SND_ASYNC | winsound.SND_FILENAME,
            )
            return True

        if system == "Darwin" and shutil.which("afplay"):
            subprocess.Popen(["afplay", sound_path])
            return True

        if shutil.which("ffplay"):
            subprocess.Popen(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "quiet",
                    sound_path,
                ]
            )
            return True

        if shutil.which("paplay"):
            subprocess.Popen(["paplay", sound_path])
            return True

        if shutil.which("aplay") and suffix == ".wav":
            subprocess.Popen(["aplay", sound_path])
            return True
    except Exception:
        return False

    return False


def _play_customSound(severity: int = 0):
    soundPath = ""
    try:
        fullPath = get_resource_path("src", "assets", "audio", "warningSounds")
        file_names = []
        if os.path.exists(fullPath):
            allowed_exts = (".wav",) if platform.system() == "Windows" else (
                ".mp3",
                ".wav",
                ".aiff",
                ".ogg",
            )
            file_names = [
                entry.name
                for entry in os.scandir(fullPath)
                if entry.is_file() and entry.name.lower().endswith(allowed_exts)
            ]

        if not file_names:
            _play_warning_sound()
            return

        soundPath = os.path.join(
            fullPath, file_names[random.randint(0, len(file_names) - 1)]
        )
        if os.path.exists(soundPath) and _play_audio_file(soundPath):
            return

        _play_warning_sound()
    except Exception as e:
        _play_warning_sound()


# _play_customSound(1)
