import os
import tempfile
import unittest

import cv2
import numpy as np

from src.logic import mediaEditor


class TestMergeAndBlendImages(unittest.TestCase):

    def setUp(self):
        """Sets up basic dummy images to use across multiple tests."""
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create two 50x50 solid color blocks.
        # We use values of 100 and 200 because they average perfectly to 150.
        self.img1 = np.full((50, 50, 3), 100, dtype=np.uint8)
        self.img2 = np.full((50, 50, 3), 200, dtype=np.uint8)

        self.img1_path = os.path.join(self.temp_dir.name, "img1.png")
        self.img2_path = os.path.join(self.temp_dir.name, "img2.png")
        cv2.imwrite(self.img1_path, self.img1)
        cv2.imwrite(self.img2_path, self.img2)
        self.output_path = os.path.join(self.temp_dir.name, "merged.png")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_negative_coordinates_raises_error(self):
        """Tests that the function immediately throws a ValueError for negative coordinates."""
        image_paths = [self.img1_path, self.img2_path]
        coords = [(0, 0), (50, -10)]

        with self.assertRaises(ValueError) as context:
            mediaEditor.merge_and_blend_images(image_paths, coords, self.output_path)

        self.assertIn(
            "YOUR X AND Y COORDS MUST ALL BE ABOVE OR EQUAL TO 0",
            str(context.exception),
        )

    def test_mismatched_lists_returns_none(self):
        """Tests that passing different sized lists returns None."""
        image_paths = [self.img1_path, self.img2_path]
        coords = [(0, 0)]

        result = mediaEditor.merge_and_blend_images(
            image_paths, coords, self.output_path
        )

        self.assertIsNone(
            result, "Function should return None when list lengths mismatch."
        )

    def test_successful_side_by_side_merge(self):
        """Tests merging two images with zero overlap."""
        image_paths = [self.img1_path, self.img2_path]
        coords = [(0, 0), (50, 0)]

        result = mediaEditor.merge_and_blend_images(
            image_paths, coords, self.output_path
        )

        # The new canvas should be 50 pixels high and 100 pixels wide (50 + 50)
        self.assertEqual(result.shape, (50, 100, 3))

        # Check a pixel in the first image's area (should be 100)
        self.assertTrue(np.array_equal(result[25, 25], [100, 100, 100]))

        # Check a pixel in the second image's area (should be 200)
        self.assertTrue(np.array_equal(result[25, 75], [200, 200, 200]))

    def test_successful_overlap_blending(self):
        """Tests that overlapping pixels are mathematically averaged correctly."""
        image_paths = [self.img1_path, self.img2_path]
        coords = [(0, 0), (25, 0)]

        result = mediaEditor.merge_and_blend_images(
            image_paths, coords, self.output_path
        )

        # The new canvas width should be 75 (img1 takes 0-50, img2 takes 25-75)
        self.assertEqual(result.shape, (50, 75, 3))

        # Check a pixel where ONLY image 1 exists (x = 10). Should be 100.
        self.assertTrue(np.array_equal(result[25, 10], [100, 100, 100]))

        # Check a pixel where ONLY image 2 exists (x = 60). Should be 200.
        self.assertTrue(np.array_equal(result[25, 60], [200, 200, 200]))

        # Check a pixel in the OVERLAP zone (x = 30).
        # The math should average 100 and 200 to exactly 150.
        self.assertTrue(
            np.array_equal(result[25, 30], [150, 150, 150]),
            "The overlapping area did not blend to the correct average.",
        )


if __name__ == "__main__":
    unittest.main()
