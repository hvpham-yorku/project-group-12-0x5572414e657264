import os
import unittest
from unittest.mock import patch

from src.database.models import Camera
from src.pages import cameraZoneWindow


class TestCameraZoneWindowVideos(unittest.TestCase):
    def test_list_database_videos_builds_labels(self):
        cams = [
            Camera(camera_id=1, store_id=2, relative_file_path="assets/databaseVideos/v1.mp4"),
            Camera(camera_id=2, store_id=2, relative_file_path="assets/databaseVideos/v2.mp4"),
        ]

        with patch("src.pages.cameraZoneWindow.get_cameras_by_store", return_value=cams):
            labels = cameraZoneWindow._list_database_videos(2)

        self.assertEqual(len(labels), 2)
        self.assertIn("1 - v1.mp4", labels)
        self.assertIn("2 - v2.mp4", labels)

    def test_set_selected_video_uses_mapping(self):
        cameraZoneWindow.VIDEO_LABEL_TO_PATH.clear()
        cameraZoneWindow.VIDEO_LABEL_TO_PATH["1 - v1.mp4"] = "assets/databaseVideos/v1.mp4"
        cameraZoneWindow._set_selected_video_by_name("1 - v1.mp4")
        self.assertEqual(
            cameraZoneWindow.SELECTED_VIDEO_PATH,
            "assets/databaseVideos/v1.mp4",
        )


if __name__ == "__main__":
    unittest.main()
