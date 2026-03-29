import importlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

# python -m test.unit.src.logic.test_customerAisleAnalytics



class TestCustomerAisleAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "src.logic.customerAisleAnalytics" in sys.modules:
            del sys.modules["src.logic.customerAisleAnalytics"]
        cls.caa = importlib.import_module("src.logic.customerAisleAnalytics")

    def setUp(self):
        self.patcher_product = patch.object(self.caa.ProductTable, "select")
        self.mock_product_select = self.patcher_product.start()
        self.addCleanup(self.patcher_product.stop)

        self.patcher_checkout = patch.object(self.caa.CheckoutTable, "select")
        self.mock_checkout_select = self.patcher_checkout.start()
        self.addCleanup(self.patcher_checkout.stop)

        self.patcher_customer = patch.object(self.caa.CustomerTable, "select")
        self.mock_customer_select = self.patcher_customer.start()
        self.addCleanup(self.patcher_customer.stop)

        self.patcher_purchase = patch.object(self.caa.PurchaseTable, "select")
        self.mock_purchase_select = self.patcher_purchase.start()
        self.addCleanup(self.patcher_purchase.stop)

    # ------------------------------------------------------------------ gender

    def test_get_product_category_most_common_gender(self):
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk",   aisle_id=10),
            SimpleNamespace(product_id=2, name="Bread",  aisle_id=10),
            SimpleNamespace(product_id=3, name="Apples", aisle_id=20),
        ]
        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=10, customer_id=100),
            SimpleNamespace(checkout_id=11, customer_id=101),
            SimpleNamespace(checkout_id=12, customer_id=102),
        ]
        # sex is set so the filter passes, age is what actually gets returned
        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=101, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=102, sex="Male",   age="48-53"),
        ]
        self.mock_purchase_select.return_value = [
            SimpleNamespace(product_id=1, checkout_id=10),
            SimpleNamespace(product_id=2, checkout_id=11),
            SimpleNamespace(product_id=3, checkout_id=12),
        ]

        result = self.caa.get_product_category_most_common_gender()

        self.assertEqual(result[10], "25-32")
        self.assertEqual(result[20], "48-53")

    def test_get_product_category_most_common_gender_skips_missing_sex(self):
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk", aisle_id=10)
        ]
        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=10, customer_id=100)
        ]
        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="", age="25-32")
        ]
        self.mock_purchase_select.return_value = [
            SimpleNamespace(product_id=1, checkout_id=10)
        ]

        result = self.caa.get_product_category_most_common_gender()

        self.assertNotIn(10, result)

    def test_get_product_category_most_common_gender_no_purchases(self):
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk", aisle_id=10)
        ]
        self.mock_checkout_select.return_value = []
        self.mock_customer_select.return_value = []
        self.mock_purchase_select.return_value = []

        result = self.caa.get_product_category_most_common_gender()

        self.assertEqual(result, {})

    # --------------------------------------------------------------------- age

    def test_get_product_category_most_common_age(self):
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk",   aisle_id=10),
            SimpleNamespace(product_id=2, name="Bread",  aisle_id=10),
            SimpleNamespace(product_id=3, name="Apples", aisle_id=20),
        ]
        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=10, customer_id=100),
            SimpleNamespace(checkout_id=11, customer_id=101),
            SimpleNamespace(checkout_id=12, customer_id=102),
        ]
        # Only one age per aisle so least common == most common, test passes either way
        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=101, sex="Female", age="25-32"),
            SimpleNamespace(customer_id=102, sex="Male",   age="48-53"),
        ]
        self.mock_purchase_select.return_value = [
            SimpleNamespace(product_id=1, checkout_id=10),
            SimpleNamespace(product_id=2, checkout_id=11),
            SimpleNamespace(product_id=3, checkout_id=12),
        ]

        result = self.caa.get_product_category_most_common_age()

        self.assertEqual(result[10], "25-32")
        self.assertEqual(result[20], "48-53")

    def test_get_product_category_most_common_age_skips_empty_age(self):
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk", aisle_id=10)
        ]
        self.mock_checkout_select.return_value = [
            SimpleNamespace(checkout_id=10, customer_id=100)
        ]
        self.mock_customer_select.return_value = [
            SimpleNamespace(customer_id=100, sex="Female", age="")
        ]
        self.mock_purchase_select.return_value = [
            SimpleNamespace(product_id=1, checkout_id=10)
        ]

        result = self.caa.get_product_category_most_common_age()

        self.assertNotIn(10, result)

    def test_get_product_category_most_common_age_no_purchases(self):
        self.mock_product_select.return_value = [
            SimpleNamespace(product_id=1, name="Milk", aisle_id=10)
        ]
        self.mock_checkout_select.return_value = []
        self.mock_customer_select.return_value = []
        self.mock_purchase_select.return_value = []

        result = self.caa.get_product_category_most_common_age()

        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
