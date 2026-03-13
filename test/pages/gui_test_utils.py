import os
import tempfile
import unittest

import dearpygui.dearpygui as dpg

from src.database.database_setup import close_db, initialize_db
from src.logic import singleton
from src.pages import cameraMergeWindow, cameraZoneWindow, menuBar


def texture_data(width: int, height: int) -> list[float]:
    return [0.0, 0.0, 0.0, 1.0] * (width * height)


class GuiDbTestCase(unittest.TestCase):
    def setUp(self):
        self._db_dir = tempfile.TemporaryDirectory()
        self._data_dir = tempfile.TemporaryDirectory()
        self.videos_dir = os.path.join(self._data_dir.name, "videos")
        self.pictures_dir = os.path.join(self._data_dir.name, "pictures")
        self.database_videos_dir = os.path.join(self._data_dir.name, "databaseVideos")

        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.pictures_dir, exist_ok=True)
        os.makedirs(self.database_videos_dir, exist_ok=True)

        close_db()
        initialize_db(os.path.join(self._db_dir.name, "test_store.db"))

        dpg.create_context()
        dpg.configure_app(manual_callback_management=True)

        self._reset_singleton_paths()
        self._reset_page_state()

    def tearDown(self):
        self._reset_page_state()
        try:
            dpg.destroy_context()
        finally:
            close_db()
            self._data_dir.cleanup()
            self._db_dir.cleanup()

    def _reset_singleton_paths(self):
        test_singleton = singleton.Singleton()
        test_singleton._tempFolder = self.videos_dir
        test_singleton._tempFolderPictures = self.pictures_dir
        test_singleton._databaseVideoFolder = self.database_videos_dir
        test_singleton._selectedVideos = {}

        cameraMergeWindow.SINGLETON = test_singleton
        cameraZoneWindow.SINGLETON = test_singleton
        menuBar.SINGLETON = test_singleton
        cameraMergeWindow.DATABASE_VIDEOS_DIR = self.database_videos_dir
        cameraZoneWindow.DATABASE_VIDEOS_DIR = self.database_videos_dir
        cameraMergeWindow.MERGED_PREVIEW_PATH = os.path.join(
            self.pictures_dir, "merged_preview.png"
        )

    def _reset_page_state(self):
        cameraMergeWindow.STORE_LABEL_TO_ID.clear()
        cameraMergeWindow.PREVIEW_TEX_WIDTH = 4
        cameraMergeWindow.PREVIEW_TEX_HEIGHT = 4
        cameraMergeWindow.PREVIEW_TEX_DATA = texture_data(4, 4)
        cameraMergeWindow._PREVIEW_PENDING_DATA = None
        cameraMergeWindow._PREVIEW_UPDATE_SCHEDULED = False
        cameraMergeWindow.SINGLETON._selectedVideos = {}

        cameraZoneWindow.ZONES.clear()
        cameraZoneWindow.SELECTED_ZONE_INDEX = 0
        cameraZoneWindow.SELECTED_VIDEO_PATH = None
        cameraZoneWindow.STORE_LABEL_TO_ID.clear()
        cameraZoneWindow.VIDEO_LABEL_TO_PATH.clear()
        cameraZoneWindow.PREVIEW_TEX_WIDTH = 4
        cameraZoneWindow.PREVIEW_TEX_HEIGHT = 4
        cameraZoneWindow.PREVIEW_TEX_DATA = texture_data(4, 4)
        cameraZoneWindow._PREVIEW_PENDING_DATA = None
        cameraZoneWindow._PREVIEW_UPDATE_SCHEDULED = False

    def create_dummy_file(self, path: str, contents: bytes = b"test") -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(contents)
        return path
