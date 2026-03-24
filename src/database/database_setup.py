"""
Database and Peewee table definitions.
Call initialize_db() before performing any database operations.
"""

import peewee as pw


db = pw.SqliteDatabase(None)


def initialize_db(db_path: str = "store.db"):
    """Initialize the database connection and create all tables."""
    db.init(db_path)
    db.connect()
    db.create_tables([
        StoreTable, CustomerTable, AisleTable, ProductTable,
        CameraTable, PathTable, CheckoutTable, PurchaseTable, LogTable,
    ])


def close_db():
    """Close the database connection."""
    if not db.is_closed():
        db.close()


class BaseTable(pw.Model):
    class Meta:
        database = db


class StoreTable(BaseTable):
    store_id = pw.AutoField()
    name = pw.CharField(max_length=255, default="")
    owner = pw.CharField(max_length=255, default="")
    height = pw.IntegerField(default=0)
    width = pw.IntegerField(default=0)

    class Meta:
        table_name = "store"


class CustomerTable(BaseTable):
    customer_id = pw.AutoField()
    entered_at = pw.DateTimeField(null=True, default=None)
    exited_at = pw.DateTimeField(null=True, default=None)
    store_id = pw.IntegerField()
    age = pw.CharField(max_length=255, default="")
    sex = pw.CharField(max_length=255, default="")

    class Meta:
        table_name = "customer"


class AisleTable(BaseTable):
    aisle_id = pw.AutoField()
    store_id = pw.IntegerField()
    bottom_left_x = pw.IntegerField(default=0)
    bottom_left_y = pw.IntegerField(default=0)
    top_right_x = pw.IntegerField(default=0)
    top_right_y = pw.IntegerField(default=0)
    vertical = pw.BooleanField(default=False)

    class Meta:
        table_name = "aisle"


class ProductTable(BaseTable):
    product_id = pw.AutoField()
    store_id = pw.IntegerField()
    aisle_id = pw.IntegerField()
    name = pw.CharField(max_length=255, default="")
    price = pw.DoubleField(default=0.0)
    order = pw.IntegerField(default=0)

    class Meta:
        table_name = "product"


class CameraTable(BaseTable):
    camera_id = pw.AutoField()
    store_id = pw.IntegerField()
    relative_file_path = pw.CharField(default="")

    class Meta:
        table_name = "camera"


class PathTable(BaseTable):
    path_id = pw.AutoField()
    customer_id = pw.IntegerField()
    timestamp = pw.DateTimeField(null=True, default=None)
    location_x = pw.IntegerField(default=0)
    location_y = pw.IntegerField(default=0)

    class Meta:
        table_name = "path"


class CheckoutTable(BaseTable):
    checkout_id = pw.AutoField()
    total_price = pw.DoubleField(default=0.0)
    created_at = pw.DateTimeField(null=True, default=None)
    store_id = pw.IntegerField()
    customer_id = pw.IntegerField()

    class Meta:
        table_name = "checkout"


class PurchaseTable(BaseTable):
    purchase_id = pw.AutoField()
    product_id = pw.IntegerField()
    checkout_id = pw.IntegerField()
    quantity = pw.IntegerField(default=0)

    class Meta:
        table_name = "purchase"


class LogTable(BaseTable):
    log_id = pw.AutoField()
    action = pw.TextField(default="")
    category = pw.TextField(default="")
    created_at = pw.DateTimeField(null=True, default=None)
    store_id = pw.IntegerField()

    class Meta:
        table_name = "log"
