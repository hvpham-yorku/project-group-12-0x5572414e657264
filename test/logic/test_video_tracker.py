"""
Visual validation script for the video tracking pipeline.

Runs ``track_people_in_video`` on a test video, prints every tracked
coordinate, then generates an annotated output video where each person
is drawn with a unique colour, a trailing path polyline, and an ID label.

Usage (from project root):
    python -m test.logic.test_video_tracker
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import cv2
import numpy as np

from src.logic.videoTracker import (
    PersonTrack,
    TrackedPosition,
    track_people_in_video,
)

INPUT_VIDEO = os.path.join("test", "test_videos", "test_1.mp4")
OUTPUT_VIDEO = os.path.join("test", "test_videos", "test_1_tracked.mp4")

# Visually distinct BGR colours – wraps around for >10 people.
_PALETTE: List[Tuple[int, int, int]] = [
    (75, 25, 230),   # red
    (75, 180, 60),   # green
    (25, 225, 255),  # yellow
    (200, 130, 0),   # blue
    (48, 130, 245),  # orange
    (180, 30, 145),  # purple
    (240, 240, 70),  # cyan
    (230, 50, 240),  # magenta
    (60, 245, 210),  # lime
    (212, 190, 250), # pink
]


def _colour(track_id: int) -> Tuple[int, int, int]:
    return _PALETTE[track_id % len(_PALETTE)]


def _video_offset_label(seconds: float) -> str:
    """Format *seconds* as ``MM:SS.mmm``."""
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:06.3f}"


def _draw_text_with_background(
    frame: np.ndarray,
    text: str,
    origin: Tuple[int, int],
    colour: Tuple[int, int, int] = (255, 255, 255),
    scale: float = 0.5,
    thickness: int = 1,
) -> None:
    """Draw *text* with a dark rectangle behind it for readability."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = origin
    cv2.rectangle(
        frame,
        (x - 2, y - th - 4),
        (x + tw + 2, y + baseline + 2),
        (0, 0, 0),
        cv2.FILLED,
    )
    cv2.putText(frame, text, (x, y), font, scale, colour, thickness, cv2.LINE_AA)


# ---------------------------------------------------------------------------
# Step 1 – print coordinates
# ---------------------------------------------------------------------------

def print_track_coordinates(
    tracks: List[PersonTrack],
    video_start: datetime,
    fps: float,
    total_frames: int,
    width: int,
    height: int,
) -> None:
    duration = total_frames / fps
    print("=" * 60)
    print("  VIDEO TRACKING RESULTS")
    print("=" * 60)
    print(f"  Source    : {INPUT_VIDEO}")
    print(f"  FPS       : {fps:.1f}")
    print(f"  Frames    : {total_frames}")
    print(f"  Duration  : {duration:.1f}s")
    print(f"  Resolution: {width}x{height}")
    print(f"  People    : {len(tracks)}")
    print("=" * 60)

    if not tracks:
        print("\n  (no people detected)\n")
        return

    for track in tracks:
        first_off = (track.positions[0].timestamp - video_start).total_seconds()
        last_off = (track.positions[-1].timestamp - video_start).total_seconds()
        print(
            f"\n--- Person {track.track_id}  "
            f"({len(track.positions)} positions, "
            f"{_video_offset_label(first_off)} - "
            f"{_video_offset_label(last_off)}) ---"
        )
        for pos in track.positions:
            off = (pos.timestamp - video_start).total_seconds()
            print(f"  ({pos.x:4d}, {pos.y:4d})  @  {_video_offset_label(off)}")

    print()


# ---------------------------------------------------------------------------
# Step 2 – generate annotated video
# ---------------------------------------------------------------------------

def generate_tracking_video(
    tracks: List[PersonTrack],
    video_path: str,
    output_path: str,
    video_start: datetime,
) -> None:
    """Re-read *video_path* and overlay tracked paths into *output_path*."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: cannot reopen video '{video_path}' for annotation.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Measure real frame size from an actual decoded frame, then seek back.
    ok, first_frame = cap.read()
    if not ok:
        print("Error: video has no readable frames.")
        cap.release()
        return
    real_h, real_w = first_frame.shape[:2]
    # H.264 requires even dimensions; round down if necessary.
    width = real_w & ~1
    height = real_h & ~1
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    codec_candidates = [
        ("avc1", ".mp4"),
        ("mp4v", ".mp4"),
        ("XVID", ".avi"),
        ("MJPG", ".avi"),
    ]
    out = None
    for codec, ext in codec_candidates:
        candidate_path = os.path.splitext(output_path)[0] + ext
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(candidate_path, fourcc, fps, (width, height))
        if writer.isOpened():
            out = writer
            output_path = candidate_path
            print(f"  Using codec '{codec}' -> {output_path}")
            break
        writer.release()

    if out is None:
        print("Error: no working video codec found. Cannot write output.")
        cap.release()
        return

    needs_resize = (real_w != width or real_h != height)

    # Pre-index: track_id -> [(frame_idx, x, y), ...]
    track_frames: Dict[int, List[Tuple[int, int, int]]] = {}
    for track in tracks:
        entries: List[Tuple[int, int, int]] = []
        for pos in track.positions:
            fi = round((pos.timestamp - video_start).total_seconds() * fps)
            entries.append((fi, pos.x, pos.y))
        track_frames[track.track_id] = entries

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # --- draw trailing polyline + current dot per track ---
        for track_id, entries in track_frames.items():
            colour = _colour(track_id)

            trail = [(x, y) for fi, x, y in entries if fi <= frame_idx]
            if not trail:
                continue

            if len(trail) >= 2:
                pts = np.array(trail, dtype=np.int32).reshape(-1, 1, 2)
                cv2.polylines(frame, [pts], isClosed=False, color=colour, thickness=2)

            current = [(x, y) for fi, x, y in entries if fi == frame_idx]
            if current:
                cx, cy = current[-1]
                cv2.circle(frame, (cx, cy), 7, colour, cv2.FILLED)
                cv2.circle(frame, (cx, cy), 9, (255, 255, 255), 1)
                _draw_text_with_background(
                    frame,
                    f"ID:{track_id}",
                    (cx + 14, cy + 4),
                    colour=colour,
                    scale=0.5,
                    thickness=1,
                )

        # --- HUD overlays ---
        offset_secs = frame_idx / fps
        _draw_text_with_background(
            frame,
            f"Frame {frame_idx}/{total_frames}  |  {_video_offset_label(offset_secs)}",
            (10, 25),
            scale=0.55,
            thickness=1,
        )
        _draw_text_with_background(
            frame,
            f"Tracked: {len(tracks)} people",
            (10, 50),
            scale=0.5,
            thickness=1,
        )

        if needs_resize:
            frame = cv2.resize(frame, (width, height))
        out.write(frame)
        frame_idx += 1

        if frame_idx % 100 == 0:
            pct = frame_idx / total_frames * 100 if total_frames else 0
            print(f"  rendering: frame {frame_idx}/{total_frames} ({pct:.0f}%)")

    cap.release()
    out.release()
    print(f"  Done – saved to: {output_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if not os.path.isfile(INPUT_VIDEO):
        print(f"Error: test video not found at '{INPUT_VIDEO}'")
        print("Place your .mp4 file there and run again.")
        sys.exit(1)

    # Read video metadata before tracking.
    probe = cv2.VideoCapture(INPUT_VIDEO)
    fps = probe.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(probe.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(probe.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(probe.get(cv2.CAP_PROP_FRAME_HEIGHT))
    probe.release()

    video_start = datetime(2000, 1, 1)

    print(f"\nProcessing '{INPUT_VIDEO}' ...")
    tracks = track_people_in_video(INPUT_VIDEO, video_start_time=video_start)
    print(f"Tracking complete – {len(tracks)} people found.\n")

    print_track_coordinates(tracks, video_start, fps, total_frames, width, height)

    print(f"Generating annotated video -> '{OUTPUT_VIDEO}' ...")
    generate_tracking_video(tracks, INPUT_VIDEO, OUTPUT_VIDEO, video_start)


if __name__ == "__main__":
    main()
