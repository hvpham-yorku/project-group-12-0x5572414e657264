"""
Video-based people tracking using YOLOv8 (ONNX Runtime) person detection
and greedy nearest-neighbour matching for frame-to-frame data association.

Pipeline
--------
1.  ``detect_people_in_frame`` – runs a YOLOv8 ONNX model on a single
    frame and returns centroid + bounding-box detections for every person.
2.  ``track_people_in_video`` – iterates every frame of a video file,
    feeds each into (1), then stitches detections across frames into
    coherent per-person trajectories via Kalman-predicted positions and
    greedy cost-matrix matching.
3.  ``save_tracked_paths`` – converts the tracked trajectories into
    ``Customer`` and ``Path`` model objects and persists them through
    the existing ``model_managers`` layer.

Dependencies: opencv-python, numpy, onnxruntime  (no scipy, no ultralytics)
"""

from __future__ import annotations

import os
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import onnxruntime as ort

from src.database.models import Customer, Path
from src.database import model_managers

_COCO_PERSON_CLASS = 0
_MODEL_INPUT_SIZE = 640
_MODEL_URL = (
    "https://huggingface.co/inference4j/yolov8n/resolve/main/yolov8n.onnx"
)
_DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "assets", "yolov8n.onnx",
)


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
# ONNX model management
# ---------------------------------------------------------------------------

def _ensure_model(model_path: str) -> str:
    """Return *model_path* if it already exists, otherwise download it."""
    if os.path.isfile(model_path):
        return model_path

    directory = os.path.dirname(model_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    print(f"Downloading YOLOv8n ONNX model to '{model_path}' ...")
    try:
        urllib.request.urlretrieve(_MODEL_URL, model_path)
    except Exception as exc:
        raise RuntimeError(
            f"Auto-download failed ({exc}).\n"
            f"Please download yolov8n.onnx manually from:\n"
            f"  {_MODEL_URL}\n"
            f"and place it at: {model_path}"
        ) from exc

    print("Download complete.")
    return model_path


# ---------------------------------------------------------------------------
# YOLO pre-processing / post-processing
# ---------------------------------------------------------------------------

def _preprocess(frame: np.ndarray) -> Tuple[np.ndarray, float, int, int]:
    """Letterbox-resize *frame* to 640x640 and build the ONNX input blob.

    Returns ``(blob, scale, pad_w, pad_h)`` so post-processing can map
    coordinates back to the original frame.
    """
    h, w = frame.shape[:2]
    scale = min(_MODEL_INPUT_SIZE / w, _MODEL_INPUT_SIZE / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(frame, (new_w, new_h))

    pad_w = (_MODEL_INPUT_SIZE - new_w) // 2
    pad_h = (_MODEL_INPUT_SIZE - new_h) // 2
    padded = np.full(
        (_MODEL_INPUT_SIZE, _MODEL_INPUT_SIZE, 3), 114, dtype=np.uint8,
    )
    padded[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized

    blob = padded[:, :, ::-1].astype(np.float32) / 255.0   # BGR -> RGB + normalise
    blob = np.ascontiguousarray(blob.transpose(2, 0, 1)[np.newaxis, ...])
    return blob, scale, pad_w, pad_h


def _postprocess(
    output: np.ndarray,
    scale: float,
    pad_w: int,
    pad_h: int,
    conf_threshold: float,
    iou_threshold: float,
) -> List[Detection]:
    """Parse the raw YOLO output tensor into ``Detection`` objects.

    The model outputs shape ``(1, 84, 8400)`` -- 8 400 anchor proposals
    each carrying 4 box values (cx, cy, w, h in 640-space) and 80 COCO
    class scores.
    """
    preds = output[0].transpose()                       # (8400, 84)

    class_scores = preds[:, 4:]
    max_scores = class_scores.max(axis=1)
    class_ids = class_scores.argmax(axis=1)

    mask = (max_scores >= conf_threshold) & (class_ids == _COCO_PERSON_CLASS)
    preds = preds[mask]
    max_scores = max_scores[mask]

    if len(preds) == 0:
        return []

    cx = preds[:, 0]
    cy = preds[:, 1]
    bw = preds[:, 2]
    bh = preds[:, 3]

    # Convert centre-format to top-left-format and map to original frame.
    x = (cx - bw / 2 - pad_w) / scale
    y = (cy - bh / 2 - pad_h) / scale
    bw = bw / scale
    bh = bh / scale

    boxes = np.stack([x, y, bw, bh], axis=1)

    indices = cv2.dnn.NMSBoxes(
        boxes.tolist(), max_scores.tolist(), conf_threshold, iou_threshold,
    )
    if len(indices) == 0:
        return []
    indices = np.asarray(indices).flatten()

    detections: List[Detection] = []
    for i in indices:
        bx, by, w, h = boxes[i]
        detections.append(Detection(
            x=int(bx + w / 2),
            y=int(by + h / 2),
            w=max(int(w), 0),
            h=max(int(h), 0),
        ))
    return detections


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
    session: ort.InferenceSession,
    confidence: float = 0.5,
    iou_threshold: float = 0.45,
) -> List[Detection]:
    """Detect people in *frame* using a YOLOv8 ONNX model.

    Parameters
    ----------
    frame:
        A BGR image (numpy array) read from a video or camera.
    session:
        A loaded ``onnxruntime.InferenceSession`` pointing at a YOLOv8
        ONNX model.  Must be reused across calls to avoid reloading
        weights every frame.
    confidence:
        Minimum detection confidence.  Boxes below this score are dropped.
    iou_threshold:
        IoU threshold for Non-Maximum Suppression.

    Returns
    -------
    List[Detection]
        One ``Detection`` per person found, carrying the centroid (x, y)
        and bounding-box dimensions (w, h).
    """
    blob, scale, pad_w, pad_h = _preprocess(frame)

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    output = session.run([output_name], {input_name: blob})[0]

    return _postprocess(output, scale, pad_w, pad_h, confidence, iou_threshold)


# ---------------------------------------------------------------------------
# Greedy nearest-neighbour matching (replaces scipy Hungarian)
# ---------------------------------------------------------------------------

def _greedy_match(
    cost: np.ndarray,
    max_distance: float,
) -> List[Tuple[int, int]]:
    """Return ``(row, col)`` pairs picked greedily by ascending cost.

    Iterates every cell in the cost matrix from cheapest to most
    expensive.  Each row and column is used at most once, and pairs
    whose cost exceeds *max_distance* are skipped.
    """
    if cost.size == 0:
        return []
    n_rows, n_cols = cost.shape
    order = np.argsort(cost, axis=None)
    matched: List[Tuple[int, int]] = []
    used_rows: set = set()
    used_cols: set = set()
    for flat in order:
        r, c = divmod(int(flat), n_cols)
        if r in used_rows or c in used_cols:
            continue
        if cost[r, c] > max_distance:
            break
        matched.append((r, c))
        used_rows.add(r)
        used_cols.add(c)
        if len(used_rows) == n_rows or len(used_cols) == n_cols:
            break
    return matched


def _match_detections_to_tracks(
    tracks: Dict[int, _KalmanTrack],
    detections: List[Detection],
    max_distance: float,
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """Assign new detections to existing tracks via greedy matching.

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

    pairs = _greedy_match(cost, max_distance)

    matched = [(track_ids[r], c) for r, c in pairs]
    matched_tids = {track_ids[r] for r, _ in pairs}
    matched_dets = {c for _, c in pairs}

    unmatched_tracks = [t for t in track_ids if t not in matched_tids]
    unmatched_detections = [j for j in range(len(detections)) if j not in matched_dets]
    return matched, unmatched_tracks, unmatched_detections


# ---------------------------------------------------------------------------
# Function 2 – full-video tracking
# ---------------------------------------------------------------------------

def track_people_in_video(
    video_path: str,
    video_start_time: Optional[datetime] = None,
    model_path: str = _DEFAULT_MODEL_PATH,
    confidence: float = 0.5,
    iou_threshold: float = 0.45,
    max_match_distance: float = 50.0,
    max_frames_lost: int = 30,
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
    model_path:
        Path to a YOLOv8 ``.onnx`` model file.  If the file does not
        exist it will be auto-downloaded (~13 MB) on first use.
    confidence:
        Minimum YOLO detection confidence for a person box to be kept.
    iou_threshold:
        IoU threshold for Non-Maximum Suppression.
    max_match_distance:
        Maximum pixel distance between a Kalman prediction and a
        detection for the pair to be considered a valid match.
    max_frames_lost:
        How many consecutive frames a track may go unmatched before
        it is finalized and removed from the active set.
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

    resolved = _ensure_model(model_path)
    session = ort.InferenceSession(
        resolved, providers=["CPUExecutionProvider"],
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

        dets = detect_people_in_frame(frame, session, confidence, iou_threshold)

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
