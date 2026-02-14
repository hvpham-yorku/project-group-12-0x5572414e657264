from dataclasses import dataclass
from datetime import datetime


@dataclass
class Store:
    store_id: int = -1
    name: str = ""
    owner: str = ""


@dataclass
class Purchase:
    purchase_id: int = -1
    product_id: int = -1
    checkout_id: int = -1
    quantity: int = 0


@dataclass
class Path:
    path_id: int = -1
    customer_id: int = -1
    location_x: int = 0
    location_y: int = 0
    timestamp: datetime = None


@dataclass
class Checkout:
    checkout_id: int = -1
    store_id: int = -1
    customer_id: int = -1
    total_price: float = 0
    created_at: datetime = None


@dataclass
class Product:
    product_id: int = -1
    store_id: int = -1
    aisle_id: int = -1
    name: str = ""
    price: float = 0.0


@dataclass
class Customer:
    customer_id: int = -1
    entered_at: datetime = None
    exited_at: datetime = None
    store_id: int = -1


@dataclass
class Aisle:
    aisle_id: int = -1
    store_id: int = -1


@dataclass
class Camera:
    camera_id: int = -1
    store_id: int = -1
    location_x: int = 0
    location_y: int = 0


@dataclass
class Log:
    log_id: int = -1
    store_id: int = -1
    action: str = ""
    category: str = ""
    created_at: datetime = None

