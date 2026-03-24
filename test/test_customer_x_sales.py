import unittest
from datetime import datetime
from src.customer_x_sales import customer_conversion_function

class MockCustomer:
    def __init__(self, entered_at, exited_at):
        self.entered_at = entered_at
        self.exited_at = exited_at

class MockCheckout:
    def __init__(self, created_at, total_price):
        self.created_at = created_at
        self.total_price = total_price

class TestCustomerConversion(unittest.TestCase):

    # ✅ Test 1: Basic functionality
    def test_basic_case(self):
        customers = [
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
        ]

        checkouts = [
            MockCheckout(datetime(2026, 1, 1, 10), 20.0),
        ]

        result = customer_conversion_function(customers, checkouts)

        self.assertEqual(result["hours"], [10])
        self.assertEqual(result["customers"], [2])
        self.assertEqual(result["checkouts"], [1])
        self.assertEqual(result["sales"], [20.0])
        self.assertAlmostEqual(result["conversion_rates"][0], 0.5)

    # ✅ Test 2: Multiple hours
    def test_multiple_hours(self):
        customers = [
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
            MockCustomer(datetime(2026, 1, 1, 11), datetime(2026, 1, 1, 11)),
        ]

        checkouts = [
            MockCheckout(datetime(2026, 1, 1, 10), 10.0),
            MockCheckout(datetime(2026, 1, 1, 11), 30.0),
        ]

        result = customer_conversion_function(customers, checkouts)

        self.assertEqual(result["hours"], [10, 11])
        self.assertEqual(result["customers"], [1, 1])
        self.assertEqual(result["checkouts"], [1, 1])
        self.assertEqual(result["sales"], [10.0, 30.0])
        self.assertEqual(result["conversion_rates"], [1.0, 1.0])

    # ✅ Test 3: No checkouts
    def test_no_checkouts(self):
        customers = [
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
        ]

        checkouts = []

        result = customer_conversion_function(customers, checkouts)

        self.assertEqual(result["customers"], [1])
        self.assertEqual(result["checkouts"], [0])
        self.assertEqual(result["sales"], [0.0])
        self.assertEqual(result["conversion_rates"], [0.0])

    # ✅ Test 4: No customers
    def test_no_customers(self):
        customers = []
        checkouts = [
            MockCheckout(datetime(2026, 1, 1, 10), 50.0),
        ]

        result = customer_conversion_function(customers, checkouts)

        self.assertEqual(result["hours"], [])
        self.assertEqual(result["customers"], [])
        self.assertEqual(result["checkouts"], [])
        self.assertEqual(result["sales"], [])
        self.assertEqual(result["conversion_rates"], [])

    # ✅ Test 5: Zero division protection
    def test_zero_customers_in_hour(self):
        customers = [
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
        ]

        checkouts = [
            MockCheckout(datetime(2026, 1, 1, 11), 20.0),
        ]

        result = customer_conversion_function(customers, checkouts)

        # Only hour 10 should appear (since customers define hours)
        self.assertEqual(result["hours"], [10])
        self.assertEqual(result["conversion_rates"], [0.0])

    # ✅ Test 6: Sales aggregation
    def test_sales_sum(self):
        customers = [
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
            MockCustomer(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 10)),
        ]

        checkouts = [
            MockCheckout(datetime(2026, 1, 1, 10), 10.0),
            MockCheckout(datetime(2026, 1, 1, 10), 15.0),
        ]

        result = customer_conversion_function(customers, checkouts)

        self.assertEqual(result["sales"], [25.0])


if __name__ == '__main__':
    unittest.main()
