"""
Unit tests for src.logic.aisleTimeAnalysis

All model_managers calls are mocked so that the tests exercise only
the computation logic — no database needed.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.database.models import Aisle, Customer, Path
from src.logic.aisleTimeAnalysis import (
    CustomerAisleTime,
    AisleTimeSummary,
    _point_in_aisle,
    get_aisle_time_analysis,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(seconds: int) -> datetime:
    """Return a datetime offset from a fixed base by *seconds*."""
    return datetime(2026, 1, 1, 12, 0, 0) + timedelta(seconds=seconds)


def _make_aisle(aisle_id, store_id=1, blx=0, bly=0, trx=100, try_=100):
    return Aisle(
        aisle_id=aisle_id, store_id=store_id,
        bottom_left_x=blx, bottom_left_y=bly,
        top_right_x=trx, top_right_y=try_,
    )


def _make_customer(customer_id, store_id=1):
    return Customer(customer_id=customer_id, store_id=store_id)


def _make_path(customer_id, x, y, ts):
    return Path(customer_id=customer_id, location_x=x, location_y=y, timestamp=ts)


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

    def test_on_left_edge(self):
        self.assertTrue(_point_in_aisle(10, 100, self.aisle))

    def test_on_right_edge(self):
        self.assertTrue(_point_in_aisle(100, 100, self.aisle))

    def test_inverted_coordinates(self):
        """bottom_left values larger than top_right — still works via min/max."""
        inverted = Aisle(
            aisle_id=99, store_id=1,
            bottom_left_x=100, bottom_left_y=200,
            top_right_x=10, top_right_y=20,
        )
        self.assertTrue(_point_in_aisle(50, 100, inverted))
        self.assertFalse(_point_in_aisle(5, 100, inverted))


# ---------------------------------------------------------------------------
# get_aisle_time_analysis
# ---------------------------------------------------------------------------

_MM = "src.logic.aisleTimeAnalysis.model_managers"


class TestGetAisleTimeAnalysisNoAisles(unittest.TestCase):

    @patch(f"{_MM}.get_aisles_by_store", return_value=[])
    def test_returns_empty_when_no_aisles(self, _mock_aisles):
        result = get_aisle_time_analysis(store_id=1)
        self.assertEqual(result, [])


class TestGetAisleTimeAnalysisNoCustomers(unittest.TestCase):

    @patch(f"{_MM}.get_customers_by_store", return_value=[])
    @patch(f"{_MM}.get_aisles_by_store")
    def test_returns_zero_summaries_when_no_customers(self, mock_aisles, _mock_cust):
        mock_aisles.return_value = [_make_aisle(1)]
        result = get_aisle_time_analysis(store_id=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].aisle_id, 1)
        self.assertEqual(result[0].total_time_seconds, 0.0)
        self.assertEqual(result[0].average_time_seconds, 0.0)
        self.assertEqual(result[0].customer_count, 0)
        self.assertEqual(result[0].customer_times, [])


class TestGetAisleTimeAnalysisSingleCustomerSingleAisle(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_total_and_average_for_one_customer(self, mock_aisles, mock_custs, mock_paths):
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=100, try_=100)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 50, 50, _ts(0)),
            _make_path(10, 50, 50, _ts(10)),
            _make_path(10, 50, 50, _ts(20)),
        ]

        result = get_aisle_time_analysis(store_id=1)

        self.assertEqual(len(result), 1)
        summary = result[0]
        self.assertEqual(summary.aisle_id, 1)
        self.assertAlmostEqual(summary.total_time_seconds, 20.0)
        self.assertAlmostEqual(summary.average_time_seconds, 20.0)
        self.assertEqual(summary.customer_count, 1)
        self.assertEqual(len(summary.customer_times), 1)
        self.assertEqual(summary.customer_times[0].customer_id, 10)
        self.assertAlmostEqual(summary.customer_times[0].total_time_seconds, 20.0)


class TestGetAisleTimeAnalysisCustomerMovesBetweenAisles(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_time_split_across_aisles(self, mock_aisles, mock_custs, mock_paths):
        """Customer spends 10s in aisle A then 5s in aisle B."""
        aisle_a = _make_aisle(1, blx=0, bly=0, trx=100, try_=100)
        aisle_b = _make_aisle(2, blx=200, bly=0, trx=300, try_=100)
        mock_aisles.return_value = [aisle_a, aisle_b]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 50, 50, _ts(0)),    # in A
            _make_path(10, 50, 50, _ts(5)),    # in A
            _make_path(10, 250, 50, _ts(10)),  # in B
            _make_path(10, 250, 50, _ts(15)),  # in B
        ]

        result = get_aisle_time_analysis(store_id=1)
        by_aisle = {s.aisle_id: s for s in result}

        self.assertAlmostEqual(by_aisle[1].total_time_seconds, 10.0)
        self.assertAlmostEqual(by_aisle[2].total_time_seconds, 5.0)


class TestGetAisleTimeAnalysisCustomerOutsideAllAisles(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_no_time_when_outside(self, mock_aisles, mock_custs, mock_paths):
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=100, try_=100)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 200, 200, _ts(0)),
            _make_path(10, 200, 200, _ts(10)),
        ]

        result = get_aisle_time_analysis(store_id=1)

        self.assertEqual(result[0].total_time_seconds, 0.0)
        self.assertEqual(result[0].customer_count, 0)


class TestGetAisleTimeAnalysisMultipleCustomers(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_aggregate_across_customers(self, mock_aisles, mock_custs, mock_paths):
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=100, try_=100)]
        mock_custs.return_value = [_make_customer(10), _make_customer(20)]

        def paths_side_effect(cid):
            if cid == 10:
                return [
                    _make_path(10, 50, 50, _ts(0)),
                    _make_path(10, 50, 50, _ts(10)),
                ]
            return [
                _make_path(20, 50, 50, _ts(0)),
                _make_path(20, 50, 50, _ts(20)),
            ]

        mock_paths.side_effect = paths_side_effect

        result = get_aisle_time_analysis(store_id=1)

        summary = result[0]
        self.assertAlmostEqual(summary.total_time_seconds, 30.0)
        self.assertAlmostEqual(summary.average_time_seconds, 15.0)
        self.assertEqual(summary.customer_count, 2)


class TestGetAisleTimeAnalysisSinglePathPoint(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_customer_with_one_point_is_skipped(self, mock_aisles, mock_custs, mock_paths):
        mock_aisles.return_value = [_make_aisle(1)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [_make_path(10, 50, 50, _ts(0))]

        result = get_aisle_time_analysis(store_id=1)

        self.assertEqual(result[0].total_time_seconds, 0.0)
        self.assertEqual(result[0].customer_count, 0)


class TestGetAisleTimeAnalysisNoneTimestamps(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_none_timestamps_are_filtered(self, mock_aisles, mock_custs, mock_paths):
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=100, try_=100)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 50, 50, None),
            _make_path(10, 50, 50, _ts(0)),
            _make_path(10, 50, 50, None),
            _make_path(10, 50, 50, _ts(10)),
        ]

        result = get_aisle_time_analysis(store_id=1)

        self.assertAlmostEqual(result[0].total_time_seconds, 10.0)
        self.assertEqual(result[0].customer_count, 1)


class TestGetAisleTimeAnalysisUnsortedPaths(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_paths_are_sorted_by_timestamp(self, mock_aisles, mock_custs, mock_paths):
        """Paths returned out of order should still produce correct results."""
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=100, try_=100)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 50, 50, _ts(20)),
            _make_path(10, 50, 50, _ts(0)),
            _make_path(10, 50, 50, _ts(10)),
        ]

        result = get_aisle_time_analysis(store_id=1)

        self.assertAlmostEqual(result[0].total_time_seconds, 20.0)


class TestGetAisleTimeAnalysisMultipleAislesNoOverlap(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_unvisited_aisle_has_zero_totals(self, mock_aisles, mock_custs, mock_paths):
        """Aisle 2 exists but no customer visits it."""
        aisle_a = _make_aisle(1, blx=0, bly=0, trx=100, try_=100)
        aisle_b = _make_aisle(2, blx=200, bly=200, trx=300, try_=300)
        mock_aisles.return_value = [aisle_a, aisle_b]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 50, 50, _ts(0)),
            _make_path(10, 50, 50, _ts(10)),
        ]

        result = get_aisle_time_analysis(store_id=1)
        by_aisle = {s.aisle_id: s for s in result}

        self.assertAlmostEqual(by_aisle[1].total_time_seconds, 10.0)
        self.assertEqual(by_aisle[1].customer_count, 1)
        self.assertEqual(by_aisle[2].total_time_seconds, 0.0)
        self.assertEqual(by_aisle[2].customer_count, 0)
        self.assertEqual(by_aisle[2].customer_times, [])


class TestGetAisleTimeAnalysisTransitionInterval(unittest.TestCase):

    @patch(f"{_MM}.get_paths_by_customer")
    @patch(f"{_MM}.get_customers_by_store")
    @patch(f"{_MM}.get_aisles_by_store")
    def test_transition_from_aisle_to_outside(self, mock_aisles, mock_custs, mock_paths):
        """Left-Riemann: time between last in-aisle point and first outside
        point is still attributed to the aisle."""
        mock_aisles.return_value = [_make_aisle(1, blx=0, bly=0, trx=100, try_=100)]
        mock_custs.return_value = [_make_customer(10)]
        mock_paths.return_value = [
            _make_path(10, 50, 50, _ts(0)),    # inside
            _make_path(10, 50, 50, _ts(5)),    # inside
            _make_path(10, 200, 200, _ts(10)), # outside
            _make_path(10, 200, 200, _ts(20)), # outside
        ]

        result = get_aisle_time_analysis(store_id=1)

        # t=0→5 (5s, in aisle) + t=5→10 (5s, in aisle) = 10s
        # t=10→20 is outside, contributes 0
        self.assertAlmostEqual(result[0].total_time_seconds, 10.0)


if __name__ == "__main__":
    unittest.main()
