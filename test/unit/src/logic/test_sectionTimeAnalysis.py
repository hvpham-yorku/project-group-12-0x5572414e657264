"""
Unit tests for src.logic.sectionTimeAnalysis

All model_managers calls are mocked so that the tests exercise only
the computation logic — no database needed.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.database.models import Aisle, Customer, Path, Product
from src.logic.sectionTimeAnalysis import (
    CustomerSectionTime,
    SectionTimeSummary,
    _point_in_aisle,
    _get_section_index,
    get_section_time_analysis,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(seconds: int) -> datetime:
    """Return a datetime offset from a fixed base by *seconds*."""
    return datetime(2026, 1, 1, 12, 0, 0) + timedelta(seconds=seconds)


def _make_aisle(aisle_id, store_id=1, blx=0, bly=0, trx=100, try_=100, vertical=False):
    return Aisle(
        aisle_id=aisle_id, store_id=store_id,
        bottom_left_x=blx, bottom_left_y=bly,
        top_right_x=trx, top_right_y=try_,
        vertical=vertical,
    )


def _make_customer(customer_id, store_id=1):
    return Customer(customer_id=customer_id, store_id=store_id)


def _make_path(customer_id, x, y, ts):
    return Path(customer_id=customer_id, location_x=x, location_y=y, timestamp=ts)


def _make_product(product_id, aisle_id, order, store_id=1):
    return Product(
        product_id=product_id, store_id=store_id,
        aisle_id=aisle_id, name=f"P{product_id}", price=1.0, order=order,
    )


# ---------------------------------------------------------------------------
# _point_in_aisle
# ---------------------------------------------------------------------------

class TestPointInAisle(unittest.TestCase):

    def setUp(self):
        self.aisle = _make_aisle(1, blx=10, bly=20, trx=100, try_=200)

    def test_inside(self):
        self.assertTrue(_point_in_aisle(50, 100, self.aisle))

    def test_outside_left(self):
        self.assertFalse(_point_in_aisle(5, 100, self.aisle))

    def test_outside_right(self):
        self.assertFalse(_point_in_aisle(110, 100, self.aisle))

    def test_outside_below(self):
        self.assertFalse(_point_in_aisle(50, 10, self.aisle))

    def test_outside_above(self):
        self.assertFalse(_point_in_aisle(50, 210, self.aisle))

    def test_on_boundary_bottom_left(self):
        self.assertTrue(_point_in_aisle(10, 20, self.aisle))

    def test_on_boundary_top_right(self):
        self.assertTrue(_point_in_aisle(100, 200, self.aisle))

    def test_inverted_coordinates(self):
        inverted = Aisle(
            aisle_id=99, store_id=1,
            bottom_left_x=100, bottom_left_y=200,
            top_right_x=10, top_right_y=20,
        )
        self.assertTrue(_point_in_aisle(50, 100, inverted))
        self.assertFalse(_point_in_aisle(5, 100, inverted))


# ---------------------------------------------------------------------------
# _get_section_index
# ---------------------------------------------------------------------------

class TestGetSectionIndexHorizontal(unittest.TestCase):
    """Horizontal aisle: sections split along x-axis."""

    def setUp(self):
        self.aisle = _make_aisle(1, blx=0, bly=0, trx=70, try_=10, vertical=False)
        self.num_sections = 7  # section_width = 10

    def test_first_section(self):
        self.assertEqual(_get_section_index(5, 5, self.aisle, self.num_sections), 1)

    def test_middle_section(self):
        self.assertEqual(_get_section_index(35, 5, self.aisle, self.num_sections), 4)

    def test_last_section(self):
        self.assertEqual(_get_section_index(65, 5, self.aisle, self.num_sections), 7)

    def test_boundary_between_sections(self):
        # x=10 is start of section 2
        self.assertEqual(_get_section_index(10, 5, self.aisle, self.num_sections), 2)

    def test_right_edge_clamped(self):
        # x=70 is exactly on the far boundary → clamped to last section
        self.assertEqual(_get_section_index(70, 5, self.aisle, self.num_sections), 7)

    def test_left_edge(self):
        self.assertEqual(_get_section_index(0, 5, self.aisle, self.num_sections), 1)


class TestGetSectionIndexVertical(unittest.TestCase):
    """Vertical aisle: sections stacked along y-axis."""

    def setUp(self):
        self.aisle = _make_aisle(1, blx=0, bly=0, trx=10, try_=50, vertical=True)
        self.num_sections = 5  # section_height = 10

    def test_first_section(self):
        self.assertEqual(_get_section_index(5, 5, self.aisle, self.num_sections), 1)

    def test_middle_section(self):
        self.assertEqual(_get_section_index(5, 25, self.aisle, self.num_sections), 3)

    def test_last_section(self):
        self.assertEqual(_get_section_index(5, 45, self.aisle, self.num_sections), 5)

    def test_top_edge_clamped(self):
        self.assertEqual(_get_section_index(5, 50, self.aisle, self.num_sections), 5)

    def test_bottom_edge(self):
        self.assertEqual(_get_section_index(5, 0, self.aisle, self.num_sections), 1)


class TestGetSectionIndexZeroSpan(unittest.TestCase):

    def test_zero_width_horizontal(self):
        aisle = _make_aisle(1, blx=50, bly=0, trx=50, try_=100, vertical=False)
        self.assertEqual(_get_section_index(50, 50, aisle, 3), 1)

    def test_zero_height_vertical(self):
        aisle = _make_aisle(1, blx=0, bly=50, trx=100, try_=50, vertical=True)
        self.assertEqual(_get_section_index(50, 50, aisle, 3), 1)


# ---------------------------------------------------------------------------
# get_section_time_analysis
# ---------------------------------------------------------------------------

_MM = "src.logic.sectionTimeAnalysis.model_managers"


class TestNoAisles(unittest.TestCase):

    @patch(f"{_MM}.get_aisles_by_store", return_value=[])
    def test_returns_empty(self, _):
        self.assertEqual(get_section_time_analysis(store_id=1), [])


class TestNoProducts(unittest.TestCase):

    @patch(f"{_MM}.get_products_by_aisle", return_value=[])
    @patch(f"{_MM}.get_aisles_by_store")
    def test_returns_empty_when_aisles_have_no_products(self, mock_aisles, _):
        mock_aisles.return_value = [_make_aisle(1)]
        self.assertEqual(get_section_time_analysis(store_id=1), [])


class TestAllOrdersZero(unittest.TestCase):

    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_returns_empty_when_max_order_is_zero(self, mock_aisles, mock_prods):
        mock_aisles.return_value = [_make_aisle(1)]
        mock_prods.return_value = [_make_product(1, 1, order=0)]
        self.assertEqual(get_section_time_analysis(store_id=1), [])


class TestNoCustomers(unittest.TestCase):

    @patch(f"{_MM}.get_customers_by_store", return_value=[])
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_zero_summaries_for_all_sections(self, mock_aisles, mock_prods, _):
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=30, try_=10)]
        mock_prods.return_value = [_make_product(1, 1, order=3)]

        result = get_section_time_analysis(store_id=1)

        self.assertEqual(len(result), 3)
        for s in result:
            self.assertEqual(s.total_time_seconds, 0.0)
            self.assertEqual(s.average_time_seconds, 0.0)
            self.assertEqual(s.customer_count, 0)


class TestHorizontalAisleSections(unittest.TestCase):
    """Customer walks through sections 1 → 2 of a horizontal aisle."""

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_time_split_across_horizontal_sections(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        # Horizontal aisle, 70px wide, 7 sections → each 10px wide
        aisle = _make_aisle(1, blx=0, bly=0, trx=70, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=7)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 5, 5, _ts(0)),     # section 1
            _make_path(10, 5, 5, _ts(5)),     # section 1
            _make_path(10, 15, 5, _ts(10)),   # section 2
            _make_path(10, 25, 5, _ts(15)),   # section 3
        ]

        result = get_section_time_analysis(store_id=1)
        by_section = {s.section_index: s for s in result}

        self.assertEqual(len(result), 7)
        self.assertAlmostEqual(by_section[1].total_time_seconds, 10.0)
        self.assertAlmostEqual(by_section[2].total_time_seconds, 5.0)
        self.assertEqual(by_section[3].total_time_seconds, 0.0)
        for idx in range(4, 8):
            self.assertEqual(by_section[idx].total_time_seconds, 0.0)


class TestVerticalAisleSections(unittest.TestCase):
    """Customer walks through sections of a vertical aisle."""

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_time_split_across_vertical_sections(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        # Vertical aisle, 50px tall, 5 sections → each 10px tall
        aisle = _make_aisle(1, blx=0, bly=0, trx=10, try_=50, vertical=True)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=5)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 5, 5, _ts(0)),    # section 1
            _make_path(10, 5, 15, _ts(10)),  # section 2
            _make_path(10, 5, 25, _ts(20)),  # section 3
        ]

        result = get_section_time_analysis(store_id=1)
        by_section = {s.section_index: s for s in result}

        self.assertEqual(len(result), 5)
        self.assertAlmostEqual(by_section[1].total_time_seconds, 10.0)
        self.assertAlmostEqual(by_section[2].total_time_seconds, 10.0)
        for idx in range(3, 6):
            self.assertEqual(by_section[idx].total_time_seconds, 0.0)


class TestMultipleCustomersAverage(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_average_across_customers(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=30, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=3)]
        mock_custs.return_value = [_make_customer(10), _make_customer(20)]

        def paths_side_effect(cid):
            if cid == 10:
                return [
                    _make_path(10, 5, 5, _ts(0)),   # section 1
                    _make_path(10, 5, 5, _ts(10)),   # section 1
                ]
            return [
                _make_path(20, 5, 5, _ts(0)),   # section 1
                _make_path(20, 5, 5, _ts(20)),   # section 1
            ]

        mock_paths.side_effect = paths_side_effect

        result = get_section_time_analysis(store_id=1)
        by_section = {s.section_index: s for s in result}

        section1 = by_section[1]
        self.assertAlmostEqual(section1.total_time_seconds, 30.0)
        self.assertAlmostEqual(section1.average_time_seconds, 15.0)
        self.assertEqual(section1.customer_count, 2)


class TestCustomerOutsideAllAisles(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_no_time_when_outside(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=30, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=3)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 200, 200, _ts(0)),
            _make_path(10, 200, 200, _ts(10)),
        ]

        result = get_section_time_analysis(store_id=1)

        for s in result:
            self.assertEqual(s.total_time_seconds, 0.0)
            self.assertEqual(s.customer_count, 0)


class TestSinglePathPointSkipped(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_customer_with_one_point_is_skipped(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=20, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=2)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [_make_path(10, 5, 5, _ts(0))]

        result = get_section_time_analysis(store_id=1)

        for s in result:
            self.assertEqual(s.total_time_seconds, 0.0)


class TestNoneTimestampsFiltered(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_none_timestamps_are_filtered(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=30, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=3)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 5, 5, None),
            _make_path(10, 5, 5, _ts(0)),
            _make_path(10, 5, 5, None),
            _make_path(10, 5, 5, _ts(10)),
        ]

        result = get_section_time_analysis(store_id=1)
        by_section = {s.section_index: s for s in result}

        self.assertAlmostEqual(by_section[1].total_time_seconds, 10.0)


class TestUnsortedPaths(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_paths_sorted_before_analysis(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=30, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=3)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 5, 5, _ts(20)),
            _make_path(10, 5, 5, _ts(0)),
            _make_path(10, 5, 5, _ts(10)),
        ]

        result = get_section_time_analysis(store_id=1)
        by_section = {s.section_index: s for s in result}

        self.assertAlmostEqual(by_section[1].total_time_seconds, 20.0)


class TestTransitionFromAisleToOutside(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_transition_attributed_to_section(
        self, mock_aisles, mock_prods, mock_custs, mock_paths,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=20, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [_make_product(1, 1, order=2)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 5, 5, _ts(0)),      # section 1 (inside)
            _make_path(10, 5, 5, _ts(5)),      # section 1 (inside)
            _make_path(10, 200, 200, _ts(10)), # outside
            _make_path(10, 200, 200, _ts(20)), # outside
        ]

        result = get_section_time_analysis(store_id=1)
        by_section = {s.section_index: s for s in result}

        # t=0→5 (5s) + t=5→10 (5s) both in section 1 = 10s
        self.assertAlmostEqual(by_section[1].total_time_seconds, 10.0)
        self.assertEqual(by_section[2].total_time_seconds, 0.0)


class TestMaxOrderDeterminesSections(unittest.TestCase):
    """Multiple products with different orders; max determines section count."""

    @patch(f"{_MM}.get_customers_by_store", return_value=[])
    @patch(f"{_MM}.get_products_by_aisle")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_section_count_equals_max_order(
        self, mock_aisles, mock_prods, _,
    ):
        aisle = _make_aisle(1, blx=0, bly=0, trx=50, try_=10, vertical=False)
        mock_aisles.return_value = [aisle]
        mock_prods.return_value = [
            _make_product(1, 1, order=2),
            _make_product(2, 1, order=5),
            _make_product(3, 1, order=3),
        ]

        result = get_section_time_analysis(store_id=1)

        self.assertEqual(len(result), 5)
        section_indices = [s.section_index for s in result]
        self.assertEqual(section_indices, [1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
