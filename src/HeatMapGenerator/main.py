import random

from heatmap_generator import generate_custom_heatmap, generate_time_range_heatmaps

def main():
    # -----------------------------------
    # MOCK DATA (replace with DB later)
    # -----------------------------------
    from datetime import datetime
    from src.database.models import Path, Aisle

    # Example paths (simulate customer movement)
    paths = [
        Path(
            location_x=random.randint(0, 30),
            location_y=random.randint(0, 20),
            timestamp=datetime(2026, 3, 25, random.randint(7, 22))
        )
        for _ in range(500)
    ]

    # Example aisles (rectangles)
    aisles = [
        Aisle(bottom_left_x=3, bottom_left_y=0, top_right_x=8, top_right_y=20),
        Aisle(bottom_left_x=12, bottom_left_y=0, top_right_x=17, top_right_y=20),
        Aisle(bottom_left_x=21, bottom_left_y=0, top_right_x=26, top_right_y=20),
    ]

    # -----------------------------------
    # RUN HEATMAPS
    # -----------------------------------

    # Single custom time range
    generate_custom_heatmap(paths, aisles, 7, 12)

    # OR: multiple time ranges
    generate_time_range_heatmaps(paths, aisles)


# -----------------------------------
# ENTRY POINT
# -----------------------------------
if __name__ == "__main__":
    main()