import unittest
from datetime import datetime, timedelta

from src.database import model_managers as mm
from src.database.database_setup import close_db, initialize_db
from src.database.models import Aisle, Checkout, Customer, Product, Purchase, Store
from src.logic.graphWindowData import GraphWindow


class GraphWindowTestCase(unittest.TestCase):
    def setUp(self):
        close_db()
        initialize_db(":memory:")

    def tearDown(self):
        close_db()

    def test_empty_database_returns_safe_defaults(self):
        graph = GraphWindow()

        self.assertEqual(graph.get_countsAvailable(), [])
        self.assertEqual(graph.get_categoriesAvailable(), [])
        self.assertEqual(graph._get_possibleDateTimes(), [])
        self.assertEqual(graph.getValuesToGraph(), [[], []])
        self.assertFalse(graph.is_validState()[0])

    def test_refresh_available_options_reloads_live_database_state(self):
        graph = GraphWindow()
        self.assertEqual(graph.get_countsAvailable(), [])
        self.assertEqual(graph.get_categoriesAvailable(), [])

        entered_at = datetime(2026, 3, 1, 10, 0, 0)
        exited_at = entered_at + timedelta(minutes=20)
        checkout_time = exited_at + timedelta(minutes=5)

        store = mm.add_store(Store(name="Test Store", owner="Owner"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        product = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Milk",
                price=4.99,
            )
        )
        customer = mm.add_customer(
            Customer(
                store_id=store.store_id,
                entered_at=entered_at,
                exited_at=exited_at,
                age="25-34",
                sex="Male",
            )
        )
        checkout = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer.customer_id,
                total_price=4.99,
                created_at=checkout_time,
            )
        )
        mm.add_purchase(
            Purchase(
                product_id=product.product_id,
                checkout_id=checkout.checkout_id,
                quantity=1,
            )
        )

        graph.refresh_available_options()

        self.assertTrue(
            any(
                item.strip() == f"Category: {aisle.aisle_id}"
                for item in graph.get_countsAvailable()
            )
        )
        self.assertTrue(
            any(
                item.strip() == f"{product.name}#ID: {product.product_id}"
                for item in graph.get_countsAvailable()
            )
        )
        self.assertIn("Male", [item.strip() for item in graph.get_categoriesAvailable()])
        self.assertIn("25-34", [item.strip() for item in graph.get_categoriesAvailable()])
        self.assertEqual(
            graph._get_possibleDateTimes(),
            sorted([entered_at, exited_at, checkout_time]),
        )


if __name__ == "__main__":
    unittest.main()
