import unittest
from datetime import datetime, timedelta

from src.database import model_managers as mm
from src.database.database_setup import close_db, initialize_db
from src.database.models import Aisle, Checkout, Customer, Product, Purchase, Store
from src.logic.revenueAnalytics import get_revenue_dashboard


class RevenueAnalyticsTestCase(unittest.TestCase):
    def setUp(self):
        close_db()
        initialize_db(":memory:")

    def tearDown(self):
        close_db()

    def test_revenue_dashboard_aggregates_time_product_age_and_sex(self):
        store = mm.add_store(Store(name="Store A", owner="Owner"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        milk = mm.add_product(
            Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Milk", price=4.0)
        )
        bread = mm.add_product(
            Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Bread", price=6.0)
        )

        first_time = datetime(2026, 3, 20, 10, 15, 0)
        second_time = first_time + timedelta(hours=1, minutes=30)

        customer_a = mm.add_customer(
            Customer(store_id=store.store_id, age="25-34", sex="Female")
        )
        customer_b = mm.add_customer(
            Customer(store_id=store.store_id, age="35-44", sex="Male")
        )

        checkout_a = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer_a.customer_id,
                total_price=10.0,
                created_at=first_time,
            )
        )
        checkout_b = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer_b.customer_id,
                total_price=8.0,
                created_at=second_time,
            )
        )

        mm.add_purchase(Purchase(product_id=milk.product_id, checkout_id=checkout_a.checkout_id, quantity=1))
        mm.add_purchase(Purchase(product_id=bread.product_id, checkout_id=checkout_a.checkout_id, quantity=1))
        mm.add_purchase(Purchase(product_id=milk.product_id, checkout_id=checkout_b.checkout_id, quantity=2))

        dashboard = get_revenue_dashboard()

        self.assertAlmostEqual(dashboard.summary.total_revenue, 18.0)
        self.assertEqual(dashboard.summary.transaction_count, 2)
        self.assertAlmostEqual(dashboard.summary.average_transaction_value, 9.0)
        self.assertEqual(dashboard.summary.time_granularity, "Hour")
        self.assertEqual(dashboard.summary.peak_time_bucket, "2026-03-20 10:00")
        self.assertAlmostEqual(dashboard.summary.peak_time_bucket_revenue, 10.0)
        self.assertEqual(dashboard.summary.top_product, "Milk")
        self.assertAlmostEqual(dashboard.summary.top_product_revenue, 12.0)

        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_time],
            [("2026-03-20 10:00", 10.0), ("2026-03-20 11:00", 8.0)],
        )
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_time_transaction_count],
            [("2026-03-20 10:00", 1.0), ("2026-03-20 11:00", 1.0)],
        )
        self.assertEqual(
            [
                (datum.label, datum.revenue)
                for datum in dashboard.by_time_average_transaction_value
            ],
            [("2026-03-20 10:00", 10.0), ("2026-03-20 11:00", 8.0)],
        )
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_product],
            [("Milk", 12.0), ("Bread", 6.0)],
        )
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_customer_age],
            [("25-34", 10.0), ("35-44", 8.0)],
        )
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_customer_sex],
            [("Female", 10.0), ("Male", 8.0)],
        )

    def test_revenue_dashboard_respects_selected_time_range(self):
        store = mm.add_store(Store(name="Store A", owner="Owner"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        product = mm.add_product(
            Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Milk", price=5.0)
        )
        customer = mm.add_customer(
            Customer(store_id=store.store_id, age="25-34", sex="Female")
        )

        first_time = datetime(2026, 3, 20, 9, 0, 0)
        second_time = datetime(2026, 3, 20, 12, 0, 0)

        checkout_a = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer.customer_id,
                total_price=5.0,
                created_at=first_time,
            )
        )
        checkout_b = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer.customer_id,
                total_price=10.0,
                created_at=second_time,
            )
        )

        mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout_a.checkout_id, quantity=1))
        mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout_b.checkout_id, quantity=2))

        dashboard = get_revenue_dashboard(
            start_time=second_time - timedelta(minutes=1),
            end_time=second_time + timedelta(minutes=1),
        )

        self.assertAlmostEqual(dashboard.summary.total_revenue, 10.0)
        self.assertEqual(dashboard.summary.transaction_count, 1)
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_time],
            [("2026-03-20 12:00", 10.0)],
        )
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_time_transaction_count],
            [("2026-03-20 12:00", 1.0)],
        )
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in dashboard.by_product],
            [("Milk", 10.0)],
        )


if __name__ == "__main__":
    unittest.main()
