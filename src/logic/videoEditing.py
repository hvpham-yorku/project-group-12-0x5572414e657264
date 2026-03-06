import cv2


def crop_video_opencv(input_path, output_path, x, y, width, height):
    """
    Crops a video using OpenCV.

    Notes:
    In OpenCV, an image (or a video frame) is essentially a multi-dimensional
    NumPy array. Because of this, cropping is as simple as using standard Python
    array slicing.

    The coordinate system starts with (0, 0) at the top-left corner.
    The x-axis goes to the right, and the y-axis goes down. To crop, you just
    tell NumPy which rows (y-coordinates) and columns (x-coordinates) you want
    to keep: frame[y:y+height, x:x+width].

    Parameters:
    - input_path (str): Path to the source video.
    - output_path (str): Path to save the cropped video.
    - x (int): Starting x-coordinate (top-left).
    - y (int): Starting y-coordinate (top-left).
    - width (int): Width of the cropped area.
    - height (int): Height of the cropped area.
    """
    # 1. Open the input video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_path}")
        return

    # 2. Get the frames per second (fps) of the original video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 3. Define the codec and create a VideoWriter object
    # 'mp4v' is a good default for .mp4 files. Use 'XVID' for .avi
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # CRITICAL: The VideoWriter dimensions MUST match the cropped width and height
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Processing video... Output will be {width}x{height} at {fps} fps.")

    # 4. Loop through the video frame by frame
    while True:
        ret, frame = cap.read()

        # If ret is False, we've reached the end of the video
        if not ret:
            break

        # 5. Crop the frame
        # NumPy array slicing format is [start_y : end_y, start_x : end_x]
        cropped_frame = frame[y : y + height, x : x + width]

        # 6. Write the cropped frame to the output video
        out.write(cropped_frame)

    # 7. Clean up and release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Cropping complete!")


# --- Example Usage ---
# crop_video_opencv('input.mp4', 'output_cropped.mp4', x=100, y=50, width=640, height=480)
