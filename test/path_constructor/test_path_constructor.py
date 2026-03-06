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
            make_point(customer_id, 25, 30, start + timedelta(seconds=16)),
        ]

        mock_get_points.return_value = points
        path = construct_path(customer_id)
        expected = [[1,2], [8,20], [12,5], [25,30]]
        self.assertEqual(path, expected)



    #test for multiple customers
    @patch("src.path_constructor.get_customer_path_points")
    def test_multiple_customers(self, mock_get_points):
        start=datetime.now()
        #mixed customer data( 200 and 201)
        points = [
            make_point(200, 2, 3, start),
            make_point(201, 50, 40, start + timedelta(seconds=3)),
            make_point(200, 5, 6, start + timedelta(seconds=5)),
            make_point(201, 52, 44, start + timedelta(seconds=9)),
        ]

        mock_get_points.return_value = [p for p in points if p.customer_id == 201]
        path=construct_path(201)
        expected = [[50,40], [52,44]]
        self.assertEqual(path, expected)

    #test for duplicate coordinates
    @patch("src.path_constructor.get_customer_path_points")
    def tets_duplicate_coordinates(self, mock_get_points):
        customer_id = 300
        start = datetime.now()

        points = [
            make_point(customer_id, 10, 10, start),
            make_point(customer_id, 15, 18, start + timedelta(seconds=5)),
            make_point(customer_id, 10, 10, start + timedelta(seconds=10)),
            make_point(customer_id, 10, 10, start + timedelta(seconds=15)),
        ]

        mock_get_points.return_value = points
        path = construct_path(customer_id)
        expected = [ [10,10], [15,18], [10,10], [10,10]]
        self.assertEqual(path, expected)

    #test for negative coordinates(not allowed)
    @patch("src.path_constructor.get_customer_path_points")
    def test_negative_coordinates(self, mock_get_points):
        customer_id = 401
        start = datetime.now()

        points = [
            make_point(customer_id, -5, 3, start),
            make_point(customer_id, 4, 8, start + timedelta(seconds=5)),
        ]
        mock_get_points.return_value = points
        with self.assertRaises(ValueError):
            construct_path(customer_id)

    #test for duplicate timestamps with different path points for one customer
    @patch("src.path_constructor.get_customer_path_points")
    def test_duplicate_timestamps(self, mock_get_points):
        customer_id = 402
        start = datetime.now()
        points = [
            make_point(customer_id, 1, 2, start),
            make_point(customer_id, 5, 6, start),
        ]
        mock_get_points.return_value = points
        with self.assertRaises(ValueError):
            construct_path(customer_id)

    @patch("src.path_constructor.get_customer_path_points")
    def test_duplicate_timestamps_2(self, mock_get_points):
        customer_id = 403
        start = datetime.now()
        points = [
            make_point(customer_id, 1, 2, start),
            make_point(customer_id, 1, 2, start),
        ]
        mock_get_points.return_value = points
        with self.assertRaises(ValueError):
            construct_path(customer_id)


if __name__ == '__main__':
    unittest.main()
