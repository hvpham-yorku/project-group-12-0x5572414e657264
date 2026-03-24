from typing import List, Optional, Tuple
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from src.database.models import Path, Aisle, Checkout
from datetime import datetime

from src.logic.dataGenerator import (
    STORE_WIDTH, STORE_HEIGHT, NUM_AISLES, AISLE_WIDTH,
    AISLE_GAP, AISLE_Y_START, AISLE_Y_END, AISLE_X_START,
    ENTRANCE_X, ENTRANCE_Y, CHECKOUT_Y, CHECKOUT_X_POSITIONS
)


#Normalization
def log_normalization(matrix: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    return np.log1p(matrix)/np.log1p(matrix.max()) if matrix.max() > 0 else matrix

#use paths to make a matrix
def paths_to_matrix(paths: List[Path]) -> npt.NDArray[np.float64]:
    matrix: npt.NDArray[np.float64] = np.zeros((STORE_HEIGHT, STORE_WIDTH))

    for p in paths:
        x = int(p.location_x)
        y = int(p.location_y)

        if 0 <= x < STORE_WIDTH and 0 <= y < STORE_HEIGHT:
            matrix[y][x] += 1

    return matrix

def filter_paths_by_time_range(
        paths: List[Path],
        start_hour: int,
        end_hour: int
) -> List[Path]:
    return [
        p for p in paths
        if start_hour <= p.timestamp.hour < end_hour
    ]

#definea store layout that's consistent with dataGenerator
def draw_store_layout(ax: Axes) -> None:
    #Aisles
    for i in range(NUM_AISLES):
        x = AISLE_X_START + i * (AISLE_WIDTH + AISLE_GAP)

        ax.add_patch(
            plt.Rectangle(
                (x, AISLE_Y_START),
                AISLE_WIDTH,
                AISLE_Y_END - AISLE_Y_START,
                fill=False,
                edgecolor="blue",
                linewidth=2
            )
        )

    #checkout counters
    for x in CHECKOUT_X_POSITIONS:
        ax.add_patch(
            plt.Rectangle(
                (x - 3, 0),
                6,
                CHECKOUT_Y,
                fill=False,
                edgecolor="green",
                linewidth=2
            )
        )

    #Entrance
    ax.scatter(ENTRANCE_X, ENTRANCE_Y, color="black", s=50, label="Entrance")

#overlay heatmap
def plot_overlay_heatmap(
        paths:List[Path],
        title: str ="Heatmap"
) -> None:
    matrix = paths_to_matrix(paths)
    matrix = log_normalization(matrix)

    fig, ax = plt.subplots(figsize=(10, 6))

    heatmap = ax.imshow(
        matrix,
        origin='lower',
        cmap='hot',
        alpha=0.7,
        extent=[0, STORE_WIDTH, 0, STORE_HEIGHT]
    )

    draw_store_layout(ax)

    plt.colorbar(heatmap, ax=ax, label="Customer Density")

    ax.set_title(title)
    ax.set_xlabel("Store Width")
    ax.set_ylabel("Store Height")

    ax.set_xlim(0, STORE_WIDTH)
    ax.set_ylim(0, STORE_HEIGHT)

    plt.show()

def generate_custom_heatmap(
        paths: List[Path],
        start_hour: int,
        end_hour: int
):
    filtered = filter_paths_by_time_range(paths, start_hour, end_hour)
    plot_overlay_heatmap(filtered, f"{start_hour}:00-{end_hour}:00")

def generate_time_range_heatmaps(paths: List[Path]) -> None:
    time_ranges = [
        ("Morning (7-12)", 7, 12),
        ("Afternoon (12-17)", 12, 17),
        ("Evening (17-23)", 17, 23),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    heatmap = None #type: ignore
    for ax, (label, start, end) in zip(axes, time_ranges):
        filtered = filter_paths_by_time_range(paths, start, end)
        matrix = log_normalization(paths_to_matrix(filtered))

        heatmap = ax.imshow(
            matrix,
            origin='lower',
            cmap='hot',
            alpha=0.7,
            extent=[0, STORE_WIDTH, 0, STORE_HEIGHT]
        )

        draw_store_layout(ax)

        ax.set_title(label)
        ax.set_xlim(0, STORE_WIDTH)
        ax.set_ylim(0, STORE_HEIGHT)

    if heatmap is not None:
        fig.colorbar(heatmap, ax=axes, label="Density")

    plt.tight_layout()
    plt.show()
