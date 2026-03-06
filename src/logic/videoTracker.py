"""
Video-based people tracking using OpenCV background subtraction
and the Hungarian algorithm for frame-to-frame data association.

Pipeline
--------
1.  ``detect_people_in_frame`` – runs MOG2 background subtraction on a
    single frame and returns centroid + bounding-box detections.
2.  ``track_people_in_video`` – iterates every frame of a video file,
    feeds each into (1), then stitches detections across frames into
    coherent per-person trajectories via Kalman-predicted positions and
    the Hungarian (Kuhn–Munkres) assignment algorithm.
3.  ``save_tracked_paths`` – converts the tracked trajectories into
    ``Customer`` and ``Path`` model objects and persists them through
    the existing ``model_managers`` layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

from src.database.models import Customer, Path
from src.database import model_managers


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class Detection:
    """Centroid and bounding-box of a single detected person in one frame."""
    x: int
    y: int
    w: int
    h: int


@dataclass
class TrackedPosition:
    """A person's position tied to a specific moment in the video."""
    x: int
    y: int
    timestamp: datetime


@dataclass
class PersonTrack:
    """Full trajectory of one tracked person across multiple frames."""
    track_id: int
    positions: List[TrackedPosition] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal Kalman-based track state
# ---------------------------------------------------------------------------

class _KalmanTrack:
    """Per-person Kalman filter wrapping OpenCV's KalmanFilter.

    State vector  : [x, y, dx, dy]  (position + velocity)
    Measurement   : [x, y]          (observed centroid)
    """

    def __init__(self, track_id: int, x: float, y: float) -> None:
        self.track_id = track_id
        self.frames_lost = 0
        self.positions: List[TrackedPosition] = []

        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0]], dtype=np.float32,
        )
        # position_new = position_old + velocity
        self.kf.transitionMatrix = np.array(
            [[1, 0, 1, 0],
             [0, 1, 0, 1],
             [0, 0, 1, 0],
             [0, 0, 0, 1]], dtype=np.float32,
        )
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 1e-2
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1e-1
        self.kf.errorCovPost = np.eye(4, dtype=np.float32)
        self.kf.statePost = np.array(
            [[x], [y], [0], [0]], dtype=np.float32,
        )

    def predict(self) -> Tuple[float, float]:
        """Advance the internal state by one time-step and return the
        predicted (x, y) centroid."""
        state = self.kf.predict().flatten()
        return float(state[0]), float(state[1])

    def correct(self, x: float, y: float) -> None:
        """Feed an observed measurement back into the filter."""
        self.kf.correct(
            np.array([[x], [y]], dtype=np.float32),
        )
        self.frames_lost = 0


# ---------------------------------------------------------------------------
# Function 1 – single-frame detection
# ---------------------------------------------------------------------------

def detect_people_in_frame(
    frame: np.ndarray,
    bg_subtractor: cv2.BackgroundSubtractorMOG2,
    min_contour_area: int = 500,
) -> List[Detection]:
    """Detect people-sized blobs in *frame* using background subtraction.

    Parameters
    ----------
    frame:
        A BGR image (numpy array) read from a video or camera.
    bg_subtractor:
        A *shared* ``cv2.BackgroundSubtractorMOG2`` instance that must be
        reused across sequential frames so the background model stays
        up-to-date.
    min_contour_area:
        Minimum contour area (in pixels) to be considered a person.
        Contours smaller than this are treated as noise and discarded.

    Returns
    -------
    List[Detection]
        One ``Detection`` per person found, carrying the centroid (x, y)
        and bounding-box dimensions (w, h).
    """
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    fg_mask = bg_subtractor.apply(blurred)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    # MOG2 marks shadows at 127; threshold keeps only definite foreground.
    fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)[1]

    contours, _ = cv2.findContours(
        fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
    )

    detections: List[Detection] = []
    for contour in contours:
        if cv2.contourArea(contour) < min_contour_area:
            continue
        bx, by, bw, bh = cv2.boundingRect(contour)
        detections.append(Detection(
            x=bx + bw // 2,
            y=by + bh // 2,
            w=bw,
            h=bh,
        ))
    return detections


# ---------------------------------------------------------------------------
# Hungarian-algorithm matching helper
# ---------------------------------------------------------------------------

def _match_detections_to_tracks(
    tracks: Dict[int, _KalmanTrack],
    detections: List[Detection],
    max_distance: float,
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """Optimally assign new detections to existing tracks.

    Returns
    -------
    matched :
        ``(track_id, detection_index)`` pairs that were accepted.
    unmatched_track_ids :
        Track IDs that received no detection this frame.
    unmatched_det_indices :
        Detection indices that matched no existing track (new people).
    """
    if not tracks or not detections:
        return (
            [],
            list(tracks.keys()),
            list(range(len(detections))),
        )

    track_ids = list(tracks.keys())
    predictions = {tid: tracks[tid].predict() for tid in track_ids}

    cost = np.zeros((len(track_ids), len(detections)), dtype=np.float64)
    for i, tid in enumerate(track_ids):
        px, py = predictions[tid]
        for j, det in enumerate(detections):
            cost[i, j] = np.hypot(px - det.x, py - det.y)

    row_idx, col_idx = linear_sum_assignment(cost)

    matched: List[Tuple[int, int]] = []
    matched_tids: set = set()
    matched_dets: set = set()

    for r, c in zip(row_idx, col_idx):
        if cost[r, c] <= max_distance:
            matched.append((track_ids[r], c))
            matched_tids.add(track_ids[r])
            matched_dets.add(c)

    unmatched_tracks = [t for t in track_ids if t not in matched_tids]
    unmatched_detections = [j for j in range(len(detections)) if j not in matched_dets]
    return matched, unmatched_tracks, unmatched_detections


# ---------------------------------------------------------------------------
# Function 2 – full-video tracking
# ---------------------------------------------------------------------------

def track_people_in_video(
    video_path: str,
    video_start_time: Optional[datetime] = None,
    min_contour_area: int = 500,
    max_match_distance: float = 50.0,
    max_frames_lost: int = 15,
    warmup_frames: int = 30,
    min_track_length: int = 5,
) -> List[PersonTrack]:
    """Process every frame of *video_path* and return per-person paths.

    Parameters
    ----------
    video_path:
        Filesystem path to the video file.
    video_start_time:
        Real-world time corresponding to frame 0.  Each subsequent
        position is time-stamped as
        ``video_start_time + frame_number / fps``.
        Defaults to ``datetime.now()`` when *None*.
    min_contour_area:
        Forwarded to ``detect_people_in_frame``.
    max_match_distance:
        Maximum pixel distance between a Kalman prediction and a
        detection for the pair to be considered a valid match.
    max_frames_lost:
        How many consecutive frames a track may go unmatched before
        it is finalized and removed from the active set.
    warmup_frames:
        Number of initial frames used exclusively to train the MOG2
        background model (no detections are produced during warmup).
    min_track_length:
        Tracks with fewer positions than this are discarded as noise.

    Returns
    -------
    List[PersonTrack]
        One ``PersonTrack`` per unique person, ordered by first
        appearance.
    """
    if video_start_time is None:
        video_start_time = datetime.now()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {video_path}")

    fps: float = cap.get(cv2.CAP_PROP_FPS) or 30.0
    bg_sub = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=50,
        detectShadows=True,
    )

    active: Dict[int, _KalmanTrack] = {}
    finished: List[PersonTrack] = []
    next_id = 0
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        timestamp = video_start_time + timedelta(seconds=frame_idx / fps)
        frame_idx += 1

        # Let MOG2 learn the background before we start detecting.
        if frame_idx <= warmup_frames:
            bg_sub.apply(frame)
            continue

        dets = detect_people_in_frame(frame, bg_sub, min_contour_area)

        matched, lost_tids, new_det_idxs = _match_detections_to_tracks(
            active, dets, max_match_distance,
        )

        # --- update matched tracks ---
        for tid, det_idx in matched:
            d = dets[det_idx]
            active[tid].correct(d.x, d.y)
            active[tid].positions.append(
                TrackedPosition(d.x, d.y, timestamp),
            )

        # --- spawn tracks for brand-new detections ---
        for det_idx in new_det_idxs:
            d = dets[det_idx]
            trk = _KalmanTrack(next_id, d.x, d.y)
            trk.positions.append(TrackedPosition(d.x, d.y, timestamp))
            active[next_id] = trk
            next_id += 1

        # --- age unmatched tracks ---
        for tid in lost_tids:
            active[tid].frames_lost += 1

        # --- retire tracks that have been lost too long ---
        expired = [
            tid for tid, t in active.items()
            if t.frames_lost > max_frames_lost
        ]
        for tid in expired:
            trk = active.pop(tid)
            if len(trk.positions) >= min_track_length:
                finished.append(
                    PersonTrack(track_id=trk.track_id, positions=trk.positions),
                )

    cap.release()

    # Flush tracks that were still active when the video ended.
    for trk in active.values():
        if len(trk.positions) >= min_track_length:
            finished.append(
                PersonTrack(track_id=trk.track_id, positions=trk.positions),
            )

    return finished


# ---------------------------------------------------------------------------
# Function 3 – persist to database
# ---------------------------------------------------------------------------

def save_tracked_paths(
    tracks: List[PersonTrack],
    store_id: int,
) -> List[Customer]:
    """Write tracked paths to the database as ``Customer`` + ``Path`` rows.

    For every ``PersonTrack`` a ``Customer`` is created whose
    ``entered_at`` / ``exited_at`` span the track's first and last
    timestamps.  Each ``TrackedPosition`` becomes one ``Path`` row
    linked to that customer.

    Parameters
    ----------
    tracks:
        Output of ``track_people_in_video``.
    store_id:
        The store these customers belong to.

    Returns
    -------
    List[Customer]
        The newly created ``Customer`` objects (with assigned IDs).
    """
    saved: List[Customer] = []

    for track in tracks:
        if not track.positions:
            continue

        customer = model_managers.add_customer(Customer(
            store_id=store_id,
            entered_at=track.positions[0].timestamp,
            exited_at=track.positions[-1].timestamp,
        ))

        for pos in track.positions:
            model_managers.add_path(Path(
                customer_id=customer.customer_id,
                location_x=pos.x,
                location_y=pos.y,
                timestamp=pos.timestamp,
            ))

        saved.append(customer)

    return saved
