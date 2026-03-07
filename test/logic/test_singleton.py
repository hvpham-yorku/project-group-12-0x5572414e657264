import os
import tempfile
import unittest

from src.logic.singleton import Singleton


class TestSingleton(unittest.TestCase):

    def setUp(self):
        # Reset the Singleton before each test to ensure isolation
        Singleton._instance = None

    def test_same_instance_identity(self):
        """Verify that two calls return the exact same object in memory."""
        s1 = Singleton()
        s2 = Singleton()

        # 'is' checks for identity (memory address), not just equality
        self.assertIs(s1, s2, "The two variables do not point to the same instance.")

    def test_attribute_persistence(self):
        """Verify that data set on one instance is visible on the 'other'."""
        s1 = Singleton()
        s1.some_data = "Secret Value"

        s2 = Singleton()
        self.assertEqual(s2.some_data, "Secret Value")

    def test_reset_functionality(self):
        """Verify that our manual reset in setUp actually works (Meta-test)."""
        s1 = Singleton()
        s1.version = 1.0

        # Simulate what happens between tests
        Singleton._instance = None

        s2 = Singleton()
        # s2 should NOT have the 'version' attribute now
        self.assertFalse(hasattr(s2, "version"))

    def test_update_selected_video_coordinates(self):
        s = Singleton()
        video_path = "/tmp/fake_video.mp4"
        s._selectedVideos = {video_path: {"state": True, "coor": [0, 0]}}
        step = s._moveAmount

        s.update_selectedVideoCoordinates(video_path, "right")
        self.assertEqual(s._selectedVideos[video_path]["coor"], [step, 0])

        s.update_selectedVideoCoordinates(video_path, "down")
        self.assertEqual(s._selectedVideos[video_path]["coor"], [step, step])

        s.update_selectedVideoCoordinates(video_path, "left")
        self.assertEqual(s._selectedVideos[video_path]["coor"], [0, step])

        s.update_selectedVideoCoordinates(video_path, "up")
        self.assertEqual(s._selectedVideos[video_path]["coor"], [0, 0])

    def test_get_all_temp_files_populates_selected(self):
        s = Singleton()
        with tempfile.TemporaryDirectory() as temp_dir:
            s._tempFolder = temp_dir
            file_path = os.path.join(temp_dir, "clip.mp4")
            with open(file_path, "wb") as f:
                f.write(b"test")

            files = s.get_all_temp_files()
            self.assertIn(file_path, files)
            self.assertIn(file_path, s._selectedVideos)
            self.assertEqual(s._selectedVideos[file_path]["coor"], [0, 0])


if __name__ == "__main__":
    unittest.main()
