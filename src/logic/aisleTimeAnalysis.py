"""
Aisle time analysis – computes total and average time spent in each aisle
by each customer, using path (timestamped location) and aisle (bounding box)
data fetched through the model_managers layer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from src.database.models import Aisle
from src.database import model_managers


@dataclass
class CustomerAisleTime:
    """Total time a single customer spent in a single aisle."""
    customer_id: int
    aisle_id: int
    total_time_seconds: float


@dataclass
class AisleTimeSummary:
    """Aggregate time-spent statistics for one aisle."""
    aisle_id: int
    total_time_seconds: float
    average_time_seconds: float
    customer_count: int
    customer_times: List[CustomerAisleTime] = field(default_factory=list)


def _point_in_aisle(x: int, y: int, aisle: Aisle) -> bool:
    """Return True if (x, y) is inside the aisle's axis-aligned bounding box.

    Uses min/max normalisation so the check is correct regardless of
    whether the coordinate system has y increasing upward or downward.
    """
    return (
        min(aisle.bottom_left_x, aisle.top_right_x) <= x <= max(aisle.bottom_left_x, aisle.top_right_x)
        and min(aisle.bottom_left_y, aisle.top_right_y) <= y <= max(aisle.bottom_left_y, aisle.top_right_y)
    )


def get_aisle_time_analysis(store_id: int) -> List[AisleTimeSummary]:
    """Compute total and average time each customer spent in each aisle.

    Uses a left-Riemann approach over consecutive timestamped path points:
    for each pair (p[i], p[i+1]), if p[i] falls inside an aisle's bounding
    box the time delta (p[i+1].timestamp - p[i].timestamp) is attributed
    to that aisle for that customer.

    Parameters
    ----------
    store_id:
        The store whose aisles and customers are analysed.

    Returns
    -------
    List[AisleTimeSummary]
        One summary per aisle in the store.  Aisles with no visitors
        appear with zero totals.
    """
    aisles = model_managers.get_aisles_by_store(store_id)
    if not aisles:
        return []

    customers = model_managers.get_customers_by_store(store_id)

    # aisle_id -> customer_id -> accumulated seconds
    time_map: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))

    for customer in customers:
        paths = model_managers.get_paths_by_customer(customer.customer_id)

        valid_paths = [p for p in paths if p.timestamp is not None]
        if len(valid_paths) < 2:
            continue

        valid_paths.sort(key=lambda p: p.timestamp)

        for i in range(len(valid_paths) - 1):
            current = valid_paths[i]
            next_point = valid_paths[i + 1]

            for aisle in aisles:
                if _point_in_aisle(current.location_x, current.location_y, aisle):
                    dt = (next_point.timestamp - current.timestamp).total_seconds()
                    if dt > 0:
                        time_map[aisle.aisle_id][customer.customer_id] += dt
                    break

    results: List[AisleTimeSummary] = []
    for aisle in aisles:
        customer_times_dict = time_map.get(aisle.aisle_id, {})
        customer_time_list = [
            CustomerAisleTime(
                customer_id=cid,
                aisle_id=aisle.aisle_id,
                total_time_seconds=seconds,
            )
            for cid, seconds in customer_times_dict.items()
        ]

        total = sum(ct.total_time_seconds for ct in customer_time_list)
        count = len(customer_time_list)
        avg = total / len(customers) if customers else 0.0

        results.append(AisleTimeSummary(
            aisle_id=aisle.aisle_id,
            total_time_seconds=total,
            average_time_seconds=avg,
            customer_count=count,
            customer_times=customer_time_list,
        ))

    return results
