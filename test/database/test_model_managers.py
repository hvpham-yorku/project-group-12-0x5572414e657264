"""
Unit tests for src.database.model_managers
Each test gets a fresh in-memory SQLite database.
"""

import unittest
from datetime import datetime

from src.database.database_setup import initialize_db, close_db
from src.database.models import (
    Store, Customer, Aisle, Product, Camera, Path, Checkout, Purchase, Log,
)
from src.database import model_managers as mm


class DBTestCase(unittest.TestCase):
    """Base class that gives every test a clean in-memory database."""

    def setUp(self):
        close_db()
        initialize_db(":memory:")

    def tearDown(self):
        close_db()


class TestStoreManager(DBTestCase):

    def test_add_store(self):
        store = mm.add_store(Store(name="TestMart", owner="Alice"))
        self.assertIsInstance(store, Store)
        self.assertGreater(store.store_id, 0)
        self.assertEqual(store.name, "TestMart")
        self.assertEqual(store.owner, "Alice")

    def test_get_store_by_id(self):
        created = mm.add_store(Store(name="A", owner="B"))
        fetched = mm.get_store_by_id(created.store_id)
        self.assertEqual(fetched, created)

    def test_get_store_by_id_not_found(self):
        self.assertIsNone(mm.get_store_by_id(9999))

    def test_get_all_stores(self):
        mm.add_store(Store(name="S1", owner="O1"))
        mm.add_store(Store(name="S2", owner="O2"))
        stores = mm.get_all_stores()
        self.assertEqual(len(stores), 2)

    def test_update_store(self):
        created = mm.add_store(Store(name="Old", owner="Owner"))
        updated = mm.update_store(Store(store_id=created.store_id, name="New", owner="Owner"))
        self.assertEqual(updated.name, "New")
        self.assertEqual(updated.store_id, created.store_id)

    def test_delete_store(self):
        created = mm.add_store(Store(name="X", owner="Y"))
        self.assertTrue(mm.delete_store(created.store_id))
        self.assertIsNone(mm.get_store_by_id(created.store_id))

    def test_delete_store_not_found(self):
        self.assertFalse(mm.delete_store(9999))


class TestCustomerManager(DBTestCase):

    def _make_store(self):
        return mm.add_store(Store(name="S", owner="O"))

    def test_add_customer(self):
        store = self._make_store()
        now = datetime(2026, 1, 1, 12, 0, 0)
        cust = mm.add_customer(Customer(
            store_id=store.store_id, entered_at=now,
            age=30, sex="male", race="asian",
        ))
        self.assertGreater(cust.customer_id, 0)
        self.assertEqual(cust.store_id, store.store_id)
        self.assertEqual(cust.entered_at, now)
        self.assertIsNone(cust.exited_at)
        self.assertEqual(cust.age, 30)
        self.assertEqual(cust.sex, "male")
        self.assertEqual(cust.race, "asian")

    def test_get_customer_by_id(self):
        store = self._make_store()
        created = mm.add_customer(Customer(store_id=store.store_id))
        fetched = mm.get_customer_by_id(created.customer_id)
        self.assertEqual(fetched, created)

    def test_get_customer_by_id_not_found(self):
        self.assertIsNone(mm.get_customer_by_id(9999))

    def test_get_customers_by_store(self):
        s1 = self._make_store()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        mm.add_customer(Customer(store_id=s1.store_id))
        mm.add_customer(Customer(store_id=s1.store_id))
        mm.add_customer(Customer(store_id=s2.store_id))
        self.assertEqual(len(mm.get_customers_by_store(s1.store_id)), 2)
        self.assertEqual(len(mm.get_customers_by_store(s2.store_id)), 1)

    def test_update_customer(self):
        store = self._make_store()
        created = mm.add_customer(Customer(store_id=store.store_id, age=25, sex="female", race="white"))
        exit_time = datetime(2026, 1, 1, 13, 0, 0)
        updated = mm.update_customer(
            Customer(customer_id=created.customer_id, store_id=store.store_id, exited_at=exit_time, age=26, sex="female", race="white")
        )
        self.assertEqual(updated.exited_at, exit_time)
        self.assertEqual(updated.age, 26)
        self.assertEqual(updated.sex, "female")
        self.assertEqual(updated.race, "white")

    def test_delete_customer(self):
        store = self._make_store()
        created = mm.add_customer(Customer(store_id=store.store_id))
        self.assertTrue(mm.delete_customer(created.customer_id))
        self.assertIsNone(mm.get_customer_by_id(created.customer_id))

    def test_delete_customer_not_found(self):
        self.assertFalse(mm.delete_customer(9999))


class TestAisleManager(DBTestCase):

    def _make_store(self):
        return mm.add_store(Store(name="S", owner="O"))

    def test_add_aisle(self):
        store = self._make_store()
        aisle = mm.add_aisle(Aisle(
            store_id=store.store_id,
            bottom_left_x=10, bottom_left_y=20,
            top_right_x=100, top_right_y=200,
        ))
        self.assertGreater(aisle.aisle_id, 0)
        self.assertEqual(aisle.store_id, store.store_id)
        self.assertEqual(aisle.bottom_left_x, 10)
        self.assertEqual(aisle.bottom_left_y, 20)
        self.assertEqual(aisle.top_right_x, 100)
        self.assertEqual(aisle.top_right_y, 200)

    def test_get_aisle_by_id(self):
        store = self._make_store()
        created = mm.add_aisle(Aisle(store_id=store.store_id))
        self.assertEqual(mm.get_aisle_by_id(created.aisle_id), created)

    def test_get_aisle_by_id_not_found(self):
        self.assertIsNone(mm.get_aisle_by_id(9999))

    def test_get_aisles_by_store(self):
        s1 = self._make_store()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        mm.add_aisle(Aisle(store_id=s1.store_id))
        mm.add_aisle(Aisle(store_id=s1.store_id))
        mm.add_aisle(Aisle(store_id=s2.store_id))
        self.assertEqual(len(mm.get_aisles_by_store(s1.store_id)), 2)
        self.assertEqual(len(mm.get_aisles_by_store(s2.store_id)), 1)

    def test_update_aisle(self):
        s1 = self._make_store()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        created = mm.add_aisle(Aisle(store_id=s1.store_id, bottom_left_x=0, bottom_left_y=0, top_right_x=0, top_right_y=0))
        updated = mm.update_aisle(Aisle(
            aisle_id=created.aisle_id, store_id=s2.store_id,
            bottom_left_x=5, bottom_left_y=15,
            top_right_x=50, top_right_y=150,
        ))
        self.assertEqual(updated.store_id, s2.store_id)
        self.assertEqual(updated.bottom_left_x, 5)
        self.assertEqual(updated.bottom_left_y, 15)
        self.assertEqual(updated.top_right_x, 50)
        self.assertEqual(updated.top_right_y, 150)

    def test_delete_aisle(self):
        store = self._make_store()
        created = mm.add_aisle(Aisle(store_id=store.store_id))
        self.assertTrue(mm.delete_aisle(created.aisle_id))
        self.assertIsNone(mm.get_aisle_by_id(created.aisle_id))

    def test_delete_aisle_not_found(self):
        self.assertFalse(mm.delete_aisle(9999))


class TestProductManager(DBTestCase):

    def _make_dependencies(self):
        store = mm.add_store(Store(name="S", owner="O"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        return store, aisle

    def test_add_product(self):
        store, aisle = self._make_dependencies()
        prod = mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Milk", price=3.99, order=2))
        self.assertGreater(prod.product_id, 0)
        self.assertEqual(prod.name, "Milk")
        self.assertAlmostEqual(prod.price, 3.99)
        self.assertEqual(prod.order, 2)

    def test_get_product_by_id(self):
        store, aisle = self._make_dependencies()
        created = mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Eggs", price=2.50))
        self.assertEqual(mm.get_product_by_id(created.product_id), created)

    def test_get_product_by_id_not_found(self):
        self.assertIsNone(mm.get_product_by_id(9999))

    def test_get_products_by_store(self):
        store, aisle = self._make_dependencies()
        mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="A", price=1.0))
        mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="B", price=2.0))
        self.assertEqual(len(mm.get_products_by_store(store.store_id)), 2)

    def test_get_products_by_aisle(self):
        store, a1 = self._make_dependencies()
        a2 = mm.add_aisle(Aisle(store_id=store.store_id))
        mm.add_product(Product(store_id=store.store_id, aisle_id=a1.aisle_id, name="A", price=1.0))
        mm.add_product(Product(store_id=store.store_id, aisle_id=a2.aisle_id, name="B", price=2.0))
        self.assertEqual(len(mm.get_products_by_aisle(a1.aisle_id)), 1)
        self.assertEqual(len(mm.get_products_by_aisle(a2.aisle_id)), 1)

    def test_update_product(self):
        store, aisle = self._make_dependencies()
        created = mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Old", price=1.0, order=1))
        updated = mm.update_product(
            Product(product_id=created.product_id, store_id=store.store_id, aisle_id=aisle.aisle_id, name="New", price=5.0, order=3)
        )
        self.assertEqual(updated.name, "New")
        self.assertAlmostEqual(updated.price, 5.0)
        self.assertEqual(updated.order, 3)

    def test_delete_product(self):
        store, aisle = self._make_dependencies()
        created = mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="X", price=1.0))
        self.assertTrue(mm.delete_product(created.product_id))
        self.assertIsNone(mm.get_product_by_id(created.product_id))

    def test_delete_product_not_found(self):
        self.assertFalse(mm.delete_product(9999))


class TestCameraManager(DBTestCase):

    def _make_store(self):
        return mm.add_store(Store(name="S", owner="O"))

    def test_add_camera(self):
        store = self._make_store()
        cam = mm.add_camera(Camera(store_id=store.store_id))
        self.assertGreater(cam.camera_id, 0)
        self.assertEqual(cam.store_id, store.store_id)

    def test_get_camera_by_id(self):
        store = self._make_store()
        created = mm.add_camera(Camera(store_id=store.store_id))
        self.assertEqual(mm.get_camera_by_id(created.camera_id), created)

    def test_get_camera_by_id_not_found(self):
        self.assertIsNone(mm.get_camera_by_id(9999))

    def test_get_cameras_by_store(self):
        s1 = self._make_store()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        mm.add_camera(Camera(store_id=s1.store_id))
        mm.add_camera(Camera(store_id=s1.store_id))
        mm.add_camera(Camera(store_id=s2.store_id))
        self.assertEqual(len(mm.get_cameras_by_store(s1.store_id)), 2)
        self.assertEqual(len(mm.get_cameras_by_store(s2.store_id)), 1)

    def test_update_camera(self):
        s1 = self._make_store()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        created = mm.add_camera(Camera(store_id=s1.store_id))
        updated = mm.update_camera(
            Camera(camera_id=created.camera_id, store_id=s2.store_id)
        )
        self.assertEqual(updated.store_id, s2.store_id)

    def test_delete_camera(self):
        store = self._make_store()
        created = mm.add_camera(Camera(store_id=store.store_id))
        self.assertTrue(mm.delete_camera(created.camera_id))
        self.assertIsNone(mm.get_camera_by_id(created.camera_id))

    def test_delete_camera_not_found(self):
        self.assertFalse(mm.delete_camera(9999))


class TestPathManager(DBTestCase):

    def _make_customer(self):
        store = mm.add_store(Store(name="S", owner="O"))
        return mm.add_customer(Customer(store_id=store.store_id))

    def test_add_path(self):
        cust = self._make_customer()
        ts = datetime(2026, 2, 1, 10, 0, 0)
        p = mm.add_path(Path(customer_id=cust.customer_id, location_x=5, location_y=10, timestamp=ts))
        self.assertGreater(p.path_id, 0)
        self.assertEqual(p.customer_id, cust.customer_id)
        self.assertEqual(p.location_x, 5)
        self.assertEqual(p.location_y, 10)
        self.assertEqual(p.timestamp, ts)

    def test_get_path_by_id(self):
        cust = self._make_customer()
        created = mm.add_path(Path(customer_id=cust.customer_id, location_x=1, location_y=2))
        self.assertEqual(mm.get_path_by_id(created.path_id), created)

    def test_get_path_by_id_not_found(self):
        self.assertIsNone(mm.get_path_by_id(9999))

    def test_get_paths_by_customer(self):
        c1 = self._make_customer()
        c2 = self._make_customer()
        mm.add_path(Path(customer_id=c1.customer_id, location_x=0, location_y=0))
        mm.add_path(Path(customer_id=c1.customer_id, location_x=1, location_y=1))
        mm.add_path(Path(customer_id=c2.customer_id, location_x=2, location_y=2))
        self.assertEqual(len(mm.get_paths_by_customer(c1.customer_id)), 2)
        self.assertEqual(len(mm.get_paths_by_customer(c2.customer_id)), 1)

    def test_update_path(self):
        cust = self._make_customer()
        created = mm.add_path(Path(customer_id=cust.customer_id, location_x=0, location_y=0))
        new_ts = datetime(2026, 3, 1, 15, 30, 0)
        updated = mm.update_path(
            Path(path_id=created.path_id, customer_id=cust.customer_id, location_x=50, location_y=60, timestamp=new_ts)
        )
        self.assertEqual(updated.location_x, 50)
        self.assertEqual(updated.location_y, 60)
        self.assertEqual(updated.timestamp, new_ts)

    def test_delete_path(self):
        cust = self._make_customer()
        created = mm.add_path(Path(customer_id=cust.customer_id, location_x=0, location_y=0))
        self.assertTrue(mm.delete_path(created.path_id))
        self.assertIsNone(mm.get_path_by_id(created.path_id))

    def test_delete_path_not_found(self):
        self.assertFalse(mm.delete_path(9999))


class TestCheckoutManager(DBTestCase):

    def _make_deps(self):
        store = mm.add_store(Store(name="S", owner="O"))
        cust = mm.add_customer(Customer(store_id=store.store_id))
        return store, cust

    def test_add_checkout(self):
        store, cust = self._make_deps()
        now = datetime(2026, 4, 1, 9, 0, 0)
        co = mm.add_checkout(
            Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=49.99, created_at=now)
        )
        self.assertGreater(co.checkout_id, 0)
        self.assertAlmostEqual(co.total_price, 49.99)
        self.assertEqual(co.created_at, now)

    def test_get_checkout_by_id(self):
        store, cust = self._make_deps()
        created = mm.add_checkout(Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=10.0))
        self.assertEqual(mm.get_checkout_by_id(created.checkout_id), created)

    def test_get_checkout_by_id_not_found(self):
        self.assertIsNone(mm.get_checkout_by_id(9999))

    def test_get_checkouts_by_store(self):
        s1, c1 = self._make_deps()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        c2 = mm.add_customer(Customer(store_id=s2.store_id))
        mm.add_checkout(Checkout(store_id=s1.store_id, customer_id=c1.customer_id, total_price=1.0))
        mm.add_checkout(Checkout(store_id=s2.store_id, customer_id=c2.customer_id, total_price=2.0))
        self.assertEqual(len(mm.get_checkouts_by_store(s1.store_id)), 1)
        self.assertEqual(len(mm.get_checkouts_by_store(s2.store_id)), 1)

    def test_get_checkouts_by_customer(self):
        store, cust = self._make_deps()
        mm.add_checkout(Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=1.0))
        mm.add_checkout(Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=2.0))
        self.assertEqual(len(mm.get_checkouts_by_customer(cust.customer_id)), 2)

    def test_update_checkout(self):
        store, cust = self._make_deps()
        created = mm.add_checkout(Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=10.0))
        updated = mm.update_checkout(
            Checkout(checkout_id=created.checkout_id, store_id=store.store_id, customer_id=cust.customer_id, total_price=99.99)
        )
        self.assertAlmostEqual(updated.total_price, 99.99)

    def test_delete_checkout(self):
        store, cust = self._make_deps()
        created = mm.add_checkout(Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=5.0))
        self.assertTrue(mm.delete_checkout(created.checkout_id))
        self.assertIsNone(mm.get_checkout_by_id(created.checkout_id))

    def test_delete_checkout_not_found(self):
        self.assertFalse(mm.delete_checkout(9999))


class TestPurchaseManager(DBTestCase):

    def _make_deps(self):
        store = mm.add_store(Store(name="S", owner="O"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        product = mm.add_product(Product(store_id=store.store_id, aisle_id=aisle.aisle_id, name="Item", price=5.0))
        cust = mm.add_customer(Customer(store_id=store.store_id))
        checkout = mm.add_checkout(Checkout(store_id=store.store_id, customer_id=cust.customer_id, total_price=0))
        return product, checkout

    def test_add_purchase(self):
        product, checkout = self._make_deps()
        pur = mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=3))
        self.assertGreater(pur.purchase_id, 0)
        self.assertEqual(pur.product_id, product.product_id)
        self.assertEqual(pur.checkout_id, checkout.checkout_id)
        self.assertEqual(pur.quantity, 3)

    def test_get_purchase_by_id(self):
        product, checkout = self._make_deps()
        created = mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=1))
        self.assertEqual(mm.get_purchase_by_id(created.purchase_id), created)

    def test_get_purchase_by_id_not_found(self):
        self.assertIsNone(mm.get_purchase_by_id(9999))

    def test_get_purchases_by_checkout(self):
        product, checkout = self._make_deps()
        mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=1))
        mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=2))
        self.assertEqual(len(mm.get_purchases_by_checkout(checkout.checkout_id)), 2)

    def test_get_purchases_by_product(self):
        product, checkout = self._make_deps()
        mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=1))
        self.assertEqual(len(mm.get_purchases_by_product(product.product_id)), 1)

    def test_update_purchase(self):
        product, checkout = self._make_deps()
        created = mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=1))
        updated = mm.update_purchase(
            Purchase(purchase_id=created.purchase_id, product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=10)
        )
        self.assertEqual(updated.quantity, 10)

    def test_delete_purchase(self):
        product, checkout = self._make_deps()
        created = mm.add_purchase(Purchase(product_id=product.product_id, checkout_id=checkout.checkout_id, quantity=1))
        self.assertTrue(mm.delete_purchase(created.purchase_id))
        self.assertIsNone(mm.get_purchase_by_id(created.purchase_id))

    def test_delete_purchase_not_found(self):
        self.assertFalse(mm.delete_purchase(9999))


class TestLogManager(DBTestCase):

    def _make_store(self):
        return mm.add_store(Store(name="S", owner="O"))

    def test_add_log(self):
        store = self._make_store()
        now = datetime(2026, 5, 1, 8, 0, 0)
        log = mm.add_log(Log(store_id=store.store_id, action="entered", category="security", created_at=now))
        self.assertGreater(log.log_id, 0)
        self.assertEqual(log.action, "entered")
        self.assertEqual(log.category, "security")
        self.assertEqual(log.created_at, now)

    def test_get_log_by_id(self):
        store = self._make_store()
        created = mm.add_log(Log(store_id=store.store_id, action="a", category="b"))
        self.assertEqual(mm.get_log_by_id(created.log_id), created)

    def test_get_log_by_id_not_found(self):
        self.assertIsNone(mm.get_log_by_id(9999))

    def test_get_logs_by_store(self):
        s1 = self._make_store()
        s2 = mm.add_store(Store(name="S2", owner="O2"))
        mm.add_log(Log(store_id=s1.store_id, action="x", category="c"))
        mm.add_log(Log(store_id=s1.store_id, action="y", category="c"))
        mm.add_log(Log(store_id=s2.store_id, action="z", category="c"))
        self.assertEqual(len(mm.get_logs_by_store(s1.store_id)), 2)
        self.assertEqual(len(mm.get_logs_by_store(s2.store_id)), 1)

    def test_get_logs_by_category(self):
        store = self._make_store()
        mm.add_log(Log(store_id=store.store_id, action="a", category="security"))
        mm.add_log(Log(store_id=store.store_id, action="b", category="security"))
        mm.add_log(Log(store_id=store.store_id, action="c", category="sales"))
        self.assertEqual(len(mm.get_logs_by_category("security")), 2)
        self.assertEqual(len(mm.get_logs_by_category("sales")), 1)

    def test_update_log(self):
        store = self._make_store()
        created = mm.add_log(Log(store_id=store.store_id, action="old", category="cat"))
        updated = mm.update_log(
            Log(log_id=created.log_id, store_id=store.store_id, action="new", category="cat")
        )
        self.assertEqual(updated.action, "new")

    def test_delete_log(self):
        store = self._make_store()
        created = mm.add_log(Log(store_id=store.store_id, action="x", category="y"))
        self.assertTrue(mm.delete_log(created.log_id))
        self.assertIsNone(mm.get_log_by_id(created.log_id))

    def test_delete_log_not_found(self):
        self.assertFalse(mm.delete_log(9999))


if __name__ == "__main__":
    unittest.main()
