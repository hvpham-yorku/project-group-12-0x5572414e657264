import matplotlib
import numpy as np
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.animation import FuncAnimation, PillowWriter
from collections import defaultdict
from src.logic.dataGenerator import (
    STORE_WIDTH, STORE_HEIGHT, NUM_AISLES, AISLE_WIDTH,
    AISLE_GAP, AISLE_Y_START, AISLE_Y_END, AISLE_X_START,
    ENTRANCE_X, ENTRANCE_Y, CHECKOUT_Y, CHECKOUT_X_POSITIONS
)
from datetime import datetime

#Normalization
def log_normalization(matrix):
    return np.log1p(matrix)/np.log1p(matrix.max()) if matrix.max() > 0 else matrix

#use paths to make a matrix
#possible code smell - layout defined as matrix[x][y] instead of matrix[y][x]
def paths_to_matrix(paths, grid_size=(100, 60)):
    matrix = np.zeros((STORE_HEIGHT, STORE_WIDTH))

    for p in paths:
        x = int(p.location_x)
        y = int(p.location_y)

        if 0 <= x < STORE_WIDTH and 0 <= y < STORE_HEIGHT:
            matrix[y][x] += 1

    return matrix

def filter_paths_by_time_range(paths, start_hour, end_hour):
    return [
        p for p in paths
        if start_hour <= p.timestamp.hour < end_hour
    ]

#Group paths by minute
def group_paths_by_minute(paths):
    grouped = defaultdict(list)
    for p in paths:
        minute_key = p.timestamp.replace(second=0, microsecond=0)
        grouped[minute_key].append(p)

    return grouped


#Main heatmap Generator
def generate_heatmap(paths):
    grouped = group_paths_by_minute(paths)

    minute_matrices = {}
    hour_matrices = defaultdict(lambda: np.zeros((100, 60)))

    open_hour = 7
    close_hour = 23

    for minute, minute_paths in grouped.items():
        if not (open_hour <= minute.hour < close_hour):
            continue

        #minute matrix
        m_matrix = paths_to_matrix(minute_paths)
        minute_matrices[minute] = m_matrix

        #aggregate to hour
        hour_key = minute.replace(minute=0)
        hour_matrices[hour_key] += m_matrix

    #Daily aggregation
    daily_matrix = np.sum(list(hour_matrices.values()), axis=0)

    return daily_matrix, minute_matrices, dict(hour_matrices), grouped


#save heatmap
def save_heatmap(matrix, filename="daily_heatmap.png"):
    matrix = log_normalization(matrix)

    plt.imshow(matrix)
    plt.colorbar()
    plt.title("Daily Store Heatmap")
    plt.savefig(filename)
    plt.close()

#Animate heatmap(live view)
def animate_heatmap(minute_matrices, interval=200):
    times = sorted(minute_matrices.keys())
    matrices = [log_normalization(minute_matrices[t]) for t in times]

    fig, ax = plt.subplots()
    heatmap = ax.imshow(matrices[0])
    plt.colorbar(heatmap)

    def update(frame):
        heatmap.set_data(matrices[frame])
        ax.set_title(f"Time: {times[frame].strftime('%H:%M')}")
        return [heatmap]

    anim = FuncAnimation(
        fig,
        update,
        frames=len(matrices),
        interval=100, repeat=False)

    plt.show()

#save animation as GIF
def save_animation(minute_matrices, filename="heatmap.gif"):
    times = sorted(minute_matrices.keys())[::5]
    matrices = [log_normalization(minute_matrices[t]) for t in times]

    fig, ax = plt.subplots()
    heatmap = ax.imshow(matrices[0])

    def update(frame):
        heatmap.set_data(matrices[frame])
        ax.set_title(times[frame].strftime('%H:%M'))
        return [heatmap]

    anim = FuncAnimation(fig, update, frames=len(matrices), interval=200)

    anim.save(filename, writer=PillowWriter(fps=5))
    plt.close()