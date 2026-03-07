import os
import tempfile
import unittest

import cv2
import numpy as np

from src.logic import mediaEditor


class TestMergeAndBlendVideos(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.video1 = os.path.join(self.temp_dir.name, "v1.mp4")
        self.video2 = os.path.join(self.temp_dir.name, "v2.mp4")
        self.output = os.path.join(self.temp_dir.name, "merged.mp4")

        self._write_dummy_video(self.video1, (50, 50), (100, 100, 100))
        self._write_dummy_video(self.video2, (50, 50), (200, 200, 200))

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_dummy_video(self, path, size, color):
        width, height = size
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(path, fourcc, 10, (width, height))
        frame = np.full((height, width, 3), color, dtype=np.uint8)
        for _ in range(2):
            out.write(frame)
        out.release()

    def test_merge_outputs_video(self):
        mediaEditor.merge_and_blend_videos(
            [self.video1, self.video2],
            [(0, 0), (50, 0)],
            self.output,
        )

        self.assertTrue(os.path.exists(self.output))
        cap = cv2.VideoCapture(self.output)
        self.assertTrue(cap.isOpened())
        self.assertEqual(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 100)
        self.assertEqual(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), 50)
        cap.release()

    def test_negative_coordinates_raises(self):
        with self.assertRaises(ValueError):
            mediaEditor.merge_and_blend_videos(
                [self.video1, self.video2],
                [(0, 0), (-5, 0)],
                self.output,
            )

    def test_mismatched_lists_raises(self):
        with self.assertRaises(ValueError):
            mediaEditor.merge_and_blend_videos(
                [self.video1, self.video2],
                [(0, 0)],
                self.output,
            )


if __name__ == "__main__":
    unittest.main()
