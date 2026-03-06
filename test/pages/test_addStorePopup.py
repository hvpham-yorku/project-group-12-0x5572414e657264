import unittest
from unittest.mock import MagicMock, patch

from src.pages import addStorePopup


class TestAddStorePopup(unittest.TestCase):
    def test_create_store_success(self):
        with patch.object(addStorePopup.dpg, "get_value") as get_value, \
             patch("src.pages.addStorePopup.add_store") as add_store, \
             patch("src.pages.addStorePopup.logWindow.addLog") as add_log, \
             patch("src.pages.addStorePopup.cameraZoneWindow.refresh_store_dropdowns") as refresh_zone, \
             patch("src.pages.addStorePopup.cameraMergeWindow.refresh_store_dropdown") as refresh_merge, \
             patch("src.pages.addStorePopup._close_popup") as close_popup:

            get_value.side_effect = ["My Store", "Owner"]
            add_store.return_value = MagicMock(store_id=1, name="My Store")

            addStorePopup._create_store(None, None, None)

            add_store.assert_called_once()
            add_log.assert_called_once()
            refresh_zone.assert_called_once()
            refresh_merge.assert_called_once()
            close_popup.assert_called_once()

    def test_create_store_missing_name(self):
        with patch.object(addStorePopup.dpg, "get_value") as get_value, \
             patch("src.pages.addStorePopup.add_store") as add_store, \
             patch("src.pages.addStorePopup.logWindow.addLog") as add_log:

            get_value.side_effect = ["", "Owner"]

            addStorePopup._create_store(None, None, None)

            add_store.assert_not_called()
            add_log.assert_called_once()


if __name__ == "__main__":
    unittest.main()
