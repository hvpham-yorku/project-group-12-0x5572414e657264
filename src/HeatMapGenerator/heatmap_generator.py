from typing import List, Tuple, Optional
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
def paths_to_matrix(paths: List[Path], store: Store) -> npt.NDArray[np.float64]:

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
) -> npt.NDArray[np.uint8]:
    filtered = filter_paths_by_time_range(paths, start_hour, end_hour)
    store_width, store_height = get_store_dimensions(store)
    if store_width <= 0 or store_height <= 0:
        raise ValueError("Store dimensions must be greater than zero to render a heatmap.")

    matrix = log_normalization(paths_to_matrix(filtered, store))
    heatmap_uint8 = np.clip(matrix * 255.0, 0, 255).astype(np.uint8)
    heatmap_rgb = cv2.cvtColor(
        cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_INFERNO),
        cv2.COLOR_BGR2RGB,
    )
    heatmap_rgb = np.flipud(heatmap_rgb)

    if background_image_path is not None:
        background_bgr = cv2.imread(background_image_path, cv2.IMREAD_COLOR)
        if background_bgr is not None:
            background_rgb = cv2.cvtColor(background_bgr, cv2.COLOR_BGR2RGB)
            background_rgb = cv2.resize(
                background_rgb,
                (store_width, store_height),
                interpolation=cv2.INTER_AREA,
            )
            heatmap_rgb = cv2.addWeighted(background_rgb, 0.35, heatmap_rgb, 0.65, 0.0)

    output_rgb = cv2.resize(
        heatmap_rgb,
        (max(width, 1), max(height, 1)),
        interpolation=cv2.INTER_LINEAR,
    )

    scale_x = max(width, 1) / store_width
    scale_y = max(height, 1) / store_height
    for aisle in aisles:
        x1 = int(round(aisle.bottom_left_x * scale_x))
        x2 = int(round(aisle.top_right_x * scale_x))
        y1 = int(round((store_height - aisle.top_right_y) * scale_y))
        y2 = int(round((store_height - aisle.bottom_left_y) * scale_y))
        if x2 <= x1 or y2 <= y1:
            continue
        cv2.rectangle(output_rgb, (x1, y1), (x2, y2), (255, 255, 255), 1)

    cv2.putText(
        output_rgb,
        f"{start_hour:02d}:00 - {end_hour:02d}:00",
        (12, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return cv2.cvtColor(output_rgb, cv2.COLOR_RGB2RGBA)


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
