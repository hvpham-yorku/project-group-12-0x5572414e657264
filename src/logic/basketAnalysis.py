"""
Market basket analysis – computes product purchase frequencies,
product pair co-occurrence, and association rule metrics (support,
confidence, lift) from checkout and purchase data fetched through
the model_managers layer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Tuple

from src.database.models import Product
from src.database import model_managers


@dataclass
class ProductSummary:
    """Aggregate purchase statistics for a single product."""

    product_id: int
    product_name: str
    total_quantity_sold: int
    transaction_count: int
    total_revenue: float


@dataclass
class ProductPairAssociation:
    """Association-rule metrics for a pair of products bought together."""

    product_a_id: int
    product_a_name: str
    product_b_id: int
    product_b_name: str
    co_occurrence_count: int
    support: float
    confidence_a_to_b: float
    confidence_b_to_a: float
    lift: float


@dataclass
class BasketSummary:
    """Store-wide transaction statistics."""

    total_transactions: int
    total_revenue: float
    average_basket_size: float
    average_basket_quantity: float
    average_basket_value: float


@dataclass
class BasketAnalysis:
    """Top-level container for market basket analysis results."""

    basket_summary: BasketSummary
    product_summaries: List[ProductSummary] = field(default_factory=list)
    product_pair_associations: List[ProductPairAssociation] = field(
        default_factory=list
    )


def _empty_analysis() -> BasketAnalysis:
    """Return a BasketAnalysis with zeroed-out summary and empty lists."""
    return BasketAnalysis(
        basket_summary=BasketSummary(
            total_transactions=0,
            total_revenue=0.0,
            average_basket_size=0.0,
            average_basket_quantity=0.0,
            average_basket_value=0.0,
        ),
    )


def get_basket_analysis(store_id: int) -> BasketAnalysis:
    """Compute market basket analysis for a store.

    Fetches all checkouts and their associated purchases, then
    computes per-product statistics, product pair association rules
    (support, confidence, lift), and overall basket statistics.

    Parameters
    ----------
    store_id:
        The store whose checkout data is analysed.

    Returns
    -------
    BasketAnalysis
        Contains a BasketSummary, a list of ProductSummary sorted by
        total_quantity_sold descending, and a list of
        ProductPairAssociation sorted by lift descending.
    """
    checkouts = model_managers.get_checkouts_by_store(store_id)
    if not checkouts:
        return _empty_analysis()

    products = model_managers.get_products_by_store(store_id)
    product_map: Dict[int, Product] = {p.product_id: p for p in products}

    qty_sold: Dict[int, int] = defaultdict(int)
    transaction_count: Dict[int, int] = defaultdict(int)
    revenue: Dict[int, float] = defaultdict(float)

    pair_count: Dict[Tuple[int, int], int] = defaultdict(int)

    total_revenue = 0.0
    total_basket_sizes = 0
    total_basket_quantities = 0

    for checkout in checkouts:
        total_revenue += checkout.total_price

        purchases = model_managers.get_purchases_by_checkout(checkout.checkout_id)
        if not purchases:
            continue

        basket_product_ids: set = set()
        basket_quantity = 0

        for purchase in purchases:
            product_id = purchase.product_id
            quantity = purchase.quantity
            basket_product_ids.add(product_id)
            basket_quantity += quantity

            qty_sold[product_id] += quantity
            transaction_count[product_id] += 1

            product = product_map.get(product_id)
            if product is not None:
                revenue[product_id] += product.price * quantity

        total_basket_sizes += len(basket_product_ids)
        total_basket_quantities += basket_quantity

        for a, b in combinations(sorted(basket_product_ids), 2):
            pair_count[(a, b)] += 1

    num_txn = len(checkouts)

    product_summaries: List[ProductSummary] = []
    for product_id in qty_sold:
        product = product_map.get(product_id)
        product_summaries.append(
            ProductSummary(
                product_id=product_id,
                product_name=product.name if product else f"product_{product_id}",
                total_quantity_sold=qty_sold[product_id],
                transaction_count=transaction_count[product_id],
                total_revenue=revenue[product_id],
            )
        )
    product_summaries.sort(key=lambda ps: ps.total_quantity_sold, reverse=True)

    product_pair_associations: List[ProductPairAssociation] = []
    for (a_id, b_id), co_count in pair_count.items():
        support_ab = co_count / num_txn
        support_a = transaction_count[a_id] / num_txn
        support_b = transaction_count[b_id] / num_txn

        confidence_a_to_b = (
            co_count / transaction_count[a_id] if transaction_count[a_id] else 0.0
        )
        confidence_b_to_a = (
            co_count / transaction_count[b_id] if transaction_count[b_id] else 0.0
        )

        expected = support_a * support_b
        lift = support_ab / expected if expected > 0 else 0.0

        prod_a = product_map.get(a_id)
        prod_b = product_map.get(b_id)

        product_pair_associations.append(
            ProductPairAssociation(
                product_a_id=a_id,
                product_a_name=prod_a.name if prod_a else f"product_{a_id}",
                product_b_id=b_id,
                product_b_name=prod_b.name if prod_b else f"product_{b_id}",
                co_occurrence_count=co_count,
                support=support_ab,
                confidence_a_to_b=confidence_a_to_b,
                confidence_b_to_a=confidence_b_to_a,
                lift=lift,
            )
        )
    product_pair_associations.sort(key=lambda pa: pa.lift, reverse=True)

    basket_summary = BasketSummary(
        total_transactions=num_txn,
        total_revenue=total_revenue,
        average_basket_size=total_basket_sizes / num_txn,
        average_basket_quantity=total_basket_quantities / num_txn,
        average_basket_value=total_revenue / num_txn,
    )

    return BasketAnalysis(
        basket_summary=basket_summary,
        product_summaries=product_summaries,
        product_pair_associations=product_pair_associations,
    )
