import os
import unittest
from unittest.mock import patch

import dearpygui.dearpygui as dpg

from src.database import model_managers as mm
from src.database.models import Store
from src.pages import cameraMergeWindow
from test.pages.gui_test_utils import GuiDbTestCase


class TestCameraMergeWindowUI(GuiDbTestCase):
    def test_create_window_populates_store_dropdown(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))

        with patch.object(
            cameraMergeWindow,
            "_load_image_rgba",
            return_value=cameraMergeWindow.PREVIEW_TEX_DATA.copy(),
        ), patch.object(cameraMergeWindow, "_set_preview_texture"):
            cameraMergeWindow.create_camera_merge_window()

        self.assertTrue(dpg.does_item_exist("camera_merge_window"))
        self.assertTrue(dpg.does_item_exist("videoFiles"))
        items = dpg.get_item_configuration(cameraMergeWindow.STORE_DROPDOWN_TAG)["items"]
        self.assertIn(cameraMergeWindow.STORE_PLACEHOLDER, items)
        self.assertIn(f"{store.store_id} - {store.name}", items)

    def test_done_saves_camera_record_for_selected_store(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        store_label = f"{store.store_id} - {store.name}"
        video_path = self.create_dummy_file(os.path.join(self.videos_dir, "clip.mp4"))
        cameraMergeWindow.SINGLETON._selectedVideos = {
            video_path: {"state": True, "coor": [0, 0]}
        }

        with dpg.window(tag="merge_test_window"):
            dpg.add_combo(
                items=cameraMergeWindow._get_store_options(),
                default_value=store_label,
                tag=cameraMergeWindow.STORE_DROPDOWN_TAG,
            )

        def fake_merge(video_paths, coordinates, output_path):
            self.create_dummy_file(output_path, b"merged")

        with patch("src.pages.cameraMergeWindow.logWindow.addLog"), \
             patch(
                 "src.pages.cameraMergeWindow.mediaEditor.merge_and_blend_videos",
                 side_effect=fake_merge,
             ):
            cameraMergeWindow.callback_merge_selected_videos(None, None, None)

        cameras = mm.get_cameras_by_store(store.store_id)
        self.assertEqual(len(cameras), 1)
        self.assertEqual(cameras[0].store_id, store.store_id)
        self.assertTrue(cameras[0].relative_file_path.endswith(".mp4"))

    def test_done_requires_store_selection(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        video_path = self.create_dummy_file(os.path.join(self.videos_dir, "clip.mp4"))
        cameraMergeWindow.SINGLETON._selectedVideos = {
            video_path: {"state": True, "coor": [0, 0]}
        }

        with dpg.window(tag="merge_test_window"):
            dpg.add_combo(
                items=cameraMergeWindow._get_store_options(),
                default_value=cameraMergeWindow.STORE_PLACEHOLDER,
                tag=cameraMergeWindow.STORE_DROPDOWN_TAG,
            )

        with patch("src.pages.cameraMergeWindow.logWindow.addLog") as add_log, \
             patch("src.pages.cameraMergeWindow.mediaEditor.merge_and_blend_videos") as merge:
            cameraMergeWindow.callback_merge_selected_videos(None, None, None)

        merge.assert_not_called()
        self.assertEqual(mm.get_cameras_by_store(store.store_id), [])
        add_log.assert_called_once()


if __name__ == "__main__":
    unittest.main()
