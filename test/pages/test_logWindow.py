import unittest
from contextlib import contextmanager
from unittest.mock import patch

from src.pages import logWindow


@contextmanager
def fake_table_row(*args, **kwargs):
    yield


class TestLogWindow(unittest.TestCase):
    def test_warning_sound_on_severity_one(self):
        with patch.object(logWindow.dpg, "table_row", fake_table_row), \
             patch.object(logWindow.dpg, "add_text"), \
             patch("src.pages.logWindow.add_log"), \
             patch("src.pages.logWindow._play_warning_sound") as sound:
            logWindow.addLog(1, "Warning message")
            sound.assert_called_once()

    def test_no_sound_on_other_severity(self):
        with patch.object(logWindow.dpg, "table_row", fake_table_row), \
             patch.object(logWindow.dpg, "add_text"), \
             patch("src.pages.logWindow.add_log"), \
             patch("src.pages.logWindow._play_warning_sound") as sound:
            logWindow.addLog(0, "Info")
            sound.assert_not_called()


if __name__ == "__main__":
    unittest.main()
