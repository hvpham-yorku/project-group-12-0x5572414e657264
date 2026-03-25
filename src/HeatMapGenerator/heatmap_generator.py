from typing import List, Tuple
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from datetime import datetime

from src.database.models import Path, Aisle


# ---------------------------
# NORMALIZATION
# ---------------------------
def log_normalization(matrix: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    return np.log1p(matrix) / np.log1p(matrix.max()) if matrix.max() > 0 else matrix


# ---------------------------
# DYNAMIC STORE DIMENSIONS
# ---------------------------
def get_store_dimensions(paths: List[Path]) -> Tuple[int, int]:
    max_x = max((p.location_x for p in paths), default=0)
    max_y = max((p.location_y for p in paths), default=0)
    return max_x + 1, max_y + 1


# ---------------------------
# PATHS → MATRIX
# ---------------------------
def paths_to_matrix(paths: List[Path]) -> npt.NDArray[np.float64]:
    width, height = get_store_dimensions(paths)
    matrix = np.zeros((height, width))

    for p in paths:
        x = int(p.location_x)
        y = int(p.location_y)

        if 0 <= x < width and 0 <= y < height:
            matrix[y][x] += 1

    return matrix


# ---------------------------
# TIME FILTER
# ---------------------------
def filter_paths_by_time_range(
        paths: List[Path],
        start_hour: int,
        end_hour: int
) -> List[Path]:
    return [
        p for p in paths
        if p.timestamp is not None and start_hour <= p.timestamp.hour < end_hour
    ]


# ---------------------------
# DRAW STORE LAYOUT (DB-DRIVEN)
# ---------------------------
def draw_store_layout(
        ax: Axes,
        aisles: List[Aisle]
) -> None:

    for aisle in aisles:
        width = aisle.top_right_x - aisle.bottom_left_x
        height = aisle.top_right_y - aisle.bottom_left_y

        ax.add_patch(
            plt.Rectangle(
                (aisle.bottom_left_x, aisle.bottom_left_y),
                width,
                height,
                fill=False,
                edgecolor="blue",
                linewidth=2
            )
        )


# ---------------------------
# HEATMAP OVERLAY
# ---------------------------
def plot_overlay_heatmap(
        paths: List[Path],
        aisles: List[Aisle],
        title: str = "Heatmap"
) -> None:

    matrix = log_normalization(paths_to_matrix(paths))
    height, width = matrix.shape

    fig, ax = plt.subplots(figsize=(10, 6))

    heatmap = ax.imshow(
        matrix,
        origin='lower',
        cmap='hot',
        alpha=0.7,
        extent=[0, width, 0, height]
    )

    draw_store_layout(ax, aisles)

    plt.colorbar(heatmap, ax=ax, label="Customer Density")

    ax.set_title(title)
    ax.set_xlabel("Store Width")
    ax.set_ylabel("Store Height")

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    plt.show()


# ---------------------------
# CUSTOM TIME HEATMAP
# ---------------------------
def generate_custom_heatmap(
        paths: List[Path],
        aisles: List[Aisle],
        start_hour: int,
        end_hour: int
):
    filtered = filter_paths_by_time_range(paths, start_hour, end_hour)
    plot_overlay_heatmap(filtered, aisles, f"{start_hour}:00-{end_hour}:00")


# ---------------------------
# MULTI-TIME HEATMAPS
# ---------------------------
def generate_time_range_heatmaps(
        paths: List[Path],
        aisles: List[Aisle]
) -> None:

    time_ranges = [
        ("Morning (7-12)", 7, 12),
        ("Afternoon (12-17)", 12, 17),
        ("Evening (17-23)", 17, 23),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    heatmap = None  # type: ignore

    for ax, (label, start, end) in zip(axes, time_ranges):
        filtered = filter_paths_by_time_range(paths, start, end)
        matrix = log_normalization(paths_to_matrix(filtered))

        height, width = matrix.shape

        heatmap = ax.imshow(
            matrix,
            origin='lower',
            cmap='hot',
            alpha=0.7,
            extent=[0, width, 0, height]
        )

        draw_store_layout(ax, aisles)

        ax.set_title(label)
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

    if heatmap is not None:
        fig.colorbar(heatmap, ax=axes, label="Density")

    plt.tight_layout()
    plt.show()