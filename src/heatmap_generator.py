import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from collections import defaultdict
from datetime import datetime

#Normalization
def log_normalization(matrix):
    return np.log1p(matrix)/np.log1p(matrix.max()) if matrix.max() > 0 else matrix

#Group paths by minute
def group_paths_by_minute(paths):
    grouped = defaultdict(list)
    for p in paths:
        minute_key = p.timestamp.replace(second=0, microsecond=0)
        grouped[minute_key].append(p)

    return grouped

#use paths to make a matrix
def paths_to_matrix(paths, grid_size=(100, 60)):
    matrix = np.zeros(grid_size)

    for p in paths:
        x = int(p.location_x)
        y = int(p.location_y)

        if 0 <= x < grid_size[0] and 0 <= y < grid_size[1]:
            matrix[x][y] += 1

    return matrix

