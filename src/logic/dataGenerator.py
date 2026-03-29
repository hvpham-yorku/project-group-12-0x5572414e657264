"""
Data generation functions for simulating a day of store activity.

Store layout (100 x 60 grid, origin at bottom-left):

    y=60 +----------------------------------------------------+
         |                    (back wall)                      |
    y=50 |   [A1]    [A2]    [A3]    [A4]    [A5]            |
         |   [  ]    [  ]    [  ]    [  ]    [  ]            |
         |   [  ]    [  ]    [  ]    [  ]    [  ]            |
    y=15 |   [A1]    [A2]    [A3]    [A4]    [A5]            |
         |                                                    |
    y=5  |          [C1]     [C2]     [C3]                   |
    y=0  +------------ [entrance/exit] ----------------------+
        x=0                 x=50                           x=100

    A1-A5: Aisles — each rectangle covers the walkway plus shelves
           on both sides.  Customers walk through the center of an
           aisle to browse / pick up products.
    C1-C3: Checkout counters.
    The open space between aisle rectangles are the main corridors
    customers use to move from one aisle to another.
"""

import csv
import math
import os
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

from src.database.models import (
    Store,
    Aisle,
    Product,
    Customer,
    Checkout,
    Purchase,
    Path,
)
from src.database.database_setup import (
    db,
    StoreTable,
    CustomerTable,
    AisleTable,
    ProductTable,
    CameraTable,
    PathTable,
    CheckoutTable,
    PurchaseTable,
    LogTable,
)
from src.utils.paths import get_data_path


# ──────────────────────────────────────────────────────────────
# Store Layout Constants
# ──────────────────────────────────────────────────────────────

STORE_WIDTH = 100
STORE_HEIGHT = 60

NUM_AISLES = 5
AISLE_WIDTH = 14
AISLE_GAP = 0
AISLE_Y_START = 15
AISLE_Y_END = 50

SHELF_DEPTH = 3

_TOTAL_AISLES_WIDTH = NUM_AISLES * AISLE_WIDTH + (NUM_AISLES - 1) * AISLE_GAP
AISLE_X_START = (STORE_WIDTH - _TOTAL_AISLES_WIDTH) // 2

ENTRANCE_X = STORE_WIDTH // 2
ENTRANCE_Y = 0

CHECKOUT_Y = 5
CHECKOUT_X_POSITIONS = [25, 50, 75]

_CORRIDOR_Y = 12
_BROWSE_DWELL = 20

AGE_GROUPS: list[tuple[int, int]] = [
    (18, 24),
    (25, 34),
    (35, 44),
    (45, 54),
    (55, 64),
    (65, 78),
]


def _assign_age_group(age: int) -> str:
    """Map a concrete age to its fixed demographic bin label."""
    for lo, hi in AGE_GROUPS:
        if lo <= age <= hi:
            return f"({lo}-{hi})"
    return f"({AGE_GROUPS[-1][0]}-{AGE_GROUPS[-1][1]})"


# ──────────────────────────────────────────────────────────────
# Product Catalog — (name, price, order)
#
# `order` = position along the aisle from the entrance end (1)
# to the far end.  Two products sharing the same order are at
# roughly the same spot (e.g. opposite sides of the walkway).
# 30 items per aisle × 5 aisles = 150 total.
# ──────────────────────────────────────────────────────────────

AISLE_CATEGORIES = [
    {
        "name": "Bakery & Bread",
        "products": [
            ("White Bread", 2.49, 1),
            ("Whole Wheat Bread", 3.29, 1),
            ("Sourdough Loaf", 4.99, 2),
            ("Rye Bread", 3.49, 2),
            ("Bagels (6-pack)", 3.99, 3),
            ("Croissants (4-pack)", 5.49, 4),
            ("English Muffins", 3.29, 4),
            ("Pita Bread", 2.99, 5),
            ("Tortillas (10-pack)", 3.49, 5),
            ("Hamburger Buns (8-pack)", 2.99, 6),
            ("Hot Dog Buns (8-pack)", 2.99, 6),
            ("Cinnamon Raisin Bread", 3.79, 7),
            ("Banana Bread", 4.49, 8),
            ("Dinner Rolls (12-pack)", 3.99, 8),
            ("Baguette", 2.49, 9),
            ("Cornbread Mix", 2.29, 10),
            ("Naan Bread (4-pack)", 3.99, 10),
            ("Brioche Rolls", 4.29, 11),
            ("Multigrain Bread", 3.49, 12),
            ("Ciabatta Rolls (4-pack)", 3.99, 12),
            ("Challah Bread", 5.49, 13),
            ("Pumpernickel Bread", 3.79, 13),
            ("Flatbread", 3.29, 14),
            ("Crumpets (6-pack)", 3.49, 15),
            ("Breadsticks", 2.99, 15),
            ("Garlic Bread", 3.49, 16),
            ("Focaccia", 4.49, 17),
            ("Marble Rye", 3.79, 17),
            ("Oat Bread", 3.29, 18),
            ("Gluten-Free Bread", 5.99, 18),
        ],
    },
    {
        "name": "Canned Goods & Soups",
        "products": [
            ("Chicken Noodle Soup", 1.99, 1),
            ("Tomato Soup", 1.49, 1),
            ("Cream of Mushroom Soup", 1.79, 2),
            ("Vegetable Soup", 1.79, 2),
            ("Minestrone Soup", 2.29, 3),
            ("Lentil Soup", 1.99, 3),
            ("Clam Chowder", 2.49, 4),
            ("Beef Stew", 2.99, 4),
            ("Chili with Beans", 2.49, 5),
            ("Black Beans", 1.29, 6),
            ("Kidney Beans", 1.29, 6),
            ("Chickpeas", 1.49, 7),
            ("Canned Corn", 1.19, 8),
            ("Canned Peas", 1.19, 8),
            ("Canned Green Beans", 1.19, 9),
            ("Diced Tomatoes", 1.49, 9),
            ("Tomato Paste", 0.99, 10),
            ("Tomato Sauce", 1.29, 10),
            ("Canned Tuna", 1.99, 11),
            ("Canned Salmon", 3.49, 11),
            ("Canned Sardines", 2.49, 12),
            ("Canned Peaches", 1.99, 13),
            ("Canned Pineapple", 1.79, 13),
            ("Canned Mandarin Oranges", 1.49, 14),
            ("Canned Pumpkin", 2.29, 14),
            ("Coconut Milk", 1.99, 15),
            ("Evaporated Milk", 1.49, 16),
            ("Sweetened Condensed Milk", 1.79, 16),
            ("Canned Olives", 2.49, 17),
            ("Canned Artichoke Hearts", 2.99, 17),
        ],
    },
    {
        "name": "Snacks & Chips",
        "products": [
            ("Potato Chips (Original)", 3.99, 1),
            ("BBQ Potato Chips", 3.99, 1),
            ("Sour Cream & Onion Chips", 3.99, 2),
            ("Tortilla Chips", 3.49, 2),
            ("Pretzels", 2.99, 3),
            ("Cheese Puffs", 3.49, 3),
            ("Butter Popcorn", 3.29, 4),
            ("Kettle Corn", 3.49, 4),
            ("Trail Mix", 4.99, 5),
            ("Mixed Nuts", 5.99, 6),
            ("Almonds", 6.49, 6),
            ("Cashews", 7.49, 7),
            ("Salted Peanuts", 3.49, 7),
            ("Granola Bars (6-pack)", 3.99, 8),
            ("Protein Bars (4-pack)", 5.99, 8),
            ("Rice Cakes", 2.99, 9),
            ("Saltine Crackers", 2.49, 10),
            ("Wheat Crackers", 3.29, 10),
            ("Cheese Crackers", 3.49, 11),
            ("Graham Crackers", 3.29, 11),
            ("Animal Crackers", 2.99, 12),
            ("Beef Jerky", 6.99, 13),
            ("Dried Mango", 3.99, 14),
            ("Dried Cranberries", 3.49, 14),
            ("Fruit Snacks", 3.29, 15),
            ("Veggie Straws", 3.49, 15),
            ("Pita Chips", 3.29, 16),
            ("Salsa (Jar)", 3.49, 17),
            ("Hummus", 3.99, 17),
            ("Guacamole", 4.49, 18),
        ],
    },
    {
        "name": "Beverages",
        "products": [
            ("Spring Water (24-pack)", 4.99, 1),
            ("Sparkling Water (12-pack)", 5.99, 1),
            ("Cola (12-pack)", 6.49, 2),
            ("Diet Cola (12-pack)", 6.49, 2),
            ("Lemon-Lime Soda (12-pack)", 6.49, 3),
            ("Ginger Ale (12-pack)", 6.49, 3),
            ("Orange Juice (64 oz)", 4.49, 4),
            ("Apple Juice (64 oz)", 3.99, 4),
            ("Grape Juice (64 oz)", 4.29, 5),
            ("Cranberry Juice (64 oz)", 4.49, 5),
            ("Lemonade (64 oz)", 3.49, 6),
            ("Iced Tea (64 oz)", 3.29, 6),
            ("Green Tea (20-pack)", 4.99, 7),
            ("Black Tea (20-pack)", 3.99, 7),
            ("Herbal Tea (20-pack)", 4.49, 8),
            ("Ground Coffee (12 oz)", 7.99, 9),
            ("Whole Bean Coffee (12 oz)", 9.99, 9),
            ("Instant Coffee", 5.49, 10),
            ("Coffee Pods (12-pack)", 8.99, 10),
            ("Hot Chocolate Mix", 3.99, 11),
            ("Almond Milk (64 oz)", 3.49, 12),
            ("Oat Milk (64 oz)", 4.29, 12),
            ("Soy Milk (64 oz)", 3.29, 13),
            ("Coconut Water", 2.49, 13),
            ("Sports Drink (8-pack)", 6.99, 14),
            ("Energy Drink (4-pack)", 7.49, 14),
            ("Tomato Juice (46 oz)", 3.49, 15),
            ("Vegetable Juice (46 oz)", 3.99, 15),
            ("Kombucha", 3.49, 16),
            ("Protein Shake (4-pack)", 7.99, 16),
        ],
    },
    {
        "name": "Dairy & Frozen",
        "products": [
            ("Whole Milk (1 gal)", 3.99, 1),
            ("2% Milk (1 gal)", 3.89, 1),
            ("Skim Milk (1 gal)", 3.79, 2),
            ("Heavy Cream (16 oz)", 3.49, 3),
            ("Half and Half (32 oz)", 3.29, 3),
            ("Unsalted Butter", 4.49, 4),
            ("Salted Butter", 4.49, 4),
            ("Cream Cheese (8 oz)", 2.49, 5),
            ("Cheddar Cheese (8 oz)", 3.99, 6),
            ("Mozzarella Cheese (8 oz)", 3.79, 6),
            ("Swiss Cheese (8 oz)", 4.29, 7),
            ("Grated Parmesan Cheese", 4.99, 7),
            ("Vanilla Yogurt (32 oz)", 4.49, 8),
            ("Greek Yogurt (Plain, 32 oz)", 5.49, 8),
            ("Sour Cream (16 oz)", 2.49, 9),
            ("Cottage Cheese (16 oz)", 3.29, 9),
            ("Eggs (12-pack)", 3.49, 10),
            ("Egg Whites (32 oz)", 4.99, 10),
            ("Vanilla Ice Cream (48 oz)", 4.99, 11),
            ("Chocolate Ice Cream (48 oz)", 4.99, 11),
            ("Frozen Pizza (Cheese)", 5.49, 12),
            ("Frozen Pizza (Pepperoni)", 5.99, 12),
            ("Frozen Mixed Vegetables", 2.49, 13),
            ("Frozen Broccoli", 2.29, 13),
            ("Frozen Corn", 2.29, 14),
            ("Frozen French Fries", 3.49, 14),
            ("Frozen Chicken Nuggets", 6.49, 15),
            ("Frozen Fish Fillets", 7.49, 15),
            ("Frozen Burritos (8-pack)", 5.99, 16),
            ("Frozen Waffles (10-pack)", 3.49, 16),
        ],
    },
]


# ──────────────────────────────────────────────────────────────
# Customer Arrival Distribution
#
# Weights per hour for a typical grocery-store day (7 AM – 9 PM).
# Two peaks: lunch (12 PM) and after-work (5 PM), with a clear
# afternoon lull (2–3 PM).  Weights sum to 1.0.
# ──────────────────────────────────────────────────────────────

HOURLY_ARRIVAL_WEIGHTS = {
    7: 0.02,  # early-morning trickle
    8: 0.05,  # morning opening
    9: 0.08,  # morning rush
    10: 0.06,  # mid-morning
    11: 0.09,  # pre-lunch pickup
    12: 0.12,  # lunch-rush peak
    13: 0.08,  # post-lunch
    14: 0.05,  # afternoon lull
    15: 0.05,  # afternoon lull
    16: 0.08,  # late-afternoon pickup
    17: 0.12,  # evening-rush peak
    18: 0.10,  # evening rush
    19: 0.06,  # evening tapering
    20: 0.03,  # late evening
    21: 0.01,  # near closing
}

# Common aisle-visiting patterns (0-based indices into the sorted
# aisle list).  Used to make shopping baskets more realistic:
# customers who buy bread often also buy dairy, etc.
_AISLE_COMBOS = [
    [0, 4],  # Bakery + Dairy
    [2, 3],  # Snacks + Beverages
    [0, 1, 4],  # Bakery + Canned Goods + Dairy
    [1, 3],  # Canned Goods + Beverages
    [0, 2, 3, 4],  # Bakery + Snacks + Beverages + Dairy
]


def resolve_sales_csv_dir(csv_dir: str = "generated_data") -> str:
    """
    Resolve sales CSV directories while preserving the existing dev behavior.
    """
    csv_path = Path(csv_dir).expanduser()
    if csv_path.is_absolute():
        return str(csv_path)

    if getattr(sys, "frozen", False):
        return str(Path(get_data_path()).joinpath(csv_path))

    return str(Path(os.getcwd()).resolve().parent.joinpath(csv_path))


# ──────────────────────────────────────────────────────────────
# Generator Functions
# ──────────────────────────────────────────────────────────────


def generate_store_and_aisles(store_id: int = 1) -> tuple[Store, list[Aisle]]:
    """Generate a Store and its 5 vertical parallel aisles.

    Each aisle rectangle covers the walkway and the shelves on both
    sides.  The aisles are contiguous (no gaps) — adjacent aisles share
    a back-to-back shelf wall.  Customers enter/exit aisles from the
    open zones above (y > AISLE_Y_END) or below (y < AISLE_Y_START).

    Within each 14-unit-wide aisle: 3 units left shelf, 8 units
    walkway, 3 units right shelf (see ``SHELF_DEPTH``).

    Computed aisle positions (with default constants):
        Aisle 1  Bakery & Bread      : (15, 15) -> (29, 50)
        Aisle 2  Canned Goods & Soups: (29, 15) -> (43, 50)
        Aisle 3  Snacks & Chips      : (43, 15) -> (57, 50)
        Aisle 4  Beverages           : (57, 15) -> (71, 50)
        Aisle 5  Dairy & Frozen      : (71, 15) -> (85, 50)

    Returns:
        (Store, list[Aisle]) with sequential IDs starting from 1.
    """
    store = Store(
        store_id=store_id,
        name="SimMart",
        owner="DataGen Corp",
        height=STORE_HEIGHT,
        width=STORE_WIDTH,
    )

    aisles: list[Aisle] = []
    for i in range(NUM_AISLES):
        x = AISLE_X_START + i * (AISLE_WIDTH + AISLE_GAP)
        aisles.append(
            Aisle(
                aisle_id=i + 1,
                store_id=store_id,
                bottom_left_x=x,
                bottom_left_y=AISLE_Y_START,
                top_right_x=x + AISLE_WIDTH,
                top_right_y=AISLE_Y_END,
                vertical=True,
            )
        )

    return store, aisles


def generate_products(store_id: int, aisles: list[Aisle]) -> list[Product]:
    """Generate products from the catalog and assign them to aisles.

    Each of the 5 aisles receives 30 products for a total of 150 items.
    The ``order`` field represents the product's position along the
    aisle from the entrance end (order 1) toward the far end.  Products
    that share the same order value are at roughly the same spot in the
    aisle (e.g. opposite sides of the walkway or adjacent on the shelf).

    Args:
        store_id: The store these products belong to.
        aisles:   The list of Aisle objects (must contain 5 aisles whose
                  order matches AISLE_CATEGORIES).

    Returns:
        list[Product] with sequential product_ids starting from 1.
    """
    if len(aisles) != len(AISLE_CATEGORIES):
        raise ValueError(f"Expected {len(AISLE_CATEGORIES)} aisles, got {len(aisles)}")

    products: list[Product] = []
    product_id = 1

    for aisle, category in zip(aisles, AISLE_CATEGORIES):
        for name, price, order in category["products"]:
            products.append(
                Product(
                    product_id=product_id,
                    store_id=store_id,
                    aisle_id=aisle.aisle_id,
                    name=name,
                    price=price,
                    order=order,
                )
            )
            product_id += 1

    return products


def generate_customers(
    store_id: int,
    num_customers: int = 1000,
    base_date: datetime | None = None,
) -> list[Customer]:
    """Generate customers with entry/exit times following realistic daily patterns.

    Entry times are sampled from ``HOURLY_ARRIVAL_WEIGHTS`` so the data
    shows clear morning, lunch, and evening rushes with lulls in between.

    Shopping duration follows a triangular distribution (5–60 min,
    mode 20 min).  The duration determines how long the customer is in
    the store and is later used by ``generate_checkouts_and_purchases``
    to decide basket size.

    Demographics (age range string and sex) are sampled from weighted
    distributions that approximate a typical grocery-store population.

    Returned list is sorted by ``entered_at`` with sequential IDs.

    Args:
        store_id:      Store the customers belong to.
        num_customers: How many customers to generate (default 1000).
        base_date:     The calendar day to simulate.  Only the date
                       portion is used; time is overwritten.  Defaults
                       to today.
    """
    if base_date is None:
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    hours = list(HOURLY_ARRIVAL_WEIGHTS.keys())
    weights = list(HOURLY_ARRIVAL_WEIGHTS.values())
    arrival_hours = random.choices(hours, weights=weights, k=num_customers)

    customers: list[Customer] = []
    for hour in arrival_hours:
        entry_time = base_date.replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )

        duration_min = random.triangular(5, 60, 20)
        exit_time = entry_time + timedelta(minutes=duration_min)

        age = int(random.triangular(18, 78, 35))
        age = max(AGE_GROUPS[0][0], min(AGE_GROUPS[-1][1], age))
        age_str = _assign_age_group(age)

        sex = random.choices(["M", "F"], weights=[0.45, 0.55])[0]

        customers.append(
            Customer(
                entered_at=entry_time,
                exited_at=exit_time,
                store_id=store_id,
                age=age_str,
                sex=sex,
            )
        )

    customers.sort(key=lambda c: c.entered_at)
    for idx, cust in enumerate(customers):
        cust.customer_id = idx + 1

    return customers


def generate_checkouts_and_purchases(
    store_id: int,
    customers: list[Customer],
    products: list[Product],
    checkout_rate: float = 0.95,
) -> tuple[list[Checkout], list[Purchase]]:
    """Generate one checkout per purchasing customer, each with purchases.

    About ``checkout_rate`` (default 95 %) of customers make a purchase;
    the rest are browsers who leave without buying.

    Basket construction:
      * Shopping duration (``exited_at - entered_at``) determines both
        the number of aisles visited and the number of items picked.
      * Aisles are chosen using common affinity patterns (e.g. Bakery +
        Dairy) for small trips, and random selection for large ones.
      * Within an aisle, products are picked at random but **two products
        with the same order value are never both selected** — they sit at
        the same spot so a customer would choose one or the other.
      * Quantities are mostly 1 (80 %), occasionally 2 (15 %) or 3 (5 %).

    ``Checkout.total_price`` is the sum of ``product.price * quantity``
    across all purchases in that checkout.

    ``Checkout.created_at`` is placed 1-3 minutes before the customer's
    ``exited_at`` (time to pay and walk to exit), but never earlier than
    2 minutes after ``entered_at``.

    Args:
        store_id:      Store ID for the checkout records.
        customers:     Full customer list (from ``generate_customers``).
        products:      Full product list (from ``generate_products``).
        checkout_rate: Fraction of customers who purchase (0.0–1.0).

    Returns:
        (list[Checkout], list[Purchase]) with sequential IDs.
    """
    products_by_aisle: dict[int, list[Product]] = {}
    for p in products:
        products_by_aisle.setdefault(p.aisle_id, []).append(p)
    aisle_ids = sorted(products_by_aisle.keys())

    aisle_combos: list[list[int]] = []
    for indices in _AISLE_COMBOS:
        combo = [aisle_ids[i] for i in indices if i < len(aisle_ids)]
        if combo:
            aisle_combos.append(combo)

    num_checkouts = int(len(customers) * checkout_rate)
    checkout_customers = sorted(
        random.sample(customers, k=num_checkouts),
        key=lambda c: c.customer_id,
    )

    checkouts: list[Checkout] = []
    purchases: list[Purchase] = []
    checkout_id = 1
    purchase_id = 1

    for customer in checkout_customers:
        duration_min = (customer.exited_at - customer.entered_at).total_seconds() / 60.0

        num_items, num_aisles = _basket_params(duration_min)
        num_aisles = min(num_aisles, len(aisle_ids))

        visited = _pick_aisles(aisle_ids, aisle_combos, num_aisles)
        basket = _build_basket(visited, products_by_aisle, num_items)
        if not basket:
            continue

        purchase_items: list[tuple[Product, int]] = []
        for product in basket:
            qty = random.choices([1, 2, 3], weights=[0.80, 0.15, 0.05])[0]
            purchase_items.append((product, qty))

        total_price = round(sum(p.price * q for p, q in purchase_items), 2)

        buffer_min = random.uniform(1.0, 3.0)
        checkout_time = customer.exited_at - timedelta(minutes=buffer_min)
        earliest_checkout = customer.entered_at + timedelta(minutes=2)
        if checkout_time < earliest_checkout:
            checkout_time = earliest_checkout

        checkouts.append(
            Checkout(
                checkout_id=checkout_id,
                store_id=store_id,
                customer_id=customer.customer_id,
                total_price=total_price,
                created_at=checkout_time,
            )
        )

        for product, qty in purchase_items:
            purchases.append(
                Purchase(
                    purchase_id=purchase_id,
                    product_id=product.product_id,
                    checkout_id=checkout_id,
                    quantity=qty,
                )
            )
            purchase_id += 1

        checkout_id += 1

    return checkouts, purchases


# ──────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────


def _basket_params(duration_min: float) -> tuple[int, int]:
    """Return (num_items, num_aisles) based on shopping duration."""
    if duration_min < 12:
        return random.randint(1, 3), 1
    if duration_min < 20:
        return random.randint(2, 6), random.randint(1, 2)
    if duration_min < 35:
        return random.randint(4, 10), random.randint(2, 3)
    if duration_min < 50:
        return random.randint(8, 16), random.randint(3, 4)
    return random.randint(12, 22), random.randint(4, 5)


def _pick_aisles(
    aisle_ids: list[int],
    aisle_combos: list[list[int]],
    num_aisles: int,
) -> list[int]:
    """Select which aisles a customer visits.

    For small trips (<=3 aisles) there is a 60 % chance of using one of
    the predefined affinity combos; otherwise aisles are random.
    """
    if num_aisles <= 3 and random.random() < 0.6:
        valid = [c for c in aisle_combos if len(c) == num_aisles]
        if valid:
            return list(random.choice(valid))
    return random.sample(aisle_ids, k=num_aisles)


def _build_basket(
    visited_aisle_ids: list[int],
    products_by_aisle: dict[int, list[Product]],
    num_items: int,
) -> list[Product]:
    """Pick products from the visited aisles.

    Items are distributed roughly evenly across the visited aisles.
    Within an aisle, two products that share the same ``order`` value
    are never both selected (they are alternatives at the same shelf
    position, not complements).
    """
    n_aisles = len(visited_aisle_ids)
    base, extra = divmod(num_items, n_aisles)
    counts = [base + (1 if i < extra else 0) for i in range(n_aisles)]
    random.shuffle(counts)

    basket: list[Product] = []
    for aisle_id, count in zip(visited_aisle_ids, counts):
        available = list(products_by_aisle[aisle_id])
        random.shuffle(available)

        picked = 0
        used_orders: set[int] = set()
        for product in available:
            if picked >= count:
                break
            if product.order not in used_orders:
                basket.append(product)
                used_orders.add(product.order)
                picked += 1

    return basket


# ──────────────────────────────────────────────────────────────
# Path generation
# ──────────────────────────────────────────────────────────────


def generate_paths(
    customers: list[Customer],
    checkouts: list[Checkout],
    purchases: list[Purchase],
    products: list[Product],
    aisles: list[Aisle],
    recording_interval: int = 5,
) -> list[Path]:
    """Generate camera-tracking-style path data for every customer.

    For each customer the function:
      1. Determines which aisles were visited (from purchases).
      2. Builds a waypoint route: entrance -> bottom corridor ->
         each aisle (left-to-right) -> checkout counter -> exit.
      3. Distributes timestamps across the route so the shopping
         phase fills ``entered_at`` to ``checkout.created_at`` and
         the exit phase fills ``checkout.created_at`` to ``exited_at``.
      4. Interpolates path points at ``recording_interval``-second
         steps with small Gaussian noise to simulate natural movement.

    Customers without a checkout (browsers) get a short route that
    enters 1-2 random aisles and then leaves.

    All paths stay within walkable areas — the bottom corridor
    (y < AISLE_Y_START) is obstacle-free, so horizontal movement
    never crosses an aisle rectangle.

    Args:
        customers:          From ``generate_customers``.
        checkouts:          From ``generate_checkouts_and_purchases``.
        purchases:          From ``generate_checkouts_and_purchases``.
        products:           From ``generate_products``.
        aisles:             From ``generate_store_and_aisles``.
        recording_interval: Seconds between path points (default 5).

    Returns:
        list[Path] with sequential ``path_id`` values starting from 1.
    """
    product_by_id = {p.product_id: p for p in products}
    aisle_by_id = {a.aisle_id: a for a in aisles}
    checkout_by_cust: dict[int, Checkout] = {}
    for co in checkouts:
        checkout_by_cust[co.customer_id] = co
    purchases_by_checkout: dict[int, list[Purchase]] = {}
    for pu in purchases:
        purchases_by_checkout.setdefault(pu.checkout_id, []).append(pu)

    max_order_per_aisle: dict[int, int] = {}
    for p in products:
        prev = max_order_per_aisle.get(p.aisle_id, 0)
        max_order_per_aisle[p.aisle_id] = max(prev, p.order)

    all_paths: list[Path] = []
    path_id = 1

    for customer in customers:
        co = checkout_by_cust.get(customer.customer_id)

        if co is not None:
            co_purchases = purchases_by_checkout.get(co.checkout_id, [])
            bought = [product_by_id[pu.product_id] for pu in co_purchases]
            checkout_x = random.choice(CHECKOUT_X_POSITIONS)

            waypoints = _build_shopper_route(
                bought,
                aisle_by_id,
                max_order_per_aisle,
                checkout_x,
            )

            co_idx = next(
                i for i, (_, _, wt) in enumerate(waypoints) if wt == "checkout"
            )
            shop_wps = waypoints[: co_idx + 1]
            shop_secs = (co.created_at - customer.entered_at).total_seconds()
            timed_shop = _distribute_time(
                shop_wps,
                customer.entered_at,
                shop_secs,
            )

            exit_secs = (customer.exited_at - co.created_at).total_seconds()
            timed_exit = _build_exit_timed(
                checkout_x,
                co.created_at,
                exit_secs,
            )

            timed = timed_shop + timed_exit[1:]
        else:
            waypoints = _build_browser_route(aisles)
            total_secs = (customer.exited_at - customer.entered_at).total_seconds()
            timed = _distribute_time(
                waypoints,
                customer.entered_at,
                total_secs,
            )

        sampled = _interpolate(timed, recording_interval)

        for x, y, t in sampled:
            all_paths.append(
                Path(
                    path_id=path_id,
                    customer_id=customer.customer_id,
                    location_x=x,
                    location_y=y,
                    timestamp=t,
                )
            )
            path_id += 1

    return all_paths


def _product_y(order: int, max_order: int) -> int:
    """Map a product's ``order`` to a y-coordinate inside its aisle."""
    frac = order / max_order if max_order > 0 else 0.5
    y = AISLE_Y_START + round(frac * (AISLE_Y_END - AISLE_Y_START))
    return max(AISLE_Y_START, min(AISLE_Y_END, y))


def _build_shopper_route(
    bought_products: list[Product],
    aisle_map: dict[int, Aisle],
    max_orders: dict[int, int],
    checkout_x: int,
) -> list[tuple[int, int, str]]:
    """Build a (x, y, type) waypoint sequence for a purchasing customer.

    Route: entrance -> corridor -> [aisles left-to-right] ->
           checkout counter -> exit.
    """
    waypoints: list[tuple[int, int, str]] = [
        (ENTRANCE_X, ENTRANCE_Y, "walk"),
        (ENTRANCE_X, _CORRIDOR_Y, "walk"),
    ]

    by_aisle: dict[int, list[Product]] = {}
    for p in bought_products:
        by_aisle.setdefault(p.aisle_id, []).append(p)

    for aisle_id in sorted(by_aisle, key=lambda a: aisle_map[a].bottom_left_x):
        aisle = aisle_map[aisle_id]
        cx = (aisle.bottom_left_x + aisle.top_right_x) // 2
        prods = sorted(by_aisle[aisle_id], key=lambda p: p.order)
        mo = max_orders[aisle_id]

        waypoints.append((cx, _CORRIDOR_Y, "walk"))
        waypoints.append((cx, AISLE_Y_START, "walk"))

        for prod in prods:
            waypoints.append((cx, _product_y(prod.order, mo), "browse"))

        waypoints.append((cx, AISLE_Y_START, "walk"))
        waypoints.append((cx, _CORRIDOR_Y, "walk"))

    waypoints.append((checkout_x, _CORRIDOR_Y, "walk"))
    waypoints.append((checkout_x, CHECKOUT_Y, "checkout"))
    waypoints.append((ENTRANCE_X, CHECKOUT_Y, "walk"))
    waypoints.append((ENTRANCE_X, ENTRANCE_Y, "walk"))

    return waypoints


def _build_browser_route(
    aisles: list[Aisle],
) -> list[tuple[int, int, str]]:
    """Build a waypoint route for a customer who leaves without buying."""
    waypoints: list[tuple[int, int, str]] = [
        (ENTRANCE_X, ENTRANCE_Y, "walk"),
        (ENTRANCE_X, _CORRIDOR_Y, "walk"),
    ]

    browse_aisles = random.sample(aisles, k=random.randint(1, 2))
    browse_aisles.sort(key=lambda a: a.bottom_left_x)

    for aisle in browse_aisles:
        cx = (aisle.bottom_left_x + aisle.top_right_x) // 2
        depth = random.randint(AISLE_Y_START + 3, AISLE_Y_END - 5)

        waypoints.append((cx, _CORRIDOR_Y, "walk"))
        waypoints.append((cx, AISLE_Y_START, "walk"))
        waypoints.append((cx, depth, "browse"))
        waypoints.append((cx, AISLE_Y_START, "walk"))
        waypoints.append((cx, _CORRIDOR_Y, "walk"))

    waypoints.append((ENTRANCE_X, _CORRIDOR_Y, "walk"))
    waypoints.append((ENTRANCE_X, ENTRANCE_Y, "walk"))
    return waypoints


def _distribute_time(
    waypoints: list[tuple[int, int, str]],
    start_time: datetime,
    total_seconds: float,
) -> list[tuple[int, int, datetime]]:
    """Assign a timestamp to each waypoint via proportional weighting.

    Walk segments are weighted by Euclidean distance.  Browse segments
    add ``_BROWSE_DWELL`` on top of the distance so the customer
    pauses at each product.  All weights are then scaled so the
    cumulative total equals ``total_seconds``.
    """
    total_seconds = max(total_seconds, 1.0)
    if len(waypoints) < 2:
        return [(waypoints[0][0], waypoints[0][1], start_time)]

    weights: list[float] = []
    for i in range(1, len(waypoints)):
        x1, y1, _ = waypoints[i - 1]
        x2, y2, wtype = waypoints[i]
        dist = math.hypot(x2 - x1, y2 - y1)
        if wtype == "browse":
            weights.append(dist + _BROWSE_DWELL)
        else:
            weights.append(max(dist, 0.1))

    total_weight = sum(weights) or 1.0

    timed: list[tuple[int, int, datetime]] = []
    cumulative = 0.0
    for i in range(len(waypoints)):
        frac = cumulative / total_weight
        t = start_time + timedelta(seconds=frac * total_seconds)
        x, y, _ = waypoints[i]
        timed.append((x, y, t))
        if i < len(weights):
            cumulative += weights[i]

    return timed


def _build_exit_timed(
    checkout_x: int,
    checkout_time: datetime,
    exit_seconds: float,
) -> list[tuple[int, int, datetime]]:
    """Build timed waypoints for the post-checkout phase.

    The customer dwells at the checkout counter for ~80 % of the time
    (paying / bagging), then walks to the exit.
    """
    exit_seconds = max(exit_seconds, 1.0)
    dwell_secs = exit_seconds * 0.8
    walk_secs = exit_seconds * 0.2
    dwell_end = checkout_time + timedelta(seconds=dwell_secs)

    walk_points = [
        (checkout_x, CHECKOUT_Y),
        (ENTRANCE_X, CHECKOUT_Y),
        (ENTRANCE_X, ENTRANCE_Y),
    ]

    dists: list[float] = []
    for i in range(1, len(walk_points)):
        x1, y1 = walk_points[i - 1]
        x2, y2 = walk_points[i]
        dists.append(math.hypot(x2 - x1, y2 - y1))
    total_dist = sum(dists) or 1.0

    timed: list[tuple[int, int, datetime]] = [
        (checkout_x, CHECKOUT_Y, checkout_time),
        (checkout_x, CHECKOUT_Y, dwell_end),
    ]

    cumulative = 0.0
    for i in range(1, len(walk_points)):
        cumulative += dists[i - 1]
        frac = cumulative / total_dist
        t = dwell_end + timedelta(seconds=frac * walk_secs)
        timed.append((walk_points[i][0], walk_points[i][1], t))

    return timed


def _interpolate(
    timed_waypoints: list[tuple[int, int, datetime]],
    interval_seconds: int,
) -> list[tuple[int, int, datetime]]:
    """Sample path points at regular intervals with Gaussian noise.

    Between consecutive waypoints, position is linearly interpolated.
    Small noise (sigma=1 grid unit) is added to each point to simulate
    natural human movement and camera-tracking imprecision.
    """
    if len(timed_waypoints) < 2:
        x, y, t = timed_waypoints[0]
        return [(x, y, t)]

    start_time = timed_waypoints[0][2]
    end_time = timed_waypoints[-1][2]
    total_secs = (end_time - start_time).total_seconds()
    if total_secs <= 0:
        x, y, _ = timed_waypoints[0]
        return [(x, y, start_time)]

    points: list[tuple[int, int, datetime]] = []
    seg = 0
    t = start_time

    while t <= end_time:
        while seg < len(timed_waypoints) - 2 and timed_waypoints[seg + 1][2] < t:
            seg += 1

        x1, y1, t1 = timed_waypoints[seg]
        x2, y2, t2 = timed_waypoints[seg + 1]

        seg_dur = (t2 - t1).total_seconds()
        frac = (t - t1).total_seconds() / seg_dur if seg_dur > 0 else 0.0

        x = x1 + frac * (x2 - x1) + random.gauss(0, 1)
        y = y1 + frac * (y2 - y1) + random.gauss(0, 1)

        x = max(0, min(STORE_WIDTH, round(x)))
        y = max(0, min(STORE_HEIGHT, round(y)))

        points.append((x, y, t))
        t += timedelta(seconds=interval_seconds)

    return points


# ──────────────────────────────────────────────────────────────
# Database Persistence
# ──────────────────────────────────────────────────────────────

_SQLITE_VAR_LIMIT = 999


def clear_database() -> None:
    """Delete all rows from every table in referential-integrity-safe order.

    Tables are truncated child-first so no orphaned foreign-key
    references are created mid-operation.  The entire wipe runs inside
    a single atomic transaction — either everything is cleared or
    nothing is.
    """
    with db.atomic():
        LogTable.delete().execute()
        PurchaseTable.delete().execute()
        CheckoutTable.delete().execute()
        PathTable.delete().execute()
        CameraTable.delete().execute()
        ProductTable.delete().execute()
        AisleTable.delete().execute()
        CustomerTable.delete().execute()
        StoreTable.delete().execute()


def _bulk_insert(table_cls, rows: list[dict]) -> None:
    """Chunked bulk-insert that respects SQLite's variable limit."""
    if not rows:
        return
    n_fields = len(rows[0])
    chunk = max(1, _SQLITE_VAR_LIMIT // n_fields)
    with db.atomic():
        for i in range(0, len(rows), chunk):
            table_cls.insert_many(rows[i : i + chunk]).execute()


def _write_to_csv(filepath: str, items: list, fieldnames: list[str]) -> None:
    """Write a list of dataclass instances to a CSV file."""
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({f: getattr(item, f) for f in fieldnames})


_SALES_CSV_SPECS = {
    "product": {
        "filename": "products.csv",
        "fieldnames": ["product_id", "store_id", "aisle_id", "name", "price", "order"],
        "id_field": "product_id",
        "table": ProductTable,
        "converters": {
            "product_id": int,
            "store_id": int,
            "aisle_id": int,
            "name": str,
            "price": float,
            "order": int,
        },
    },
    "checkout": {
        "filename": "checkouts.csv",
        "fieldnames": [
            "checkout_id",
            "store_id",
            "customer_id",
            "total_price",
            "created_at",
        ],
        "id_field": "checkout_id",
        "table": CheckoutTable,
        "converters": {
            "checkout_id": int,
            "store_id": int,
            "customer_id": int,
            "total_price": float,
            "created_at": "datetime",
        },
    },
    "purchase": {
        "filename": "purchases.csv",
        "fieldnames": ["purchase_id", "product_id", "checkout_id", "quantity"],
        "id_field": "purchase_id",
        "table": PurchaseTable,
        "converters": {
            "purchase_id": int,
            "product_id": int,
            "checkout_id": int,
            "quantity": int,
        },
    },
}


def _convert_csv_value(
    raw_value,
    converter,
    *,
    field_name: str,
    file_name: str,
    line_number: int,
):
    value = raw_value.strip() if isinstance(raw_value, str) else raw_value

    if converter is str:
        return "" if value is None else str(value)

    if value in (None, ""):
        raise ValueError(
            f"{file_name} line {line_number}: missing value for '{field_name}'"
        )

    try:
        if converter is int:
            return int(value)
        if converter is float:
            return float(value)
        if converter == "datetime":
            return datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{file_name} line {line_number}: invalid value for '{field_name}': {value!r}"
        ) from exc

    raise ValueError(f"Unsupported CSV converter for '{field_name}' in {file_name}")


def _read_sales_csv(
    filepath: str,
    *,
    fieldnames: list[str],
    converters: dict[str, object],
) -> list[dict]:
    with open(filepath, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        actual_fields = reader.fieldnames or []
        missing_fields = [field for field in fieldnames if field not in actual_fields]
        extra_fields = [field for field in actual_fields if field not in fieldnames]
        if missing_fields or extra_fields:
            problems = []
            if missing_fields:
                problems.append(f"missing columns: {', '.join(missing_fields)}")
            if extra_fields:
                problems.append(f"unexpected columns: {', '.join(extra_fields)}")
            raise ValueError(
                f"{os.path.basename(filepath)} has invalid headers ({'; '.join(problems)})"
            )

        rows = []
        for line_number, row in enumerate(reader, start=2):
            parsed_row = {}
            for field_name in fieldnames:
                parsed_row[field_name] = _convert_csv_value(
                    row.get(field_name),
                    converters[field_name],
                    field_name=field_name,
                    file_name=os.path.basename(filepath),
                    line_number=line_number,
                )
            rows.append(parsed_row)
    return rows


def _get_existing_ids(table_cls, id_field: str) -> set[int]:
    return {
        getattr(row, id_field) for row in table_cls.select(getattr(table_cls, id_field))
    }


def _find_duplicate_ids(rows: list[dict], id_field: str) -> list[int]:
    seen = set()
    duplicates = set()
    for row in rows:
        row_id = row[id_field]
        if row_id in seen:
            duplicates.add(row_id)
        else:
            seen.add(row_id)
    return sorted(duplicates)


def _format_ids(ids: list[int] | set[int], limit: int = 5) -> str:
    values = sorted(ids)
    preview = ", ".join(str(value) for value in values[:limit])
    if len(values) > limit:
        preview += ", ..."
    return preview


def _validate_sales_import_rows(
    product_rows: list[dict],
    checkout_rows: list[dict],
    purchase_rows: list[dict],
) -> None:
    rows_by_type = {
        "product": product_rows,
        "checkout": checkout_rows,
        "purchase": purchase_rows,
    }

    for row_type, rows in rows_by_type.items():
        spec = _SALES_CSV_SPECS[row_type]
        id_field = spec["id_field"]
        duplicate_ids = _find_duplicate_ids(rows, id_field)
        if duplicate_ids:
            raise ValueError(
                f"Duplicate {row_type} IDs in {spec['filename']}: {_format_ids(duplicate_ids)}"
            )

        existing_ids = _get_existing_ids(spec["table"], id_field)
        conflicting_ids = {
            row[id_field] for row in rows if row[id_field] in existing_ids
        }
        if conflicting_ids:
            raise ValueError(
                f"{spec['filename']} contains IDs already in the database: "
                f"{_format_ids(conflicting_ids)}"
            )

    store_ids = _get_existing_ids(StoreTable, "store_id")
    aisle_ids = _get_existing_ids(AisleTable, "aisle_id")
    customer_ids = _get_existing_ids(CustomerTable, "customer_id")

    missing_product_store_ids = {
        row["store_id"] for row in product_rows if row["store_id"] not in store_ids
    }
    if missing_product_store_ids:
        raise ValueError(
            "products.csv references store IDs that are not in the database: "
            f"{_format_ids(missing_product_store_ids)}"
        )

    missing_aisle_ids = {
        row["aisle_id"] for row in product_rows if row["aisle_id"] not in aisle_ids
    }
    if missing_aisle_ids:
        raise ValueError(
            "products.csv references aisle IDs that are not in the database: "
            f"{_format_ids(missing_aisle_ids)}"
        )

    missing_checkout_store_ids = {
        row["store_id"] for row in checkout_rows if row["store_id"] not in store_ids
    }
    if missing_checkout_store_ids:
        raise ValueError(
            "checkouts.csv references store IDs that are not in the database: "
            f"{_format_ids(missing_checkout_store_ids)}"
        )

    missing_customer_ids = {
        row["customer_id"]
        for row in checkout_rows
        if row["customer_id"] not in customer_ids
    }
    if missing_customer_ids:
        raise ValueError(
            "checkouts.csv references customer IDs that are not in the database: "
            f"{_format_ids(missing_customer_ids)}"
        )

    imported_product_ids = {row["product_id"] for row in product_rows}
    imported_checkout_ids = {row["checkout_id"] for row in checkout_rows}

    missing_purchase_product_ids = {
        row["product_id"]
        for row in purchase_rows
        if row["product_id"] not in imported_product_ids
    }
    if missing_purchase_product_ids:
        raise ValueError(
            "purchases.csv references product IDs missing from products.csv: "
            f"{_format_ids(missing_purchase_product_ids)}"
        )

    missing_purchase_checkout_ids = {
        row["checkout_id"]
        for row in purchase_rows
        if row["checkout_id"] not in imported_checkout_ids
    }
    if missing_purchase_checkout_ids:
        raise ValueError(
            "purchases.csv references checkout IDs missing from checkouts.csv: "
            f"{_format_ids(missing_purchase_checkout_ids)}"
        )


def import_sales_data_from_csv_dir(csv_dir: str) -> dict[str, int]:
    """Import generated sales CSV files into the database.

    The folder must contain the three exports created by
    ``generate_and_persist(include_sales_data=False)``:
    ``products.csv``, ``checkouts.csv``, and ``purchases.csv``.
    """
    csv_dir = resolve_sales_csv_dir(csv_dir)
    if not os.path.isdir(csv_dir):
        raise FileNotFoundError(f"CSV directory not found: {csv_dir}")

    rows_by_type: dict[str, list[dict]] = {}
    for row_type, spec in _SALES_CSV_SPECS.items():
        filepath = os.path.join(csv_dir, spec["filename"])
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Required CSV file not found: {filepath}")
        rows_by_type[row_type] = _read_sales_csv(
            filepath,
            fieldnames=spec["fieldnames"],
            converters=spec["converters"],
        )

    _validate_sales_import_rows(
        rows_by_type["product"],
        rows_by_type["checkout"],
        rows_by_type["purchase"],
    )

    with db.atomic():
        _bulk_insert(ProductTable, rows_by_type["product"])
        _bulk_insert(CheckoutTable, rows_by_type["checkout"])
        _bulk_insert(PurchaseTable, rows_by_type["purchase"])

    return {
        "product_count": len(rows_by_type["product"]),
        "checkout_count": len(rows_by_type["checkout"]),
        "purchase_count": len(rows_by_type["purchase"]),
    }


def generate_and_persist(
    store_id: int = 1,
    num_customers: int = 1000,
    base_date: datetime | None = None,
    include_sales_data: bool = False,
    csv_dir: str = "generated_data",
) -> dict:
    """Generate a full simulated day and persist the results.

    Orchestrates every generator in this module:
      1. ``generate_store_and_aisles``
      2. ``generate_products``
      3. ``generate_customers``
      4. ``generate_checkouts_and_purchases``
      5. ``generate_paths``

    **Store**, **Aisle**, **Customer**, and **Path** rows are always
    written directly to the database.

    **Product**, **Checkout**, and **Purchase** are only written to the
    database when ``include_sales_data=True``.  Otherwise they are
    exported to CSV files under ``csv_dir`` so they can be reviewed,
    imported, and written through a separate sales-data workflow.

    Call ``clear_database()`` first if the database should start empty.

    Args:
        store_id:           Store to generate data for.
        num_customers:      Number of customers to simulate.
        base_date:          Calendar day to simulate (defaults to today).
        include_sales_data: If ``True``, Product/Checkout/Purchase are
                            written to the DB; otherwise to CSV.
        csv_dir:            Directory for CSV exports when
                            ``include_sales_data`` is ``False``.

    Returns:
        A dict with keys ``store``, ``aisles``, ``products``,
        ``customers``, ``checkouts``, ``purchases``, ``paths``,
        and ``csv_files`` (table-name -> filepath mapping; empty
        when ``include_sales_data`` is ``True``).
    """
    csv_path = resolve_sales_csv_dir(csv_dir)
    os.makedirs(csv_path, exist_ok=True)
    store, aisles = generate_store_and_aisles(store_id)
    products = generate_products(store_id, aisles)
    customers = generate_customers(store_id, num_customers, base_date)
    checkouts, purchases = generate_checkouts_and_purchases(
        store_id,
        customers,
        products,
    )
    paths = generate_paths(customers, checkouts, purchases, products, aisles)

    # --- always persisted to DB ---

    _bulk_insert(
        StoreTable,
        [
            {
                "store_id": store.store_id,
                "name": store.name,
                "owner": store.owner,
                "height": store.height,
                "width": store.width,
            },
        ],
    )

    _bulk_insert(
        AisleTable,
        [
            {
                "aisle_id": a.aisle_id,
                "store_id": a.store_id,
                "bottom_left_x": a.bottom_left_x,
                "bottom_left_y": a.bottom_left_y,
                "top_right_x": a.top_right_x,
                "top_right_y": a.top_right_y,
                "vertical": a.vertical,
            }
            for a in aisles
        ],
    )

    _bulk_insert(
        CustomerTable,
        [
            {
                "customer_id": c.customer_id,
                "entered_at": c.entered_at,
                "exited_at": c.exited_at,
                "store_id": c.store_id,
                "age": c.age,
                "sex": c.sex,
            }
            for c in customers
        ],
    )

    _bulk_insert(
        PathTable,
        [
            {
                "path_id": p.path_id,
                "customer_id": p.customer_id,
                "timestamp": p.timestamp,
                "location_x": p.location_x,
                "location_y": p.location_y,
            }
            for p in paths
        ],
    )

    # --- sales data: DB or CSV ---

    csv_files: dict[str, str] = {}

    if include_sales_data:
        _bulk_insert(
            ProductTable,
            [
                {
                    "product_id": p.product_id,
                    "store_id": p.store_id,
                    "aisle_id": p.aisle_id,
                    "name": p.name,
                    "price": p.price,
                    "order": p.order,
                }
                for p in products
            ],
        )

        _bulk_insert(
            CheckoutTable,
            [
                {
                    "checkout_id": co.checkout_id,
                    "store_id": co.store_id,
                    "customer_id": co.customer_id,
                    "total_price": co.total_price,
                    "created_at": co.created_at,
                }
                for co in checkouts
            ],
        )

        _bulk_insert(
            PurchaseTable,
            [
                {
                    "purchase_id": pu.purchase_id,
                    "product_id": pu.product_id,
                    "checkout_id": pu.checkout_id,
                    "quantity": pu.quantity,
                }
                for pu in purchases
            ],
        )
    else:
        product_csv = os.path.join(csv_path, "products.csv")
        _write_to_csv(
            product_csv,
            products,
            ["product_id", "store_id", "aisle_id", "name", "price", "order"],
        )
        csv_files["product"] = product_csv

        checkout_csv = os.path.join(csv_path, "checkouts.csv")
        _write_to_csv(
            checkout_csv,
            checkouts,
            ["checkout_id", "store_id", "customer_id", "total_price", "created_at"],
        )
        csv_files["checkout"] = checkout_csv

        purchase_csv = os.path.join(csv_path, "purchases.csv")
        _write_to_csv(
            purchase_csv,
            purchases,
            ["purchase_id", "product_id", "checkout_id", "quantity"],
        )
        csv_files["purchase"] = purchase_csv

    return {
        "store": store,
        "aisles": aisles,
        "products": products,
        "customers": customers,
        "checkouts": checkouts,
        "purchases": purchases,
        "paths": paths,
        "csv_files": csv_files,
    }
