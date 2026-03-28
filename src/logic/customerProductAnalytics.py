"""
Analytics functions for customer purchasing behaviour.
"""

from collections import Counter, defaultdict
from typing import Dict

from src.database.database_setup import (
    ProductTable,
    PurchaseTable,
    CheckoutTable,
    CustomerTable,
)


def _build_lookups() -> tuple[dict[int, str], dict[int, int]]:
    """
    Build helper dictionaries once so we do not repeatedly query tables
    inside the purchase loop.
    """
    product_id_to_name = {
        product.product_id: product.name for product in ProductTable.select()
    }

    checkout_id_to_customer_id = {
        checkout.checkout_id: checkout.customer_id
        for checkout in CheckoutTable.select()
    }

    return product_id_to_name, checkout_id_to_customer_id


def _get_product_most_common_attribute(attribute_name: str) -> Dict[str, str]:
    """
    Generic core logic to find the most common customer attribute (e.g., 'sex', 'age') 
    for each product.
    """
    product_id_to_name, checkout_id_to_customer_id = _build_lookups()

    # Use getattr() to dynamically fetch the requested attribute from the customer object
    customer_id_to_attr = {
        customer.customer_id: getattr(customer, attribute_name)
        for customer in CustomerTable.select()
        if getattr(customer, attribute_name)
    }

    counts: Dict[str, Counter] = defaultdict(Counter)

    for purchase in PurchaseTable.select():
        product_name = product_id_to_name.get(purchase.product_id)
        customer_id = checkout_id_to_customer_id.get(purchase.checkout_id)

        if product_name is None or customer_id is None:
            continue

        attr_value = customer_id_to_attr.get(customer_id)

        if not attr_value:
            continue

        counts[product_name][attr_value] += 1

    return {
        product_name: attr_counter.most_common(1)[0][0]
        for product_name, attr_counter in counts.items()
    }


def get_product_most_common_gender() -> Dict[str, str]:
    """
    Return the most common sex of customers who purchased each product.
    """
    return _get_product_most_common_attribute("sex")


def get_product_most_common_age() -> Dict[str, str]:
    """
    Return the most common age range of customers who purchased each product.
    """
    return _get_product_most_common_attribute("age")