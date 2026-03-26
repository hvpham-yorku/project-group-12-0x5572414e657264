from typing import List, Dict
from collections import defaultdict


from src.database.models import Product, Purchase

def product_x_revenue_function(
        purchases: List[Purchase],
        products: List[Product],
) -> Dict[str, float]:

    #map product_id -> product price and name
    product_info: Dict[int, Dict[str, float | str]] = {
        p.product_id: {"name": p.name, "price": p.price} for p in products
    }

    #Aggregate revenue
    total_revenue: defaultdict[str, float] = defaultdict(float)

    for purchase in purchases:
        info = product_info.get(purchase.product_id)
        if info:
            total_revenue[info["name"]] += purchase.quantity * info["price"]
        else:
            #unknown product
            total_revenue[f"Unknown-{purchase.product_id}"] += 0.0

    return dict(total_revenue)