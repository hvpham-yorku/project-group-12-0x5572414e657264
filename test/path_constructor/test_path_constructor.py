import unittest
from unittest.mock import patch
from types import SimpleNamespace
from datetime import datetime, timedelta

from src.path_constructor import construct_path

#Helper function to simulate database PathTable rows
def make_point(customer_id, x, y, timestamp):
    return SimpleNamespace(
        customer_id=customer_id,
        location_x=x,
        location_y=y,
        timestamp=timestamp
    )


class PathTestCase(unittest.TestCase):
    pass

class TestPathConstructor(PathTestCase):

    #test constructing a normal ordered path
    @patch("src.path_constructor.get_customer_path_points")
    def test_normal_path(self, mock_get_points):
        customer_id = 101
        start = datetime.now()

        points = [
            make_point(customer_id, 2, 4, start),
            make_point(customer_id, 5, 8, start + timedelta(seconds=5)),
            make_point(customer_id, 9, 15, start + timedelta(seconds=12)),
        ]
        mock_get_points.return_value = points
        path = construct_path(customer_id)
        expected = [[2, 4], [5, 8], [9, 15]]
        self.assertEqual(path, expected)


    #test unsorted timestamps
    @patch("src.path_constructor.get_customer_path_points")
    def test_unsorted_timestamps(self, mock_get_points):
        customer_id = 102
        start = datetime.now()
        points = [
            make_point(customer_id, 10, 12, start + timedelta(seconds=15)),
            make_point(customer_id, 2, 4, start),
            make_point(customer_id, 6, 9, start + timedelta(seconds=7)),
        ]

        mock_get_points.return_value = points
        path = construct_path(customer_id)
        expected = [[2, 4], [6, 9], [10, 12]]
        self.assertEqual(path, expected)


    #test single path point
    @patch("src.path_constructor.get_customer_path_points")
    def test_single_point(self, mock_get_points):
        customer_id = 103
        start = datetime.now()
        points = [
            make_point(customer_id, 2, 7, start),
        ]

        mock_get_points.return_value = points
        path = construct_path(customer_id)
        expected = [[2, 7]]
        self.assertEqual(path, expected)


    #test empty path
    @patch("src.path_constructor.get_customer_path_points")
    def test_empty_path(self, mock_get_points):
        customer_id = 104
        start = datetime.now()

        mock_get_points.return_value = []
        path = construct_path(customer_id)
        expected = []
        self.assertEqual(path, expected)


    #test irregular movement
    @patch("src.path_constructor.get_customer_path_points")
    def test_irregular_movement(self, mock_get_points):
        customer_id = 105
        start = datetime.now()

        points = [
            make_point(customer_id, 1, 2, start),
            make_point(customer_id, 8, 20, start + timedelta(seconds=6)),
            make_point(customer_id, 12, 5, start + timedelta(seconds=11)),
            make_point(customer_id, 25, 30, start + timedelta(seconds=16)), ]


if __name__ == '__main__':
    unittest.main()
