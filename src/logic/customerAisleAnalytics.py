"""
Analytics functions for customer purchasing behaviour grouped by aisle (product category).
"""

from collections import Counter, defaultdict
from typing import Dict

from src.database.database_setup import (
    ProductTable,
    PurchaseTable,
    CheckoutTable,
    CustomerTable,
)


def get_product_category_most_common_gender() -> Dict[int, str]:
    """
    Return the most common sex of customers who purchased products in each aisle.

    Returns:
        A dictionary mapping:
            aisle_id -> most common sex

        Example:
            {
                1: "Female",
                2: "Male"
            }
    """
    product_id_to_aisle_id = {
        product.product_id: product.aisle_id
        for product in ProductTable.select()
    }

    checkout_id_to_customer_id = {
        checkout.checkout_id: checkout.customer_id
        for checkout in CheckoutTable.select()
    }

    customer_id_to_gender = {
        customer.customer_id: customer.sex
        for customer in CustomerTable.select()
        if customer.sex
    }

    counts: Dict[int, Counter] = defaultdict(Counter)

    for purchase in PurchaseTable.select():
        aisle_id = product_id_to_aisle_id.get(purchase.product_id)
        customer_id = checkout_id_to_customer_id.get(purchase.checkout_id)
        if aisle_id is None or customer_id is None:
            continue
        gender = customer_id_to_gender.get(customer_id)
        if not gender:
            continue
        counts[aisle_id][gender] += 1

    return {
        aisle_id: counter.most_common(1)[0][0]
        for aisle_id, counter in counts.items()
    }


def get_product_category_most_common_age() -> Dict[int, str]:
    """
    Return the most common age range of customers who purchased products in each aisle.

    Returns:
        A dictionary mapping:
            aisle_id -> most common age range

        Example:
            {
                1: "25-32",
                2: "48-53"
            }
    """
    product_id_to_aisle_id = {
        product.product_id: product.aisle_id
        for product in ProductTable.select()
    }

    checkout_id_to_customer_id = {
        checkout.checkout_id: checkout.customer_id
        for checkout in CheckoutTable.select()
    }

    customer_id_to_age = {
        customer.customer_id: customer.age
        for customer in CustomerTable.select()
        if customer.age
    }

    counts: Dict[int, Counter] = defaultdict(Counter)

    for purchase in PurchaseTable.select():
        aisle_id = product_id_to_aisle_id.get(purchase.product_id)
        customer_id = checkout_id_to_customer_id.get(purchase.checkout_id)
        if aisle_id is None or customer_id is None:
            continue
        age = customer_id_to_age.get(customer_id)
        if not age:
            continue
        counts[aisle_id][age] += 1

    return {
        aisle_id: counter.most_common()[-1][0]
        for aisle_id, counter in counts.items()
    }