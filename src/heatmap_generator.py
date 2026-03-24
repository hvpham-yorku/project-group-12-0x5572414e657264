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

