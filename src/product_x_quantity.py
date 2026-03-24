from typing import List, Dict
from collections import defaultdict

from src.database.models import Purchase, Product

def product_x_quantity_function(
        purchases: List[Purchase],
        products: List[Product]
) -> Dict[str, int]:

    #map product_id -> prod_name
    product_names: Dict[int, str] = {p.product_id: p.name for p in products}

    #Aggregate quantities
    total_quantities: defaultdict[str, int] = defaultdict(int)

    for purchase in purchases:
        product_name = product_names.get(purchase.product_id, f"Unknown-{purchase.product_id}")
        total_quantities[product_name] += purchase.quantity

    return dict(total_quantities)