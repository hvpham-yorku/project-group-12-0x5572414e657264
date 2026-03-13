import os
import unittest
from datetime import datetime
from unittest.mock import patch

import dearpygui.dearpygui as dpg

from src.database import model_managers as mm
from src.database.models import Camera, Store
from src.pages import addStorePopup, cameraMergeWindow, cameraZoneWindow, menuBar
from test.pages.gui_test_utils import GuiDbTestCase


class TestGuiWorkflows(GuiDbTestCase):
    def test_add_store_popup_refreshes_existing_dropdowns(self):
        with patch.object(
            cameraMergeWindow,
            "_load_image_rgba",
            return_value=cameraMergeWindow.PREVIEW_TEX_DATA.copy(),
        ), patch.object(cameraMergeWindow, "_set_preview_texture"), \
             patch.object(cameraZoneWindow, "_update_preview"), \
             patch("src.pages.addStorePopup.logWindow.addLog"), \
             patch("src.pages.cameraZoneWindow.logWindow.addLog"):
            cameraMergeWindow.create_camera_merge_window()
            cameraZoneWindow.create_camera_zone_window()

            addStorePopup.open_add_store_popup()
            dpg.set_value(addStorePopup.NAME_INPUT_TAG, "Integrated Store")
            dpg.set_value(addStorePopup.OWNER_INPUT_TAG, "Integrated Owner")
            addStorePopup._create_store(None, None, None)

        stores = mm.get_all_stores()
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].name, "Integrated Store")
        self.assertEqual(stores[0].owner, "Integrated Owner")
        label = f"{stores[0].store_id} - {stores[0].name}"
        merge_items = dpg.get_item_configuration(cameraMergeWindow.STORE_DROPDOWN_TAG)["items"]
        zone_items = dpg.get_item_configuration(cameraZoneWindow.STORE_DROPDOWN_TAG)["items"]
        self.assertIn(label, merge_items)
        self.assertIn(label, zone_items)

    def test_merge_workflow_feeds_zone_video_dropdown(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        store_label = f"{store.store_id} - {store.name}"
        video_path = self.create_dummy_file(os.path.join(self.videos_dir, "clip.mp4"))
        cameraMergeWindow.SINGLETON._selectedVideos = {
            video_path: {"state": True, "coor": [0, 0]}
        }

        with patch.object(
            cameraMergeWindow,
            "_load_image_rgba",
            return_value=cameraMergeWindow.PREVIEW_TEX_DATA.copy(),
        ), patch.object(cameraMergeWindow, "_set_preview_texture"), \
             patch.object(cameraZoneWindow, "_update_preview"), \
             patch("src.pages.cameraMergeWindow.logWindow.addLog"), \
             patch("src.pages.cameraZoneWindow.logWindow.addLog"):
            cameraMergeWindow.create_camera_merge_window()
            dpg.set_value(cameraMergeWindow.STORE_DROPDOWN_TAG, store_label)

            def fake_merge(video_paths, coordinates, output_path):
                self.create_dummy_file(output_path, b"merged")

            class FixedDateTime:
                @classmethod
                def now(cls):
                    return datetime(2026, 1, 2, 3, 4, 5)

            with patch(
                "src.pages.cameraMergeWindow.mediaEditor.merge_and_blend_videos",
                side_effect=fake_merge,
            ), patch("src.pages.cameraMergeWindow.datetime", FixedDateTime):
                cameraMergeWindow.callback_merge_selected_videos(None, None, None)

            cameraZoneWindow.create_camera_zone_window()
            dpg.set_value(cameraZoneWindow.STORE_DROPDOWN_TAG, store_label)
            cameraZoneWindow.callback_load_zones(None, None, None)

        cameras = mm.get_cameras_by_store(store.store_id)
        self.assertEqual(len(cameras), 1)
        expected_output = os.path.join(
            self.database_videos_dir,
            "merged_20260102_030405.mp4",
        )
        expected_relative_path = os.path.relpath(expected_output, os.getcwd())
        self.assertEqual(cameras[0].store_id, store.store_id)
        self.assertEqual(cameras[0].relative_file_path, expected_relative_path)
        self.assertTrue(os.path.exists(expected_output))
        expected_label = (
            f"{cameras[0].camera_id} - {os.path.basename(cameras[0].relative_file_path)}"
        )
        zone_video_items = dpg.get_item_configuration(cameraZoneWindow.VIDEO_DROPDOWN_TAG)["items"]
        self.assertIn(expected_label, zone_video_items)

    def test_zone_done_inserts_exact_aisle_rows(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        store_label = f"{store.store_id} - {store.name}"
        mm.add_camera(Camera(store_id=store.store_id, relative_file_path="videos/a.mp4"))

        with patch.object(cameraZoneWindow, "_update_preview"), \
             patch("src.pages.cameraZoneWindow.logWindow.addLog"):
            cameraZoneWindow.create_camera_zone_window()
            dpg.set_value(cameraZoneWindow.STORE_DROPDOWN_TAG, store_label)
            cameraZoneWindow.callback_load_zones(None, None, None)

            cameraZoneWindow.ZONES[:] = [
                {"x": 10, "y": 20, "w": 30, "h": 40},
                {"x": 3, "y": 4, "w": 5, "h": 6},
            ]
            cameraZoneWindow.callback_done(None, None, None)

        aisles = mm.get_aisles_by_store(store.store_id)
        self.assertEqual(len(aisles), 2)
        self.assertEqual(
            [
                (
                    aisle.store_id,
                    aisle.bottom_left_x,
                    aisle.bottom_left_y,
                    aisle.top_right_x,
                    aisle.top_right_y,
                    aisle.vertical,
                )
                for aisle in aisles
            ],
            [
                (store.store_id, 10, 20, 40, 60, False),
                (store.store_id, 3, 4, 8, 10, False),
            ],
        )

    def test_delete_orphaned_videos_uses_database_records(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        keep_path = self.create_dummy_file(
            os.path.join(self.database_videos_dir, "keep.mp4"),
            b"keep",
        )
        orphan_path = self.create_dummy_file(
            os.path.join(self.database_videos_dir, "orphan.mp4"),
            b"orphan",
        )
        mm.add_camera(Camera(store_id=store.store_id, relative_file_path=keep_path))

        with patch("src.pages.menuBar.logWindow.addLog"):
            menuBar.delete_orphaned_database_videos(None, None, None)

        self.assertTrue(os.path.exists(keep_path))
        self.assertFalse(os.path.exists(orphan_path))


if __name__ == "__main__":
    unittest.main()
