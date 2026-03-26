from typing import List, Tuple, Optional
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from src.database.models import Path, Aisle, Store


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
        store: Store
) -> npt.NDArray[np.float64]:

    width, height = get_store_dimensions(store)
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
# HEATMAP OVERLAY (WITH BACKGROUND)
# ---------------------------
def plot_overlay_heatmap(
        paths: List[Path],
        store: Store,
        title: str = "Heatmap",
        background_image_path: Optional[str] = None
) -> None:

    matrix = log_normalization(paths_to_matrix(paths, store))
    height, width = matrix.shape

    fig, ax = plt.subplots(figsize=(10, 6))

    # ---------------------------
    # BACKGROUND IMAGE
    # ---------------------------
    if background_image_path is not None:
        img = plt.imread(background_image_path)
        ax.imshow(
            img,
            extent=[0, width, 0, height],
            origin='lower',
            aspect='auto'
        )

    # ---------------------------
    # HEATMAP
    # ---------------------------
    heatmap = ax.imshow(
        matrix,
        origin='lower',
        cmap='inferno',
        alpha=0.6,
        extent=[0, width, 0, height]
    )

    plt.colorbar(heatmap, ax=ax, label="Customer Density")

    ax.set_title(title)
    ax.set_xlabel("Store Width")
    ax.set_ylabel("Store Height")

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    # Optional: cleaner UI
    # ax.axis('off')

    plt.show()


# ---------------------------
# CUSTOM TIME HEATMAP (ONLY ONE YOU NEED)
# ---------------------------
def generate_custom_heatmap(
        paths: List[Path],
        aisles: List[Aisle],  # kept for compatibility
        store: Store,
        start_hour: int,
        end_hour: int,
        background_image_path: Optional[str] = None
):
    filtered = filter_paths_by_time_range(paths, start_hour, end_hour)

    plot_overlay_heatmap(
        filtered,
        store,
        f"{start_hour}:00 - {end_hour}:00",
        background_image_path
    )