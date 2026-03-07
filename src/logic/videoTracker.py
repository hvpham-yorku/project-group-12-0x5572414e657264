"""
Video-based people tracking using Ultralytics YOLOv8 for person detection
and ByteTrack for frame-to-frame data association.

Pipeline
--------
1.  ``detect_people_in_frame`` – runs YOLOv8 on a single frame and returns
    centroid + bounding-box detections for every person.
2.  ``track_people_in_video`` – iterates every frame of a video file,
    runs YOLOv8 with ByteTrack persistence, and returns per-person
    trajectories with stable IDs.
3.  ``save_tracked_paths`` – converts the tracked trajectories into
    ``Customer`` and ``Path`` model objects and persists them through
    the existing ``model_managers`` layer.

Dependencies: ultralytics, opencv-python, numpy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

from src.database.models import Customer, Path
from src.database import model_managers

_COCO_PERSON_CLASS = 0


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
# Function 1 – single-frame detection
# ---------------------------------------------------------------------------

def detect_people_in_frame(
    frame: np.ndarray,
    model: YOLO,
    confidence: float = 0.25,
) -> List[Detection]:
    """Detect people in *frame* using YOLOv8.

    Parameters
    ----------
    frame:
        A BGR image (numpy array) read from a video or camera.
    model:
        A loaded ``ultralytics.YOLO`` model instance.  Must be reused
        across calls to avoid reloading weights every frame.
    confidence:
        Minimum detection confidence.  Boxes below this score are dropped.

    Returns
    -------
    List[Detection]
        One ``Detection`` per person found, carrying the centroid (x, y)
        and bounding-box dimensions (w, h).
    """
    results = model.predict(
        frame, classes=[_COCO_PERSON_CLASS], conf=confidence, verbose=False,
    )
    detections: List[Detection] = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        w = int(x2 - x1)
        h = int(y2 - y1)
        detections.append(Detection(
            x=int((x1 + x2) / 2),
            y=int((y1 + y2) / 2),
            w=w,
            h=h,
        ))
    return detections


# ---------------------------------------------------------------------------
# Post-processing – merge fragmented tracks
# ---------------------------------------------------------------------------

def _on_edge(x: int, y: int, width: int, height: int,
             margin_frac: float) -> bool:
    """Return ``True`` if (x, y) is within *margin_frac* of a frame edge."""
    mx = int(width * margin_frac)
    my = int(height * margin_frac)
    return x < mx or x > width - mx or y < my or y > height - my


def _merge_fragmented_tracks(
    tracks: List[PersonTrack],
    frame_width: int,
    frame_height: int,
    edge_margin: float = 0.10,
) -> List[PersonTrack]:
    """Stitch track fragments that belong to the same physical person.

    Hard rule: people can only enter/exit through the frame edges.
    Any track that *starts* in the middle of the frame is guaranteed
    to be a continuation of someone already present, so it is always
    merged with the best available predecessor — no hard distance or
    time cutoffs.

    Tracks are processed in chronological order.  Each group maintains
    a running endpoint so that chained fragments (A → B → C) resolve
    correctly.

    Parameters
    ----------
    tracks:
        Raw tracks from the YOLO + ByteTrack pass.
    frame_width, frame_height:
        Pixel dimensions of the video frame.
    edge_margin:
        Fraction of the frame considered "edge zone" (0.10 = 10%).
    """
    if len(tracks) <= 1:
        return tracks

    order = sorted(
        range(len(tracks)),
        key=lambda i: tracks[i].positions[0].timestamp
        if tracks[i].positions else datetime.max,
    )

    # Each group: list of track indices, plus its latest endpoint.
    groups: List[List[int]] = []
    group_end_time: List[datetime] = []
    group_end_xy: List[Tuple[int, int]] = []
    group_end_on_edge: List[bool] = []

    for idx in order:
        t = tracks[idx]
        if not t.positions:
            continue

        first = t.positions[0]
        last = t.positions[-1]

        starts_mid = not _on_edge(
            first.x, first.y, frame_width, frame_height, edge_margin,
        )

        merged_into = None
        if starts_mid and groups:
            best_score = float("inf")
            for g, _ in enumerate(groups):
                if group_end_on_edge[g]:
                    continue
                gap = (first.timestamp - group_end_time[g]).total_seconds()
                if gap < 0:
                    continue
                ex, ey = group_end_xy[g]
                dist = float(np.hypot(first.x - ex, first.y - ey))
                score = gap * 100.0 + dist
                if score < best_score:
                    best_score = score
                    merged_into = g

        if merged_into is not None:
            groups[merged_into].append(idx)
            group_end_time[merged_into] = last.timestamp
            group_end_xy[merged_into] = (last.x, last.y)
            group_end_on_edge[merged_into] = _on_edge(
                last.x, last.y, frame_width, frame_height, edge_margin,
            )
        else:
            groups.append([idx])
            group_end_time.append(last.timestamp)
            group_end_xy.append((last.x, last.y))
            group_end_on_edge.append(_on_edge(
                last.x, last.y, frame_width, frame_height, edge_margin,
            ))

    result: List[PersonTrack] = []
    for grp in groups:
        combined = PersonTrack(track_id=tracks[grp[0]].track_id)
        for i in grp:
            combined.positions.extend(tracks[i].positions)
        combined.positions.sort(key=lambda p: p.timestamp)
        result.append(combined)

    result.sort(
        key=lambda t: t.positions[0].timestamp if t.positions else datetime.max,
    )
    return result


# ---------------------------------------------------------------------------
# Function 2 – full-video tracking
# ---------------------------------------------------------------------------

def track_people_in_video(
    video_path: str,
    video_start_time: Optional[datetime] = None,
    model_path: str = "yolov8n.pt",
    confidence: float = 0.25,
    min_track_length: int = 5,
    edge_margin: float = 0.10,
) -> List[PersonTrack]:
    """Process every frame of *video_path* and return per-person paths.

    Uses YOLOv8 for person detection and ByteTrack for multi-object
    tracking.  A post-processing pass then merges track fragments that
    start in the middle of the frame (not at an edge), exploiting the
    physical constraint that people can only enter or leave through the
    frame borders.  Any mid-frame appearance is unconditionally merged
    with the best available predecessor — there are no hard distance or
    time cutoffs.

    Parameters
    ----------
    video_path:
        Filesystem path to the video file.
    video_start_time:
        Real-world time corresponding to frame 0.  Each subsequent
        position is time-stamped as
        ``video_start_time + frame_number / fps``.
        Defaults to ``datetime.now()`` when *None*.
    model_path:
        Path to a YOLOv8 model file.  Defaults to ``yolov8n.pt``
        which is auto-downloaded on first use (~6 MB).
    confidence:
        Minimum YOLO detection confidence for a person box to be kept.
    min_track_length:
        Tracks with fewer positions than this are discarded as noise.
    edge_margin:
        Fraction of the frame considered "edge zone" (0.10 = 10%).

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
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    model = YOLO(model_path)

    tracks_dict: Dict[int, PersonTrack] = {}
    first_seen: Dict[int, int] = {}
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        timestamp = video_start_time + timedelta(seconds=frame_idx / fps)

        results = model.track(
            frame,
            classes=[_COCO_PERSON_CLASS],
            conf=confidence,
            persist=True,
            verbose=False,
        )

        boxes = results[0].boxes
        if boxes.id is not None:
            track_ids = boxes.id.cpu().numpy().astype(int)
            coords = boxes.xyxy.cpu().numpy()

            for tid, (x1, y1, x2, y2) in zip(track_ids, coords):
                tid = int(tid)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                if tid not in tracks_dict:
                    tracks_dict[tid] = PersonTrack(track_id=tid)
                    first_seen[tid] = frame_idx

                tracks_dict[tid].positions.append(
                    TrackedPosition(cx, cy, timestamp),
                )

        frame_idx += 1

    cap.release()

    raw = [
        t for t in sorted(tracks_dict.values(),
                          key=lambda t: first_seen.get(t.track_id, 0))
        if len(t.positions) >= min_track_length
    ]

    merged = _merge_fragmented_tracks(
        raw, frame_width, frame_height, edge_margin=edge_margin,
    )

    return [t for t in merged if len(t.positions) >= min_track_length]


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
