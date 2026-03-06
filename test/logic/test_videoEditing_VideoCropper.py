import unittest
import cv2
import numpy as np
import os
import tempfile
from src.logic import videoEditing


class TestVideoCropper(unittest.TestCase):

    def setUp(self):
        """Runs before every test. Sets up a temporary directory and a dummy video."""
        # Create a temporary directory to hold our test videos
        self.test_dir = tempfile.TemporaryDirectory()

        self.input_path = os.path.join(self.test_dir.name, "dummy_input.mp4")
        self.output_path = os.path.join(self.test_dir.name, "dummy_output.mp4")

        # Create a dummy video (100x100 resolution, 5 frames, 10 fps)
        self.original_width = 100
        self.original_height = 100
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            self.input_path, fourcc, 10, (self.original_width, self.original_height)
        )

        for _ in range(5):
            # Create a simple black frame
            frame = np.zeros(
                (self.original_height, self.original_width, 3), dtype=np.uint8
            )
            out.write(frame)

        out.release()

    def tearDown(self):
        """Runs after every test. Cleans up the temporary directory."""
        self.test_dir.cleanup()

    def test_successful_crop(self):
        """Tests if the video is successfully cropped to the correct dimensions."""
        crop_x, crop_y = 10, 20
        crop_w, crop_h = 50, 40

        # Run the function
        videoEditing.crop_video_opencv(
            self.input_path, self.output_path, crop_x, crop_y, crop_w, crop_h
        )

        # 1. Check if output file was created
        self.assertTrue(
            os.path.exists(self.output_path), "Output video file was not created."
        )

        # 2. Open the output video to verify its properties
        cap = cv2.VideoCapture(self.output_path)
        self.assertTrue(cap.isOpened(), "Could not open the generated output video.")

        # 3. Verify the new dimensions match the crop_w and crop_h
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.assertEqual(
            actual_width, crop_w, f"Expected width {crop_w}, got {actual_width}"
        )
        self.assertEqual(
            actual_height, crop_h, f"Expected height {crop_h}, got {actual_height}"
        )

        # 4. Verify the video actually contains frames
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.assertGreater(frame_count, 0, "Output video has no frames.")

        cap.release()

    def test_invalid_input_path(self):
        """Tests that the function handles non-existent files gracefully without crashing."""
        fake_path = os.path.join(self.test_dir.name, "does_not_exist.mp4")

        # Run the function with a bad input path.
        # Since our function just prints an error and returns, we are checking that
        # it doesn't raise an unhandled exception (like a missing file error).
        videoEditing.crop_video_opencv(fake_path, self.output_path, 0, 0, 50, 50)

        # Verify the output file was NOT created
        self.assertFalse(os.path.exists(self.output_path))


if __name__ == "__main__":
    unittest.main()
