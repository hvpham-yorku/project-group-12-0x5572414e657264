from typing import List, Tuple, Optional
from dataclasses import dataclass
import os
import cv2
import numpy as np
import numpy.typing as npt
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

from src.database.models import Path, Aisle, Store
from src.database.model_managers import (
    get_aisles_by_store,
    get_customers_by_store,
    get_paths_by_customer,
    get_store_by_id,
)

SIM_BG = (250, 250, 248)
SIM_FLOOR = (235, 238, 242)
SIM_AISLE = (190, 190, 190)
SIM_AISLE_BORDER = (130, 130, 130)


@dataclass(frozen=True)
class HeatmapVideoRenderResult:
    output_path: str
    num_frames: int
    video_seconds: float
    total_paths: int
    filtered_paths: int
    minute_step: int
    persistence_frames: int


# ---------------------------
# NORMALIZATION
# ---------------------------
def log_normalization(matrix: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    return np.log1p(matrix) / np.log1p(matrix.max()) if matrix.max() > 0 else matrix


# ---------------------------
# STORE DIMENSIONS (FROM DB)
# ---------------------------
def get_store_dimensions(store: Store) -> Tuple[int, int]:
    return store.width, store.height


# ---------------------------
# PATHS → MATRIX
# ---------------------------
def paths_to_matrix(
    paths: List[Path],
    store: Store,
    progress_callback=None,
    progress_start: float = 0.0,
    progress_end: float = 1.0,
) -> npt.NDArray[np.float64]:

    width, height = get_store_dimensions(store)
    matrix = np.zeros((height, width))
    total_paths = len(paths)
    if total_paths == 0:
        _emit_scaled_progress(
            progress_callback,
            progress_start,
            progress_end,
            1.0,
            "No path points matched the selected heatmap window.",
        )
        return matrix

    for index, p in enumerate(paths, start=1):
        x = int(p.location_x)
        y = int(p.location_y)

        if 0 <= x < width and 0 <= y < height:
            matrix[y][x] += 1

        if _should_report_progress(index, total_paths):
            _emit_scaled_progress(
                progress_callback,
                progress_start,
                progress_end,
                index / total_paths,
                f"Accumulating heatmap density from path point {index:,}/{total_paths:,}.",
            )

    return matrix


# ---------------------------
# TIME FILTER
# ---------------------------
def filter_paths_by_time_range(
    paths: List[Path], start_hour: int, end_hour: int
) -> List[Path]:
    return [
        p
        for p in paths
        if p.timestamp is not None and start_hour <= p.timestamp.hour < end_hour
    ]


def get_store_heatmap_inputs(store_id: int) -> Tuple[Optional[Store], List[Aisle], List[Path]]:
    store = get_store_by_id(store_id)
    if store is None:
        return None, [], []

    aisles = get_aisles_by_store(store_id)
    paths: List[Path] = []
    for customer in get_customers_by_store(store_id):
        paths.extend(get_paths_by_customer(customer.customer_id))

    return store, aisles, paths


def _emit_progress(progress_callback, progress: float, status: str) -> None:
    if progress_callback is None:
        return
    progress_callback(max(0.0, min(progress, 1.0)), status)


def _emit_scaled_progress(
    progress_callback,
    start_progress: float,
    end_progress: float,
    progress: float,
    status: str,
) -> None:
    progress = max(0.0, min(progress, 1.0))
    _emit_progress(
        progress_callback,
        start_progress + ((end_progress - start_progress) * progress),
        status,
    )


def _should_report_progress(index: int, total: int, max_updates: int = 100) -> bool:
    if total <= 0:
        return index <= 1
    interval = max(total // max_updates, 1)
    return index == 1 or index == total or (index % interval) == 0


def _minute_of_day(timestamp) -> int:
    return (timestamp.hour * 60) + timestamp.minute


def filter_paths_by_minute_range(
    paths: List[Path], start_minute: int, end_minute: int
) -> List[Path]:
    return [
        p
        for p in paths
        if p.timestamp is not None and start_minute <= _minute_of_day(p.timestamp) < end_minute
    ]


def render_simulation_style_background_rgba(
    store: Store,
    aisles: List[Aisle],
    width: int = 640,
    height: int = 360,
) -> npt.NDArray[np.uint8]:
    store_width, store_height = get_store_dimensions(store)
    if store_width <= 0 or store_height <= 0:
        raise ValueError("Store dimensions must be greater than zero to render a background.")

    image = np.full((store_height, store_width, 3), SIM_BG, dtype=np.uint8)
    cv2.rectangle(
        image,
        (0, 0),
        (store_width - 1, store_height - 1),
        SIM_FLOOR,
        -1,
    )
    cv2.rectangle(
        image,
        (0, 0),
        (store_width - 1, store_height - 1),
        (0, 0, 0),
        1,
    )

    for aisle in aisles:
        x1 = max(0, min(store_width - 1, int(aisle.bottom_left_x)))
        x2 = max(0, min(store_width, int(aisle.top_right_x)))
        y1 = max(0, min(store_height - 1, int(store_height - aisle.top_right_y)))
        y2 = max(0, min(store_height, int(store_height - aisle.bottom_left_y)))
        if x2 <= x1 or y2 <= y1:
            continue

        cv2.rectangle(image, (x1, y1), (x2, y2), SIM_AISLE, -1)
        cv2.rectangle(image, (x1, y1), (x2, y2), SIM_AISLE_BORDER, 1)

    resized = cv2.resize(image, (max(width, 1), max(height, 1)), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(resized, cv2.COLOR_RGB2RGBA)


def _load_background_rgb(
    background_image_path: Optional[str],
    background_image_rgba: Optional[npt.NDArray[np.uint8]],
    width: int,
    height: int,
) -> Optional[npt.NDArray[np.uint8]]:
    if background_image_rgba is not None:
        background = background_image_rgba
        if background.shape[2] == 4:
            background = cv2.cvtColor(background, cv2.COLOR_RGBA2RGB)
        return cv2.resize(background, (width, height), interpolation=cv2.INTER_AREA)

    if background_image_path is None:
        return None

    background_bgr = cv2.imread(background_image_path, cv2.IMREAD_COLOR)
    if background_bgr is None:
        return None
    background_rgb = cv2.cvtColor(background_bgr, cv2.COLOR_BGR2RGB)
    return cv2.resize(background_rgb, (width, height), interpolation=cv2.INTER_AREA)


def _render_heatmap_matrix_rgba(
    matrix: npt.NDArray[np.float64],
    aisles: List[Aisle],
    store: Store,
    label: str,
    width: int,
    height: int,
    background_image_path: Optional[str] = None,
    background_image_rgba: Optional[npt.NDArray[np.uint8]] = None,
    progress_callback=None,
    progress_start: float = 0.0,
    progress_end: float = 1.0,
) -> npt.NDArray[np.uint8]:
    store_width, store_height = get_store_dimensions(store)
    if store_width <= 0 or store_height <= 0:
        raise ValueError("Store dimensions must be greater than zero to render a heatmap.")

    _emit_scaled_progress(
        progress_callback,
        progress_start,
        progress_end,
        0.05,
        "Normalizing heatmap density values...",
    )
    matrix = log_normalization(matrix)
    heatmap_uint8 = np.clip(matrix * 255.0, 0, 255).astype(np.uint8)
    _emit_scaled_progress(
        progress_callback,
        progress_start,
        progress_end,
        0.20,
        "Applying the heatmap color scale...",
    )
    heatmap_rgb = cv2.cvtColor(
        cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_INFERNO),
        cv2.COLOR_BGR2RGB,
    )
    heatmap_rgb = np.flipud(heatmap_rgb)

    _emit_scaled_progress(
        progress_callback,
        progress_start,
        progress_end,
        0.35,
        "Preparing the heatmap background...",
    )
    background_rgb = _load_background_rgb(
        background_image_path,
        background_image_rgba,
        store_width,
        store_height,
    )
    if background_rgb is not None:
        heatmap_rgb = cv2.addWeighted(background_rgb, 0.35, heatmap_rgb, 0.65, 0.0)

    _emit_scaled_progress(
        progress_callback,
        progress_start,
        progress_end,
        0.50,
        "Scaling the heatmap image to the preview size...",
    )
    output_rgb = cv2.resize(
        heatmap_rgb,
        (max(width, 1), max(height, 1)),
        interpolation=cv2.INTER_LINEAR,
    )

    scale_x = max(width, 1) / store_width
    scale_y = max(height, 1) / store_height
    total_aisles = len(aisles)
    for index, aisle in enumerate(aisles, start=1):
        x1 = int(round(aisle.bottom_left_x * scale_x))
        x2 = int(round(aisle.top_right_x * scale_x))
        y1 = int(round((store_height - aisle.top_right_y) * scale_y))
        y2 = int(round((store_height - aisle.bottom_left_y) * scale_y))
        if x2 <= x1 or y2 <= y1:
            continue
        cv2.rectangle(output_rgb, (x1, y1), (x2, y2), (255, 255, 255), 1)
        if _should_report_progress(index, total_aisles, max_updates=25):
            _emit_scaled_progress(
                progress_callback,
                progress_start,
                progress_end,
                0.55 + (0.30 * (index / total_aisles)),
                f"Drawing aisle overlay {index:,}/{total_aisles:,}.",
            )

    if total_aisles == 0:
        _emit_scaled_progress(
            progress_callback,
            progress_start,
            progress_end,
            0.85,
            "No aisle overlays to draw.",
        )

    _emit_scaled_progress(
        progress_callback,
        progress_start,
        progress_end,
        0.92,
        "Stamping the heatmap label...",
    )
    cv2.putText(
        output_rgb,
        label,
        (12, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    _emit_scaled_progress(
        progress_callback,
        progress_start,
        progress_end,
        1.0,
        "Heatmap image ready.",
    )
    return cv2.cvtColor(output_rgb, cv2.COLOR_RGB2RGBA)


def _build_overlay_heatmap_figure(
    paths: List[Path],
    store: Store,
    aisles: Optional[List[Aisle]] = None,
    title: str = "Heatmap",
    background_image_path: Optional[str] = None,
    figure_size: Tuple[float, float] = (10.0, 6.0),
    dpi: int = 100,
):
    width, height = get_store_dimensions(store)
    if width <= 0 or height <= 0:
        raise ValueError("Store dimensions must be greater than zero to render a heatmap.")

    matrix = log_normalization(paths_to_matrix(paths, store))
    fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)

    if background_image_path is not None:
        img = plt.imread(background_image_path)
        ax.imshow(img, extent=[0, width, 0, height], origin="lower", aspect="auto")

    heatmap = ax.imshow(
        matrix,
        origin="lower",
        cmap="inferno",
        alpha=0.6,
        extent=[0, width, 0, height],
    )
    plt.colorbar(heatmap, ax=ax, label="Customer Density")

    for aisle in aisles or []:
        aisle_width = max(0, aisle.top_right_x - aisle.bottom_left_x)
        aisle_height = max(0, aisle.top_right_y - aisle.bottom_left_y)
        if aisle_width == 0 or aisle_height == 0:
            continue
        ax.add_patch(
            Rectangle(
                (aisle.bottom_left_x, aisle.bottom_left_y),
                aisle_width,
                aisle_height,
                fill=False,
                edgecolor="white",
                linewidth=1.0,
                alpha=0.65,
            )
        )

    ax.set_title(title)
    ax.set_xlabel("Store Width")
    ax.set_ylabel("Store Height")
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    return fig


# ---------------------------
# HEATMAP OVERLAY (WITH BACKGROUND)
# ---------------------------
def plot_overlay_heatmap(
    paths: List[Path],
    store: Store,
    aisles: Optional[List[Aisle]] = None,
    title: str = "Heatmap",
    background_image_path: Optional[str] = None,
    show: bool = True,
):
    fig = _build_overlay_heatmap_figure(
        paths,
        store,
        aisles=aisles,
        title=title,
        background_image_path=background_image_path,
    )
    if show:
        plt.show()
    return fig


def render_custom_heatmap_rgba(
    paths: List[Path],
    aisles: List[Aisle],
    store: Store,
    start_hour: int,
    end_hour: int,
    width: int = 640,
    height: int = 360,
    background_image_path: Optional[str] = None,
    background_image_rgba: Optional[npt.NDArray[np.uint8]] = None,
    progress_callback=None,
) -> npt.NDArray[np.uint8]:
    _emit_progress(
        progress_callback,
        0.05,
        "Filtering path points for the selected time window...",
    )
    filtered = filter_paths_by_time_range(paths, start_hour, end_hour)
    _emit_progress(
        progress_callback,
        0.15,
        f"Building a density matrix from {len(filtered):,} filtered path points...",
    )
    matrix = paths_to_matrix(
        filtered,
        store,
        progress_callback=progress_callback,
        progress_start=0.15,
        progress_end=0.55,
    )
    return _render_heatmap_matrix_rgba(
        matrix,
        aisles,
        store,
        f"{start_hour:02d}:00 - {end_hour:02d}:00",
        width,
        height,
        background_image_path=background_image_path,
        background_image_rgba=background_image_rgba,
        progress_callback=progress_callback,
        progress_start=0.55,
        progress_end=1.0,
    )


def render_heatmap_video(
    paths: List[Path],
    aisles: List[Aisle],
    store: Store,
    start_hour: int,
    end_hour: int,
    output_path: str,
    width: int = 640,
    height: int = 360,
    fps: int = 12,
    minute_step: int = 1,
    persistence_frames: int = 30,
    background_image_path: Optional[str] = None,
    background_image_rgba: Optional[npt.NDArray[np.uint8]] = None,
    progress_callback=None,
) -> HeatmapVideoRenderResult:
    if minute_step <= 0:
        raise ValueError("Minute step must be greater than zero.")
    if persistence_frames <= 0:
        raise ValueError("Persistence frames must be greater than zero.")

    start_minute = start_hour * 60
    end_minute = end_hour * 60
    if start_minute >= end_minute:
        raise ValueError("End hour must be later than the start hour.")

    filtered_paths = filter_paths_by_minute_range(paths, start_minute, end_minute)
    _emit_progress(
        progress_callback,
        0.03,
        f"Filtered {len(filtered_paths):,} path points for heatmap video generation.",
    )
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    temp_output_path = output_path.replace(".mp4", ".rendering.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))
    _emit_progress(progress_callback, 0.06, "Opened the heatmap video output.")

    if not writer.isOpened():
        fallback_path = output_path.replace(".mp4", ".avi")
        temp_output_path = fallback_path.replace(".avi", ".rendering.avi")
        writer = cv2.VideoWriter(
            temp_output_path,
            cv2.VideoWriter_fourcc(*"MJPG"),
            fps,
            (width, height),
        )
        output_path = fallback_path
        _emit_progress(
            progress_callback,
            0.07,
            f"mp4v unavailable; falling back to {os.path.basename(output_path)}.",
        )
    if not writer.isOpened():
        raise RuntimeError("Failed to open a video writer for the heatmap video output.")

    minute_marks = list(range(start_minute, end_minute, minute_step))
    if not minute_marks:
        minute_marks = [start_minute]

    valid_points: list[tuple[int, int, int]] = []
    store_width, store_height = get_store_dimensions(store)
    total_filtered_paths = len(filtered_paths)
    for index, path in enumerate(filtered_paths, start=1):
        if path.timestamp is None:
            continue
        x = int(path.location_x)
        y = int(path.location_y)
        if 0 <= x < store_width and 0 <= y < store_height:
            valid_points.append((_minute_of_day(path.timestamp), x, y))
        if _should_report_progress(index, total_filtered_paths):
            _emit_scaled_progress(
                progress_callback,
                0.08,
                0.25,
                index / total_filtered_paths,
                f"Preparing video path point {index:,}/{total_filtered_paths:,}.",
            )
    valid_points.sort()
    if total_filtered_paths == 0:
        _emit_progress(
            progress_callback,
            0.25,
            "No path points matched the selected heatmap video window.",
        )

    trailing_matrix = np.zeros((store_height, store_width), dtype=np.float64)
    recent_frame_points: list[list[tuple[int, int]]] = []
    point_index = 0
    num_frames = len(minute_marks)
    _emit_progress(
        progress_callback,
        0.25,
        f"Rendering {num_frames} heatmap frames minute-by-minute.",
    )

    for frame_index, minute_mark in enumerate(minute_marks, start=1):
        if len(recent_frame_points) >= persistence_frames:
            expired_points = recent_frame_points.pop(0)
            for x, y in expired_points:
                trailing_matrix[y][x] = max(0.0, trailing_matrix[y][x] - 1.0)

        frame_points: list[tuple[int, int]] = []
        while point_index < len(valid_points) and valid_points[point_index][0] <= minute_mark:
            _, x, y = valid_points[point_index]
            trailing_matrix[y][x] += 1.0
            frame_points.append((x, y))
            point_index += 1
        recent_frame_points.append(frame_points)

        label = f"{minute_mark // 60:02d}:{minute_mark % 60:02d}"
        frame_rgba = _render_heatmap_matrix_rgba(
            trailing_matrix,
            aisles,
            store,
            label,
            width,
            height,
            background_image_path=background_image_path,
            background_image_rgba=background_image_rgba,
        )
        frame_bgr = cv2.cvtColor(frame_rgba, cv2.COLOR_RGBA2BGR)
        writer.write(frame_bgr)

        _emit_scaled_progress(
            progress_callback,
            0.25,
            0.97,
            frame_index / num_frames,
            f"Rendering heatmap frame {frame_index}/{num_frames} at {label}.",
        )

    writer.release()
    output_abs_path = os.path.abspath(output_path)
    temp_abs_path = os.path.abspath(temp_output_path)
    if os.path.exists(output_abs_path):
        os.remove(output_abs_path)
    _emit_progress(progress_callback, 0.99, "Finalizing the heatmap video output...")
    os.replace(temp_abs_path, output_abs_path)
    _emit_progress(
        progress_callback,
        1.0,
        f"Heatmap video render complete. Saved to {output_abs_path}",
    )

    return HeatmapVideoRenderResult(
        output_path=output_abs_path,
        num_frames=num_frames,
        video_seconds=num_frames / max(fps, 1),
        total_paths=len(paths),
        filtered_paths=len(filtered_paths),
        minute_step=minute_step,
        persistence_frames=persistence_frames,
    )


# ---------------------------
# CUSTOM TIME HEATMAP (ONLY ONE YOU NEED)
# ---------------------------
def generate_custom_heatmap(
    paths: List[Path],
    aisles: List[Aisle],  # kept for compatibility
    store: Store,
    start_hour: int,
    end_hour: int,
    background_image_path: Optional[str] = None,
):
    filtered = filter_paths_by_time_range(paths, start_hour, end_hour)

    return plot_overlay_heatmap(
        filtered,
        store,
        aisles=aisles,
        title=f"{start_hour}:00 - {end_hour}:00",
        background_image_path=background_image_path,
    )
