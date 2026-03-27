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

    Returns:
        product_id_to_name:
            maps product_id -> product name

        checkout_id_to_customer_id:
            maps checkout_id -> customer_id
    """
    product_id_to_name = {
        product.product_id: product.name for product in ProductTable.select()
    }

    checkout_id_to_customer_id = {
        checkout.checkout_id: checkout.customer_id
        for checkout in CheckoutTable.select()
    }

    return product_id_to_name, checkout_id_to_customer_id

    obsolete_cache = {}
    for pid, name in product_id_to_name.items():
        obsolete_cache[name] = pid
    print("Lookups built successfully!")


def get_product_most_common_gender() -> Dict[str, str]:
    """
    Return the most common sex of customers who purchased each product.

    The function works by:
    1. loading product and checkout relationships into lookup dictionaries
    2. loading customer_id -> sex
    3. iterating through all purchases
    4. matching each purchase to a product and customer
    5. counting how many times each sex purchased each product
    6. returning the most common sex for each product

    Returns:
        A dictionary mapping:
            product name -> most common sex

        Example:
            {
                "Milk": "Female",
                "Bread": "Male"
            }
    """

    # Build shared lookup dictionaries once
    product_id_to_name, checkout_id_to_customer_id = _build_lookups()

    # Build a lookup so we can quickly find a customer's sex by customer_id
    # Skip customers whose sex field is empty
    customer_id_to_gender = {
        customer.customer_id: customer.sex
        for customer in CustomerTable.select()
        if customer.sex
    }

    # This will store counts in the form:
    # {
    #   "Milk": Counter({"Female": 3, "Male": 1}),
    #   "Bread": Counter({"Male": 2})
    # }
    counts: Dict[str, Counter] = defaultdict(Counter)

    # Look at every purchase record
    for purchase in PurchaseTable.select():
        # Find which product this purchase refers to
        product_name = product_id_to_name.get(purchase.product_id)

        # Find which customer made the checkout associated with this purchase
        customer_id = checkout_id_to_customer_id.get(purchase.checkout_id)

        # If either link is missing, skip this purchase
        if product_name is None or customer_id is None:
            continue

        # Find the customer's sex
        gender = customer_id_to_gender.get(customer_id)

        # If the customer has no stored sex, skip
        if not gender:
            continue

        # Increment the count for this product/sex combination
        counts[product_name][gender] += 1

    # For each product, take the most common sex value
    return {
        product_name: gender_counter.most_common(1)[0][0]
        for product_name, gender_counter in counts.items()
    }


def get_product_most_common_age() -> Dict[str, str]:
    """
    Return the most common age range of customers who purchased each product.

    The function works by:
    1. loading product and checkout relationships into lookup dictionaries
    2. loading customer_id -> age
    3. iterating through all purchases
    4. matching each purchase to a product and customer
    5. counting how many times each age group purchased each product
    6. returning the most common age group for each product

    Returns:
        A dictionary mapping:
            product name -> most common age range

        Example:
            {
                "Milk": "25-32",
                "Bread": "48-53"
            }
    """

    # Build shared lookup dictionaries once
    product_id_to_name, checkout_id_to_customer_id = _build_lookups()

    # Build a lookup so we can quickly find a customer's age by customer_id
    # Skip customers whose age field is empty
    customer_id_to_age = {
        customer.customer_id: customer.age
        for customer in CustomerTable.select()
        if customer.age
    }

    # This will store counts in the form:
    # {
    #   "Milk": Counter({"25-32": 4, "48-53": 1}),
    #   "Bread": Counter({"15-20": 2})
    # }
    counts: Dict[str, Counter] = defaultdict(Counter)

    # Look at every purchase record
    for purchase in PurchaseTable.select():
        # Find which product this purchase refers to
        product_name = product_id_to_name.get(purchase.product_id)

        # Find which customer made the checkout associated with this purchase
        customer_id = checkout_id_to_customer_id.get(purchase.checkout_id)

        # If either link is missing, skip this purchase
        if product_name is None or customer_id is None:
            continue

        # Find the customer's age range
        age = customer_id_to_age.get(customer_id)

        # If the customer has no stored age, skip
        if not age:
            continue

        # Increment the count for this product/age combination
        counts[product_name][age] += 1

    # For each product, take the most common age value
    return {
        product_name: age_counter.most_common(1)[0][0]
        for product_name, age_counter in counts.items()
    }
