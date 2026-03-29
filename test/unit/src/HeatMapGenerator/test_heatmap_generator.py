from datetime import datetime
import os
import tempfile
import unittest

from src.HeatMapGenerator import heatmap_generator
from src.database.models import Aisle, Path, Store


class HeatmapGeneratorTestCase(unittest.TestCase):
    def test_render_custom_heatmap_rgba_reports_monotonic_progress(self):
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
        progress_updates: list[float] = []

        heatmap_generator.render_custom_heatmap_rgba(
            paths,
            aisles,
            store,
            start_hour=9,
            end_hour=11,
            width=320,
            height=180,
            progress_callback=lambda progress, status: progress_updates.append(progress),
        )

        self.assertGreater(len(progress_updates), 0)
        self.assertEqual(progress_updates[-1], 1.0)
        self.assertTrue(
            all(
                earlier <= later
                for earlier, later in zip(progress_updates, progress_updates[1:])
            )
        )

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

    def test_render_heatmap_video_writes_minute_by_minute_video(self):
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
            Path(location_x=2, location_y=3, timestamp=datetime(2026, 1, 1, 9, 1, 0)),
            Path(location_x=12, location_y=5, timestamp=datetime(2026, 1, 1, 9, 2, 0)),
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "heatmap_evolution.mp4")
            result = heatmap_generator.render_heatmap_video(
                paths,
                aisles,
                store,
                start_hour=9,
                end_hour=10,
                output_path=output_path,
                width=160,
                height=90,
                fps=6,
                minute_step=15,
                persistence_frames=3,
            )

            self.assertTrue(os.path.exists(result.output_path))
            self.assertGreater(result.num_frames, 0)
            self.assertEqual(result.filtered_paths, 3)
            self.assertEqual(result.persistence_frames, 3)

    def test_render_heatmap_video_reports_monotonic_progress(self):
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
            Path(location_x=2, location_y=3, timestamp=datetime(2026, 1, 1, 9, 1, 0)),
            Path(location_x=12, location_y=5, timestamp=datetime(2026, 1, 1, 9, 2, 0)),
        ]
        progress_updates: list[float] = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "heatmap_evolution.mp4")
            heatmap_generator.render_heatmap_video(
                paths,
                aisles,
                store,
                start_hour=9,
                end_hour=10,
                output_path=output_path,
                width=160,
                height=90,
                fps=6,
                minute_step=15,
                persistence_frames=3,
                progress_callback=lambda progress, status: progress_updates.append(progress),
            )

        self.assertGreater(len(progress_updates), 0)
        self.assertEqual(progress_updates[-1], 1.0)
        self.assertTrue(
            all(
                earlier <= later
                for earlier, later in zip(progress_updates, progress_updates[1:])
            )
        )


if __name__ == "__main__":
    unittest.main()
