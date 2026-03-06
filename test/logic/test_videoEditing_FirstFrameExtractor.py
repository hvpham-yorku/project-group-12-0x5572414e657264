import unittest
import cv2
import numpy as np
import os
import tempfile
from src.logic import mediaEditor

# Assuming the function is defined in a file named video_tools.py
# from video_tools import extract_first_frame


class TestFirstFrameExtractor(unittest.TestCase):

    def setUp(self):
        """Sets up a temporary directory and a dummy video for testing."""
        self.test_dir = tempfile.TemporaryDirectory()

        self.input_path = os.path.join(self.test_dir.name, "dummy_input.mp4")
        self.output_image_path = os.path.join(self.test_dir.name, "extracted_frame.jpg")

        # Create a dummy video (100x100 resolution, 3 frames, 10 fps)
        self.video_width = 100
        self.video_height = 100
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            self.input_path, fourcc, 10, (self.video_width, self.video_height)
        )

        # Write a few frames. Let's make the frames solid white so they are easy to verify.
        for _ in range(3):
            frame = (
                np.ones((self.video_height, self.video_width, 3), dtype=np.uint8) * 255
            )
            out.write(frame)

        out.release()

    def tearDown(self):
        """Cleans up the temporary directory after tests run."""
        self.test_dir.cleanup()

    def test_successful_extraction(self):
        """Tests if the first frame is successfully extracted and saved."""
        # Run the function
        result = mediaEditor.extract_first_frame(
            self.input_path, self.output_image_path
        )

        # 1. Verify the function returned True
        self.assertTrue(result, "Function should return True on success.")

        # 2. Check if the output image file actually exists on the disk
        self.assertTrue(
            os.path.exists(self.output_image_path), "Output image was not created."
        )

        # 3. Open the saved image to verify it is valid and has the correct dimensions
        saved_image = cv2.imread(self.output_image_path)
        self.assertIsNotNone(
            saved_image, "The saved image file could not be read by OpenCV."
        )
        self.assertEqual(
            saved_image.shape[1], self.video_width, "Image width does not match video."
        )
        self.assertEqual(
            saved_image.shape[0],
            self.video_height,
            "Image height does not match video.",
        )

    def test_invalid_input_path(self):
        """Tests that the function gracefully fails when given a bad video path."""
        fake_path = os.path.join(self.test_dir.name, "ghost_video.mp4")

        # Run the function
        result = mediaEditor.extract_first_frame(fake_path, self.output_image_path)

        # 1. Verify the function returned False
        self.assertFalse(
            result, "Function should return False when input file is missing."
        )

        # 2. Verify no image was accidentally created
        self.assertFalse(
            os.path.exists(self.output_image_path),
            "An image was created despite the invalid input.",
        )


if __name__ == "__main__":
    unittest.main()
