from datetime import datetime, timedelta


from src.database.database_setup import initialize_db, close_db
from src.database.models import (
    Store, Customer, Product, Aisle, Path,
    Checkout,Purchase,Camera,Log
)
from src.database.model_managers import (
    add_store, add_customer, add_product, add_camera, add_aisle, add_path, add_log, add_checkout, add_purchase,
    update_customer,
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

def simulate_customer(age, path_points, products):

    enter_time = datetime.now()

    customer = add_customer(Customer(
        entered_at=enter_time,
        store_id=store.store_id,
        age=age,
        sex="F",
        race= "Other"
    ))

    add_log(Log(
        store_id=store.store_id,
        action=f"Customer {customer.customer_id} entered",
        category="ENTRY",
        created_at=enter_time
    ))

    current_time = enter_time

    for x,y in path_points:
        add_path(Path(
            customer_id=customer.customer_id,
            timestamp=current_time,
            location_x=x,
            location_y=y
        ))
        current_time = timedelta(seconds=5)

    #checkout
    total = sum(p.price for p in products)

    checkout = add_checkout(Checkout(
        store_id=store.store_id,
        customer_id=customer.customer_id,
        total_price=total,
        created_at=current_time
    ))

    for p in products:
        add_purchase(Purchase(
            product_id=p.product_id,
            checkout_id=checkout.checkout_id,
            quantity = 1
        ))

    add_log(Log(
        store_id=store.store_id,
        action=f"Customer {customer.customer_id} checkout complete",
        category="CHECKOUT",
        created_at=current_time
    ))

    customer.exited_at = current_time
    customer = update_customer(customer)

    add_log(Log(
        store_id=store.store_id,
        action=f"Customer {customer.customer_id} exited",
        category="EXIT",
        created_at=current_time
    ))


simulate_customer(
    age=20,
    path_points=[(5,5), (10,15), (15,25), (25,30), (30,40), (55,10)],
    products=[chips,soda]
)

simulate_customer(
    age=47,
    path_points=[(25,10), (30,20), (45,30), (50,40), (55,10)],
    products=[milk]
)

simulate_customer(
    age=29,
    path_points=[(10,10), (15,20), (45,25), (50,35), (55,10)],
    products=[chips]
)
simulate_customer(
    age=41,
    path_points=[(5,5), (25,10), (45,20), (50,35), (55,10)],
    products=[milk, cereal]

)

simulate_customer(
    age=19,
    path_points=[(5,5), (15,30), (25,20), (35,45), (45,25), (50,40), (55,10)],
    products=[rice,coffee,milk]
)
simulate_customer(
    age=28,
    path_points=[(5,5), (25,20), (30,35), (55,10)],
    products=[coffee]
)

close_db()
print("Mock dataset created successfully.")
