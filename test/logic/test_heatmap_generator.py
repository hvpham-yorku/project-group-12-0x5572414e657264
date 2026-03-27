from datetime import datetime
import unittest

from src.HeatMapGenerator import heatmap_generator
from src.database.models import Aisle, Path, Store


class HeatmapGeneratorTestCase(unittest.TestCase):
    def test_render_custom_heatmap_rgba_returns_rgba_image(self):
        store = Store(store_id=1, name="Store A", width=18, height=10)
        aisles = [
            Aisle(
                aisle_id=1,
                store_id=store.store_id,
                bottom_left_x=6,
                bottom_left_y=1,
                top_right_x=9,
                top_right_y=8,
                vertical=True,
            )
        ]
        paths = [
            Path(location_x=2, location_y=3, timestamp=datetime(2026, 1, 1, 9, 0, 0)),
            Path(location_x=2, location_y=3, timestamp=datetime(2026, 1, 1, 9, 15, 0)),
            Path(location_x=12, location_y=5, timestamp=datetime(2026, 1, 1, 10, 30, 0)),
        ]

        image = heatmap_generator.render_custom_heatmap_rgba(
            paths,
            aisles,
            store,
            start_hour=9,
            end_hour=11,
            width=320,
            height=180,
        )

        self.assertEqual(image.shape, (180, 320, 4))
        self.assertGreater(int(image[:, :, 3].max()), 0)


if __name__ == "__main__":
    unittest.main()
