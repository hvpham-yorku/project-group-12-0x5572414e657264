import importlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

# python -m test.test_logic.test_customerProductAnalytics


class TestCustomerAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Import the analytics module once for the whole test class.

        If the module was already imported earlier in the session,
        remove it first so we get a fresh import.
        """
        if "src.logic.customerAnalytics" in sys.modules:
            del sys.modules["src.logic.customerAnalytics"]


        cls.ca = importlib.import_module("src.logic.customerAnalytics")

    def setUp(self):
        """
        Patch all table select() calls before every test.

        This prevents the tests from touching the real database.
        Instead, each test provides fake rows through the mocked
        select() return values.
        """
        self.patcher_product_select = patch.object(self.ca.ProductTable, "select")
        self.mock_product_select = self.patcher_product_select.start()
        self.addCleanup(self.patcher_product_select.stop)

        self.patcher_purchase_select = patch.object(self.ca.PurchaseTable, "select")
        self.mock_purchase_select = self.patcher_purchase_select.start()
        self.addCleanup(self.patcher_purchase_select.stop)

        self.patcher_checkout_select = patch.object(self.ca.CheckoutTable, "select")
        self.mock_checkout_select = self.patcher_checkout_select.start()
        self.addCleanup(self.patcher_checkout_select.stop)

        self.patcher_customer_select = patch.object(self.ca.CustomerTable, "select")
        self.mock_customer_select = self.patcher_customer_select.start()
        self.addCleanup(self.patcher_customer_select.stop)

    def test_get_product_most_common_gender(self):
        """
        Test that the function correctly returns the most common gender
        for each product.
        """
        # Fake products
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk"),
            SimpleNamespace(product_id=2, name="Bread"),
        ]

        # Fake checkouts linking checkout_id -> customer_id
        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=10, customer_id=100),
            SimpleNamespace(checkout_id=11, customer_id=101),
            SimpleNamespace(checkout_id=12, customer_id=102),
            SimpleNamespace(checkout_id=13, customer_id=103),
        ]

        # Fake customers storing sex values
        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=101, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=102, sex="Male", age="48-53"),
            SimpleNamespace(customer_id=103, sex="Male", age="48-53"),
        ]

        # Fake purchases linking products to checkouts
        self.mock_purchase_select.return_value = [
            SimpleNamespace(purchase_id=1000, product_id=1, checkout_id=10, quantity=1),
            SimpleNamespace(purchase_id=1001, product_id=1, checkout_id=11, quantity=1),
            SimpleNamespace(purchase_id=1002, product_id=1, checkout_id=12, quantity=1),
            SimpleNamespace(purchase_id=1003, product_id=2, checkout_id=12, quantity=1),
            SimpleNamespace(purchase_id=1004, product_id=2, checkout_id=13, quantity=1),
        ]

        result = self.ca.get_product_most_common_gender()

        expected = {
            "Milk": "Female",
            "Bread": "Male",
        }

        self.assertEqual(result, expected)

    def test_get_product_most_common_gender_skips_empty_gender(self):
        """
        Test that customers with empty gender values are ignored.
        """
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk"),
        ]

        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=10, customer_id=100),
            SimpleNamespace(checkout_id=11, customer_id=101),
        ]

        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="", age="25-32"),
            SimpleNamespace(customer_id=101, sex="Female", age="25-32"),
        ]

        self.mock_purchase_select.return_value = [
            SimpleNamespace(purchase_id=1000, product_id=1, checkout_id=10, quantity=1),
            SimpleNamespace(purchase_id=1001, product_id=1, checkout_id=11, quantity=1),
        ]

        result = self.ca.get_product_most_common_gender()

        expected = {
            "Milk": "Female",
        }

        self.assertEqual(result, expected)

    def test_get_product_most_common_gender_returns_empty_dict_when_no_purchases(self):
        """
        Test that no purchases leads to an empty result dictionary.
        """
        self.mock_product_select.return_value = []
        self.mock_checkout_select.return_value = []
        self.mock_customer_select.return_value = []
        self.mock_purchase_select.return_value = []

        result = self.ca.get_product_most_common_gender()

        self.assertEqual(result, {})

    def test_get_product_most_common_gender_skips_missing_checkout(self):
        """
        Test that a purchase is ignored if its checkout_id does not
        exist in the checkout table.
        """
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk"),
        ]

        # No matching checkout for checkout_id=999
        self.mock_checkout_select.return_value = []

        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="Female", age="25-32"),
        ]

        self.mock_purchase_select.return_value = [
            SimpleNamespace(purchase_id=1000, product_id=1, checkout_id=999, quantity=1),
        ]

        result = self.ca.get_product_most_common_gender()

        self.assertEqual(result, {})

    def test_get_product_most_common_age(self):
        """
        Test that the function correctly returns the most common age group
        for each product.
        """
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk"),
            SimpleNamespace(product_id=2, name="Bread"),
        ]

        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=20, customer_id=200),
            SimpleNamespace(checkout_id=21, customer_id=201),
            SimpleNamespace(checkout_id=22, customer_id=202),
            SimpleNamespace(checkout_id=23, customer_id=203),
        ]

        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=200, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=201, sex="Male", age="25-32"),
            SimpleNamespace(customer_id=202, sex="Male", age="48-53"),
            SimpleNamespace(customer_id=203, sex="Male", age="48-53"),
        ]

        self.mock_purchase_select.return_value = [
            SimpleNamespace(purchase_id=2000, product_id=1, checkout_id=20, quantity=1),
            SimpleNamespace(purchase_id=2001, product_id=1, checkout_id=21, quantity=1),
            SimpleNamespace(purchase_id=2002, product_id=1, checkout_id=22, quantity=1),
            SimpleNamespace(purchase_id=2003, product_id=2, checkout_id=22, quantity=1),
            SimpleNamespace(purchase_id=2004, product_id=2, checkout_id=23, quantity=1),
        ]

        result = self.ca.get_product_most_common_age()

        expected = {
            "Milk": "25-32",
            "Bread": "48-53",
        }

        self.assertEqual(result, expected)

    def test_get_product_most_common_age_skips_empty_age(self):
        """
        Test that customers with empty age values are ignored.
        """
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk"),
        ]

        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=20, customer_id=200),
            SimpleNamespace(checkout_id=21, customer_id=201),
        ]

        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=200, sex="Female", age=""),
            SimpleNamespace(customer_id=201, sex="Male", age="48-53"),
        ]

        self.mock_purchase_select.return_value = [
            SimpleNamespace(purchase_id=2000, product_id=1, checkout_id=20, quantity=1),
            SimpleNamespace(purchase_id=2001, product_id=1, checkout_id=21, quantity=1),
        ]

        result = self.ca.get_product_most_common_age()

        expected = {
            "Milk": "48-53",
        }

        self.assertEqual(result, expected)

    def test_get_product_most_common_age_returns_empty_dict_when_no_purchases(self):
        """
        Test that no purchases leads to an empty age result dictionary.
        """
        self.mock_product_select.return_value = []
        self.mock_checkout_select.return_value = []
        self.mock_customer_select.return_value = []
        self.mock_purchase_select.return_value = []

        result = self.ca.get_product_most_common_age()

        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()