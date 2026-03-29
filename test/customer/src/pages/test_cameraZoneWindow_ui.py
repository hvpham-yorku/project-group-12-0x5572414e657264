import unittest
from unittest.mock import patch

import dearpygui.dearpygui as dpg

from src.database import model_managers as mm
from src.database.models import Aisle, Camera, Store
from src.pages import cameraZoneWindow
from test.customer.src.pages.gui_test_utils import GuiDbTestCase


class TestCameraZoneWindowUI(GuiDbTestCase):
    def test_create_window_populates_store_and_video_dropdowns(self):
        store_a = mm.add_store(Store(name="Store A", owner="Owner A"))
        store_b = mm.add_store(Store(name="Store B", owner="Owner B"))
        mm.add_camera(Camera(store_id=store_a.store_id, relative_file_path="videos/a.mp4"))
        mm.add_camera(Camera(store_id=store_b.store_id, relative_file_path="videos/b.mp4"))

        with patch.object(cameraZoneWindow, "_update_preview"):
            cameraZoneWindow.create_camera_zone_window()

        self.assertTrue(dpg.does_item_exist(cameraZoneWindow.WINDOW_TAG))
        store_items = dpg.get_item_configuration(cameraZoneWindow.STORE_DROPDOWN_TAG)["items"]
        video_items = dpg.get_item_configuration(cameraZoneWindow.VIDEO_DROPDOWN_TAG)["items"]
        self.assertIn(f"{store_a.store_id} - {store_a.name}", store_items)
        self.assertIn(f"{store_b.store_id} - {store_b.name}", store_items)
        self.assertIn("1 - a.mp4", video_items)

    def test_switching_store_loads_only_that_stores_zones(self):
        store_a = mm.add_store(Store(name="Store A", owner="Owner A"))
        store_b = mm.add_store(Store(name="Store B", owner="Owner B"))
        mm.add_camera(Camera(store_id=store_a.store_id, relative_file_path="videos/a.mp4"))
        mm.add_camera(Camera(store_id=store_b.store_id, relative_file_path="videos/b.mp4"))
        mm.add_aisle(
            Aisle(
                store_id=store_a.store_id,
                bottom_left_x=1,
                bottom_left_y=2,
                top_right_x=11,
                top_right_y=12,
            )
        )
        mm.add_aisle(
            Aisle(
                store_id=store_b.store_id,
                bottom_left_x=5,
                bottom_left_y=6,
                top_right_x=15,
                top_right_y=16,
            )
        )

        with patch.object(cameraZoneWindow, "_update_preview"), \
             patch("src.pages.cameraZoneWindow.logWindow.addLog"):
            cameraZoneWindow.create_camera_zone_window()
            dpg.set_value(
                cameraZoneWindow.STORE_DROPDOWN_TAG,
                f"{store_b.store_id} - {store_b.name}",
            )
            cameraZoneWindow.callback_load_zones(None, None, None)

        self.assertEqual(
            cameraZoneWindow.ZONES,
            [{"x": 5, "y": 6, "w": 10, "h": 10}],
        )

    def test_done_replaces_store_zones_in_database(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        mm.add_camera(Camera(store_id=store.store_id, relative_file_path="videos/a.mp4"))
        old_aisle = mm.add_aisle(
            Aisle(
                store_id=store.store_id,
                bottom_left_x=0,
                bottom_left_y=0,
                top_right_x=5,
                top_right_y=5,
            )
        )

        with patch.object(cameraZoneWindow, "_update_preview"):
            cameraZoneWindow.create_camera_zone_window()

        dpg.set_value(
            cameraZoneWindow.STORE_DROPDOWN_TAG,
            f"{store.store_id} - {store.name}",
        )
        cameraZoneWindow.ZONES[:] = [
            {"x": 10, "y": 20, "w": 30, "h": 40},
            {"x": 1, "y": 2, "w": 3, "h": 4},
        ]

        with patch("src.pages.cameraZoneWindow.logWindow.addLog"):
            cameraZoneWindow.callback_done(None, None, None)

        aisles = mm.get_aisles_by_store(store.store_id)
        self.assertEqual(len(aisles), 2)
        self.assertEqual(
            [(a.bottom_left_x, a.bottom_left_y, a.top_right_x, a.top_right_y) for a in aisles],
            [(10, 20, 40, 60), (1, 2, 4, 6)],
        )
        self.assertNotIn(
            (
                old_aisle.bottom_left_x,
                old_aisle.bottom_left_y,
                old_aisle.top_right_x,
                old_aisle.top_right_y,
            ),
            [(a.bottom_left_x, a.bottom_left_y, a.top_right_x, a.top_right_y) for a in aisles],
        )


if __name__ == "__main__":
    unittest.main()
