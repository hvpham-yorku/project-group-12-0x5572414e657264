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


if __name__ == "__main__":
    unittest.main()
