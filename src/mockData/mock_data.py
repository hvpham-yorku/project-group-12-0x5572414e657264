from datetime import datetime

from src.database.database_setup import initialize_db, close_db
from src.database.models import (
    Store, Customer, Product, Aisle, Path,
    Checkout,Purchase,Camera,Log
)
from src.database.model_managers import (
    add_store, add_customer, add_product, add_camera, add_aisle,
)

# initialize database
initialize_db("store.db")

store = add_store(Store(
    name = "SmartMart",
    owner = "Anne"
))

add_camera(Camera(store_id=store.store_id))
add_camera(Camera(store_id=store.store_id))

aisle1 = add_aisle(Aisle(store_id=store.store_id, bottom_left_x=0, bottom_left_y=0, top_right_x=20, top_right_y=60))
aisle2 = add_aisle(Aisle(store_id=store.store_id, bottom_left_x=20, bottom_left_y=0, top_right_x=40, top_right_y=60))
aisle3 = add_aisle(Aisle(store_id=store.store_id, bottom_left_x=40, bottom_left_y=0, top_right_x=60, top_right_y=60))

chips = add_product(Product(store_id=store.store_id, aisle_id=aisle1.aisle_id, name="Chips", price=3.49,order=1))
soda = add_product(Product(store_id=store.store_id, aisle_id=aisle2.aisle_id, name="Soda", price=2.25,order=1))
milk = add_product(Product(store_id=store.store_id, aisle_id=aisle3.aisle_id, name="Milk", price=4.75,order=1))
cereal = add_product(Product(store_id=store.store_id, aisle_id=aisle3.aisle_id, name="Cereal", price=5.55,order=2))
rice = add_product(Product(store_id=store.store_id, aisle_id=aisle1.aisle_id, name="Rice", price=8.00,order=3))
coffee = add_product(Product(store_id=store.store_id, aisle_id=aisle2.aisle_id, name="Coffee", price=12.30,order=2))

