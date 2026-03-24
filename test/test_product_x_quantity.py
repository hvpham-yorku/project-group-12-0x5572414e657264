import unittest
from datetime import datetime
from collections import defaultdict

from src.database.models import Product, Purchase
from src.product_x_quantity import product_x_quantity_function

class TestProductXQuantityFunction(unittest.TestCase):

    #Test1 : Test empty purchase list returns empty dict
    def test_no_purchases(self):
        products = [Product(product_id=1, name="Apple")]
        purchases = []
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {})

    #Test 2:Test with purchases but empty product list returns Unknown keys
    def test_no_products(self):
        products = []
        purchases = [Purchase(product_id=1, quantity=3)]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Unknown-1": 3})

    #Test 3: Single purchase mapped to known product
    def test_single_purchase(self):
        products = [Product(product_id=1, name="Apple")]
        purchases = [Purchase(product_id=1, quantity=5)]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Apple": 5})

    #Test 4: Aggregates quantities for the same product
    def test_multiple_purchases_same_product(self):
        products = [Product(product_id=1, name="Apple")]
        purchases = [
            Purchase(product_id=1, quantity=2),
            Purchase(product_id=1, quantity=3)
        ]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Apple": 5})

    #Test 5: Aggregates quantities across multiple products
    def test_multiple_products(self):
        products = [
            Product(product_id=1, name="Apple"),
            Product(product_id=2, name="Banana")
        ]
        purchases = [
            Purchase(product_id=1, quantity=2),
            Purchase(product_id=2, quantity=4),
            Purchase(product_id=1, quantity=1)
        ]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Apple": 3, "Banana": 4})

    #Test 6: Handles purchases with product_id not in product list
    def test_unknown_product_id(self):
        products = [Product(product_id=1, name="Apple")]
        purchases = [Purchase(product_id=2, quantity=7)]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Unknown-2": 7})

    #Test 7: Handles purchases with zero quantity
    def test_zero_quantity_purchase(self):
        products = [Product(product_id=1, name="Apple")]
        purchases = [Purchase(product_id=1, quantity=0)]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Apple": 0})

    #Test 8: Mix of known and unknown product_ids
    def test_mix_known_and_unknown_products(self):
        products = [Product(product_id=1, name="Apple")]
        purchases = [
            Purchase(product_id=1, quantity=2),
            Purchase(product_id=2, quantity=3)
        ]
        result = product_x_quantity_function(purchases, products)
        self.assertEqual(result, {"Apple": 2, "Unknown-2": 3})


if __name__ == '__main__':
    unittest.main()
