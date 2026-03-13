import unittest
from unittest.mock import patch

import dearpygui.dearpygui as dpg

from src.database import model_managers as mm
from src.pages import addStorePopup
from test.pages.gui_test_utils import GuiDbTestCase


class TestAddStorePopupUI(GuiDbTestCase):
    def test_create_store_persists_to_database(self):
        with patch("src.pages.addStorePopup.logWindow.addLog"), \
             patch("src.pages.addStorePopup.cameraZoneWindow.refresh_store_dropdowns"), \
             patch("src.pages.addStorePopup.cameraMergeWindow.refresh_store_dropdown"):
            addStorePopup.open_add_store_popup()
            dpg.set_value(addStorePopup.NAME_INPUT_TAG, "Store A")
            dpg.set_value(addStorePopup.OWNER_INPUT_TAG, "Owner A")

            addStorePopup._create_store(None, None, None)

        stores = mm.get_all_stores()
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].name, "Store A")
        self.assertEqual(stores[0].owner, "Owner A")
        self.assertFalse(dpg.does_item_exist(addStorePopup.WINDOW_TAG))


if __name__ == "__main__":
    unittest.main()
