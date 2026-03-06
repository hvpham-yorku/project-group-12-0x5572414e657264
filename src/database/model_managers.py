"""
model manager functions to make it easier to retrieve and store data into the database
"""

from typing import List, Optional

from src.database.models import (
    Store, Purchase, Path, Checkout, Product, Customer, Aisle, Camera, Log,
)
from src.database.database_setup import (
    StoreTable, CustomerTable, AisleTable, ProductTable,
    CameraTable, PathTable, CheckoutTable, PurchaseTable, LogTable,
)
from src.database.utils import safe_int, safe_float, safe_str, safe_bool, safe_datetime


def _row_to_store(row: StoreTable) -> Store:
    return Store(
        store_id=safe_int(row.store_id),
        name=safe_str(row.name),
        owner=safe_str(row.owner),
    )


def _row_to_customer(row: CustomerTable) -> Customer:
    return Customer(
        customer_id=safe_int(row.customer_id),
        entered_at=safe_datetime(row.entered_at),
        exited_at=safe_datetime(row.exited_at),
        store_id=safe_int(row.store_id),
        age=safe_str(row.age),
        sex=safe_str(row.sex),
    )


def _row_to_aisle(row: AisleTable) -> Aisle:
    return Aisle(
        aisle_id=safe_int(row.aisle_id),
        store_id=safe_int(row.store_id),
        bottom_left_x=safe_int(row.bottom_left_x, default=0),
        bottom_left_y=safe_int(row.bottom_left_y, default=0),
        top_right_x=safe_int(row.top_right_x, default=0),
        top_right_y=safe_int(row.top_right_y, default=0),
        vertical=safe_bool(row.vertical),
    )


def _row_to_product(row: ProductTable) -> Product:
    return Product(
        product_id=safe_int(row.product_id),
        store_id=safe_int(row.store_id),
        aisle_id=safe_int(row.aisle_id),
        name=safe_str(row.name),
        price=safe_float(row.price),
        order=safe_int(row.order, default=0),
    )


def _row_to_camera(row: CameraTable) -> Camera:
    return Camera(
        camera_id=safe_int(row.camera_id),
        store_id=safe_int(row.store_id),
        relative_file_path=safe_str(row.relative_file_path),
    )


def _row_to_path(row: PathTable) -> Path:
    return Path(
        path_id=safe_int(row.path_id),
        customer_id=safe_int(row.customer_id),
        timestamp=safe_datetime(row.timestamp),
        location_x=safe_int(row.location_x, default=0),
        location_y=safe_int(row.location_y, default=0),
    )


def _row_to_checkout(row: CheckoutTable) -> Checkout:
    return Checkout(
        checkout_id=safe_int(row.checkout_id),
        store_id=safe_int(row.store_id),
        customer_id=safe_int(row.customer_id),
        total_price=safe_float(row.total_price),
        created_at=safe_datetime(row.created_at),
    )


def _row_to_purchase(row: PurchaseTable) -> Purchase:
    return Purchase(
        purchase_id=safe_int(row.purchase_id),
        product_id=safe_int(row.product_id),
        checkout_id=safe_int(row.checkout_id),
        quantity=safe_int(row.quantity, default=0),
    )


def _row_to_log(row: LogTable) -> Log:
    return Log(
        log_id=safe_int(row.log_id),
        store_id=safe_int(row.store_id),
        action=safe_str(row.action),
        category=safe_str(row.category),
        created_at=safe_datetime(row.created_at),
    )


def add_store(store: Store) -> Store:
    row = StoreTable.create(
        name=safe_str(store.name),
        owner=safe_str(store.owner),
    )
    return _row_to_store(row)


def get_store_by_id(store_id: int) -> Optional[Store]:
    row = StoreTable.get_or_none(StoreTable.store_id == safe_int(store_id))
    return _row_to_store(row) if row else None


def get_all_stores() -> List[Store]:
    return [_row_to_store(r) for r in StoreTable.select()]


def update_store(store: Store) -> Optional[Store]:
    rows = (
        StoreTable.update(
            name=safe_str(store.name),
            owner=safe_str(store.owner),
        )
        .where(StoreTable.store_id == safe_int(store.store_id))
        .execute()
    )
    return get_store_by_id(store.store_id) if rows else None


def delete_store(store_id: int) -> bool:
    return StoreTable.delete().where(StoreTable.store_id == safe_int(store_id)).execute() > 0


def add_customer(customer: Customer) -> Customer:
    row = CustomerTable.create(
        entered_at=safe_datetime(customer.entered_at),
        exited_at=safe_datetime(customer.exited_at),
        store_id=safe_int(customer.store_id),
        age=safe_str(customer.age),
        sex=safe_str(customer.sex),
    )
    return _row_to_customer(row)


def get_customer_by_id(customer_id: int) -> Optional[Customer]:
    row = CustomerTable.get_or_none(CustomerTable.customer_id == safe_int(customer_id))
    return _row_to_customer(row) if row else None


def get_customers_by_store(store_id: int) -> List[Customer]:
    return [
        _row_to_customer(r)
        for r in CustomerTable.select().where(
            CustomerTable.store_id == safe_int(store_id)
        )
    ]


def update_customer(customer: Customer) -> Optional[Customer]:
    rows = (
        CustomerTable.update(
            entered_at=safe_datetime(customer.entered_at),
            exited_at=safe_datetime(customer.exited_at),
            store_id=safe_int(customer.store_id),
            age=safe_str(customer.age),
            sex=safe_str(customer.sex),
        )
        .where(CustomerTable.customer_id == safe_int(customer.customer_id))
        .execute()
    )
    return get_customer_by_id(customer.customer_id) if rows else None


def delete_customer(customer_id: int) -> bool:
    return (
        CustomerTable.delete()
        .where(CustomerTable.customer_id == safe_int(customer_id))
        .execute()
        > 0
    )


def add_aisle(aisle: Aisle) -> Aisle:
    row = AisleTable.create(
        store_id=safe_int(aisle.store_id),
        bottom_left_x=safe_int(aisle.bottom_left_x, default=0),
        bottom_left_y=safe_int(aisle.bottom_left_y, default=0),
        top_right_x=safe_int(aisle.top_right_x, default=0),
        top_right_y=safe_int(aisle.top_right_y, default=0),
        vertical=safe_bool(aisle.vertical),
    )
    return _row_to_aisle(row)


def get_aisle_by_id(aisle_id: int) -> Optional[Aisle]:
    row = AisleTable.get_or_none(AisleTable.aisle_id == safe_int(aisle_id))
    return _row_to_aisle(row) if row else None


def get_aisles_by_store(store_id: int) -> List[Aisle]:
    return [
        _row_to_aisle(r)
        for r in AisleTable.select().where(AisleTable.store_id == safe_int(store_id))
    ]


def update_aisle(aisle: Aisle) -> Optional[Aisle]:
    rows = (
        AisleTable.update(
            store_id=safe_int(aisle.store_id),
            bottom_left_x=safe_int(aisle.bottom_left_x, default=0),
            bottom_left_y=safe_int(aisle.bottom_left_y, default=0),
            top_right_x=safe_int(aisle.top_right_x, default=0),
            top_right_y=safe_int(aisle.top_right_y, default=0),
            vertical=safe_bool(aisle.vertical),
        )
        .where(AisleTable.aisle_id == safe_int(aisle.aisle_id))
        .execute()
    )
    return get_aisle_by_id(aisle.aisle_id) if rows else None


def delete_aisle(aisle_id: int) -> bool:
    return AisleTable.delete().where(AisleTable.aisle_id == safe_int(aisle_id)).execute() > 0


def add_product(product: Product) -> Product:
    row = ProductTable.create(
        store_id=safe_int(product.store_id),
        aisle_id=safe_int(product.aisle_id),
        name=safe_str(product.name),
        price=safe_float(product.price),
        order=safe_int(product.order, default=0),
    )
    return _row_to_product(row)


def get_product_by_id(product_id: int) -> Optional[Product]:
    row = ProductTable.get_or_none(ProductTable.product_id == safe_int(product_id))
    return _row_to_product(row) if row else None


def get_products_by_store(store_id: int) -> List[Product]:
    return [
        _row_to_product(r)
        for r in ProductTable.select().where(
            ProductTable.store_id == safe_int(store_id)
        )
    ]


def get_products_by_aisle(aisle_id: int) -> List[Product]:
    return [
        _row_to_product(r)
        for r in ProductTable.select().where(
            ProductTable.aisle_id == safe_int(aisle_id)
        )
    ]


def update_product(product: Product) -> Optional[Product]:
    rows = (
        ProductTable.update(
            store_id=safe_int(product.store_id),
            aisle_id=safe_int(product.aisle_id),
            name=safe_str(product.name),
            price=safe_float(product.price),
            order=safe_int(product.order, default=0),
        )
        .where(ProductTable.product_id == safe_int(product.product_id))
        .execute()
    )
    return get_product_by_id(product.product_id) if rows else None


def delete_product(product_id: int) -> bool:
    return (
        ProductTable.delete()
        .where(ProductTable.product_id == safe_int(product_id))
        .execute()
        > 0
    )


def add_camera(camera: Camera) -> Camera:
    row = CameraTable.create(
        store_id=safe_int(camera.store_id),
        relative_file_path=safe_str(camera.relative_file_path),
    )
    return _row_to_camera(row)


def get_camera_by_id(camera_id: int) -> Optional[Camera]:
    row = CameraTable.get_or_none(CameraTable.camera_id == safe_int(camera_id))
    return _row_to_camera(row) if row else None


def get_cameras_by_store(store_id: int) -> List[Camera]:
    return [
        _row_to_camera(r)
        for r in CameraTable.select().where(
            CameraTable.store_id == safe_int(store_id)
        )
    ]


def update_camera(camera: Camera) -> Optional[Camera]:
    rows = (
        CameraTable.update(
            store_id=safe_int(camera.store_id),
            relative_file_path=safe_str(camera.relative_file_path),
        )
        .where(CameraTable.camera_id == safe_int(camera.camera_id))
        .execute()
    )
    return get_camera_by_id(camera.camera_id) if rows else None


def delete_camera(camera_id: int) -> bool:
    return (
        CameraTable.delete()
        .where(CameraTable.camera_id == safe_int(camera_id))
        .execute()
        > 0
    )


def add_path(path: Path) -> Path:
    row = PathTable.create(
        customer_id=safe_int(path.customer_id),
        timestamp=safe_datetime(path.timestamp),
        location_x=safe_int(path.location_x, default=0),
        location_y=safe_int(path.location_y, default=0),
    )
    return _row_to_path(row)


def get_path_by_id(path_id: int) -> Optional[Path]:
    row = PathTable.get_or_none(PathTable.path_id == safe_int(path_id))
    return _row_to_path(row) if row else None


def get_paths_by_customer(customer_id: int) -> List[Path]:
    return [
        _row_to_path(r)
        for r in PathTable.select().where(
            PathTable.customer_id == safe_int(customer_id)
        )
    ]


def update_path(path: Path) -> Optional[Path]:
    rows = (
        PathTable.update(
            customer_id=safe_int(path.customer_id),
            timestamp=safe_datetime(path.timestamp),
            location_x=safe_int(path.location_x, default=0),
            location_y=safe_int(path.location_y, default=0),
        )
        .where(PathTable.path_id == safe_int(path.path_id))
        .execute()
    )
    return get_path_by_id(path.path_id) if rows else None


def delete_path(path_id: int) -> bool:
    return PathTable.delete().where(PathTable.path_id == safe_int(path_id)).execute() > 0


def add_checkout(checkout: Checkout) -> Checkout:
    row = CheckoutTable.create(
        store_id=safe_int(checkout.store_id),
        customer_id=safe_int(checkout.customer_id),
        total_price=safe_float(checkout.total_price),
        created_at=safe_datetime(checkout.created_at),
    )
    return _row_to_checkout(row)


def get_checkout_by_id(checkout_id: int) -> Optional[Checkout]:
    row = CheckoutTable.get_or_none(CheckoutTable.checkout_id == safe_int(checkout_id))
    return _row_to_checkout(row) if row else None


def get_checkouts_by_store(store_id: int) -> List[Checkout]:
    return [
        _row_to_checkout(r)
        for r in CheckoutTable.select().where(
            CheckoutTable.store_id == safe_int(store_id)
        )
    ]


def get_checkouts_by_customer(customer_id: int) -> List[Checkout]:
    return [
        _row_to_checkout(r)
        for r in CheckoutTable.select().where(
            CheckoutTable.customer_id == safe_int(customer_id)
        )
    ]


def update_checkout(checkout: Checkout) -> Optional[Checkout]:
    rows = (
        CheckoutTable.update(
            store_id=safe_int(checkout.store_id),
            customer_id=safe_int(checkout.customer_id),
            total_price=safe_float(checkout.total_price),
            created_at=safe_datetime(checkout.created_at),
        )
        .where(CheckoutTable.checkout_id == safe_int(checkout.checkout_id))
        .execute()
    )
    return get_checkout_by_id(checkout.checkout_id) if rows else None


def delete_checkout(checkout_id: int) -> bool:
    return (
        CheckoutTable.delete()
        .where(CheckoutTable.checkout_id == safe_int(checkout_id))
        .execute()
        > 0
    )


def add_purchase(purchase: Purchase) -> Purchase:
    row = PurchaseTable.create(
        product_id=safe_int(purchase.product_id),
        checkout_id=safe_int(purchase.checkout_id),
        quantity=safe_int(purchase.quantity, default=0),
    )
    return _row_to_purchase(row)


def get_purchase_by_id(purchase_id: int) -> Optional[Purchase]:
    row = PurchaseTable.get_or_none(PurchaseTable.purchase_id == safe_int(purchase_id))
    return _row_to_purchase(row) if row else None


def get_purchases_by_checkout(checkout_id: int) -> List[Purchase]:
    return [
        _row_to_purchase(r)
        for r in PurchaseTable.select().where(
            PurchaseTable.checkout_id == safe_int(checkout_id)
        )
    ]


def get_purchases_by_product(product_id: int) -> List[Purchase]:
    return [
        _row_to_purchase(r)
        for r in PurchaseTable.select().where(
            PurchaseTable.product_id == safe_int(product_id)
        )
    ]


def update_purchase(purchase: Purchase) -> Optional[Purchase]:
    rows = (
        PurchaseTable.update(
            product_id=safe_int(purchase.product_id),
            checkout_id=safe_int(purchase.checkout_id),
            quantity=safe_int(purchase.quantity, default=0),
        )
        .where(PurchaseTable.purchase_id == safe_int(purchase.purchase_id))
        .execute()
    )
    return get_purchase_by_id(purchase.purchase_id) if rows else None


def delete_purchase(purchase_id: int) -> bool:
    return (
        PurchaseTable.delete()
        .where(PurchaseTable.purchase_id == safe_int(purchase_id))
        .execute()
        > 0
    )


def add_log(log: Log) -> Log:
    row = LogTable.create(
        store_id=safe_int(log.store_id),
        action=safe_str(log.action),
        category=safe_str(log.category),
        created_at=safe_datetime(log.created_at),
    )
    return _row_to_log(row)


def get_log_by_id(log_id: int) -> Optional[Log]:
    row = LogTable.get_or_none(LogTable.log_id == safe_int(log_id))
    return _row_to_log(row) if row else None


def get_logs_by_store(store_id: int) -> List[Log]:
    return [
        _row_to_log(r)
        for r in LogTable.select().where(LogTable.store_id == safe_int(store_id))
    ]


def get_logs_by_category(category: str) -> List[Log]:
    return [
        _row_to_log(r)
        for r in LogTable.select().where(LogTable.category == safe_str(category))
    ]


def update_log(log: Log) -> Optional[Log]:
    rows = (
        LogTable.update(
            store_id=safe_int(log.store_id),
            action=safe_str(log.action),
            category=safe_str(log.category),
            created_at=safe_datetime(log.created_at),
        )
        .where(LogTable.log_id == safe_int(log.log_id))
        .execute()
    )
    return get_log_by_id(log.log_id) if rows else None


def delete_log(log_id: int) -> bool:
    return LogTable.delete().where(LogTable.log_id == safe_int(log_id)).execute() > 0
