import os
import tempfile
import unittest
from unittest.mock import patch

from src.database.models import Camera
from src.pages import menuBar


class TestMenuBarCleanup(unittest.TestCase):
    def test_delete_orphaned_database_videos(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            keep_path = os.path.join(temp_dir, "keep.mp4")
            orphan_path = os.path.join(temp_dir, "orphan.mp4")

            for path in [keep_path, orphan_path]:
                with open(path, "wb") as f:
                    f.write(b"test")

            cameras = [
                Camera(camera_id=1, store_id=1, relative_file_path=keep_path),
            ]

            with patch.object(menuBar.SINGLETON, "get_databaseVideoFolder", return_value=temp_dir), \
                 patch("src.pages.menuBar.get_all_cameras", return_value=cameras), \
                 patch("src.pages.menuBar.logWindow.addLog") as add_log:

                menuBar.delete_orphaned_database_videos(None, None, None)

                self.assertTrue(os.path.exists(keep_path))
                self.assertFalse(os.path.exists(orphan_path))
                add_log.assert_called()

    def test_demo_import_callback_uses_sales_mode(self):
        with patch("src.pages.menuBar._attempt_demo_import") as attempt_demo_import:
            menuBar.callback_populateDataBaseWithDemoData(None, None, None)

        attempt_demo_import.assert_called_once_with(include_sales_data=True)

    def test_demo_import_no_sales_callback_uses_no_sales_mode(self):
        with patch("src.pages.menuBar._attempt_demo_import") as attempt_demo_import:
            menuBar.callback_populateDataBaseWithDemoDataNoSales(None, None, None)

        attempt_demo_import.assert_called_once_with(include_sales_data=False)

    def test_attempt_demo_import_blocks_when_database_not_wiped(self):
        with patch(
            "src.pages.menuBar._database_requires_wipe_before_demo_import",
            return_value=True,
        ), patch("src.pages.menuBar.display_modal_popup") as popup, patch(
            "src.pages.menuBar.generate_and_persist"
        ) as generate_and_persist, patch(
            "src.pages.menuBar._refresh_data_analysis_window"
        ) as refresh:
            menuBar._attempt_demo_import(include_sales_data=True)

        popup.assert_called_once_with(
            2, menuBar._DEMO_DATABASE_IMPORT_ERROR_MESSAGE
        )
        generate_and_persist.assert_not_called()
        refresh.assert_not_called()

    def test_attempt_demo_import_runs_when_database_is_clean(self):
        with patch(
            "src.pages.menuBar._database_requires_wipe_before_demo_import",
            return_value=False,
        ), patch("src.pages.menuBar.generate_and_persist") as generate_and_persist, patch(
            "src.pages.menuBar._refresh_data_analysis_window"
        ) as refresh:
            menuBar._attempt_demo_import(include_sales_data=False)

        generate_and_persist.assert_called_once_with(include_sales_data=False)
        refresh.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
