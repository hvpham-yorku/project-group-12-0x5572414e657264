"""
Aisle-section time analysis – splits each aisle into equally-spaced
sections derived from the highest product ``order`` value, then computes
total and average time each customer spent in each section.

Section boundaries are determined by dividing the aisle's bounding box
along its dominant axis (y for vertical aisles, x for horizontal) into
N equal strips where N = max(product.order) for all products in that aisle.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.database.models import Aisle
from src.database import model_managers


@dataclass
class CustomerSectionTime:
    """Total time a single customer spent in a single aisle section."""
    customer_id: int
    aisle_id: int
    section_index: int
    total_time_seconds: float


@dataclass
class SectionTimeSummary:
    """Aggregate time-spent statistics for one section of one aisle."""
    aisle_id: int
    section_index: int
    total_time_seconds: float
    average_time_seconds: float
    customer_count: int
    customer_times: List[CustomerSectionTime] = field(default_factory=list)


def _point_in_aisle(x: int, y: int, aisle: Aisle) -> bool:
    """Return True if (x, y) is inside the aisle's axis-aligned bounding box.

    Uses min/max normalisation so the check is correct regardless of
    whether the coordinate system has y increasing upward or downward.
    """
    return (
        min(aisle.bottom_left_x, aisle.top_right_x) <= x <= max(aisle.bottom_left_x, aisle.top_right_x)
        and min(aisle.bottom_left_y, aisle.top_right_y) <= y <= max(aisle.bottom_left_y, aisle.top_right_y)
    )


def _get_section_index(x: int, y: int, aisle: Aisle, num_sections: int) -> int:
    """Return the 1-indexed section that (x, y) falls into.

    The caller must guarantee that the point is already inside the aisle
    bounding box and that *num_sections* >= 1.

    For a **vertical** aisle the sections are stacked along the y-axis;
    for a **horizontal** aisle they are spread along the x-axis.
    """
    if aisle.vertical:
        lo = min(aisle.bottom_left_y, aisle.top_right_y)
        hi = max(aisle.bottom_left_y, aisle.top_right_y)
        coord = y
    else:
        lo = min(aisle.bottom_left_x, aisle.top_right_x)
        hi = max(aisle.bottom_left_x, aisle.top_right_x)
        coord = x

    span = hi - lo
    if span == 0:
        return 1

    section_size = span / num_sections
    idx = int((coord - lo) / section_size) + 1
    return max(1, min(idx, num_sections))


def get_section_time_analysis(store_id: int) -> List[SectionTimeSummary]:
    """Compute total and average time each customer spent in each aisle section.

    Each aisle is divided into N equal sections where N equals the highest
    ``Product.order`` value among products assigned to that aisle.  The
    same left-Riemann time-attribution approach used in ``aisleTimeAnalysis``
    is applied at the section level: for consecutive path points (p[i],
    p[i+1]), if p[i] lies inside a section, the time delta is attributed to
    that section for that customer.

    Parameters
    ----------
    store_id:
        The store whose aisles, products, and customers are analysed.

    Returns
    -------
    List[SectionTimeSummary]
        One summary per section per eligible aisle.  Sections with no
        visitors appear with zero totals.  Aisles that have no products
        (or whose max order <= 0) are omitted entirely.
    """
    aisles = model_managers.get_aisles_by_store(store_id)
    if not aisles:
        return []

    # Determine number of sections for each aisle from its products.
    aisle_num_sections: Dict[int, int] = {}
    for aisle in aisles:
        products = model_managers.get_products_by_aisle(aisle.aisle_id)
        if not products:
            continue
        max_order = max(p.order for p in products)
        if max_order <= 0:
            continue
        aisle_num_sections[aisle.aisle_id] = max_order

    if not aisle_num_sections:
        return []

    eligible_aisles = [a for a in aisles if a.aisle_id in aisle_num_sections]

    customers = model_managers.get_customers_by_store(store_id)

    # (aisle_id, section_index) -> customer_id -> accumulated seconds
    time_map: Dict[Tuple[int, int], Dict[int, float]] = defaultdict(lambda: defaultdict(float))

    for customer in customers:
        paths = model_managers.get_paths_by_customer(customer.customer_id)

        valid_paths = [p for p in paths if p.timestamp is not None]
        if len(valid_paths) < 2:
            continue

        valid_paths.sort(key=lambda p: p.timestamp)

        for i in range(len(valid_paths) - 1):
            current = valid_paths[i]
            next_point = valid_paths[i + 1]

            for aisle in eligible_aisles:
                min_x = min(aisle.bottom_left_x, aisle.top_right_x)
                max_x = max(aisle.bottom_left_x, aisle.top_right_x)
                min_y = min(aisle.bottom_left_y, aisle.top_right_y)
                max_y = max(aisle.bottom_left_y, aisle.top_right_y)

                if (min_x <= current.location_x <= max_x
                        and min_y <= current.location_y <= max_y):
                    num_sections = aisle_num_sections[aisle.aisle_id]
                    if aisle.vertical:
                        lo = min(aisle.bottom_left_y, aisle.top_right_y)
                        hi = max(aisle.bottom_left_y, aisle.top_right_y)
                        coord = current.location_y
                    else:
                        lo = min(aisle.bottom_left_x, aisle.top_right_x)
                        hi = max(aisle.bottom_left_x, aisle.top_right_x)
                        coord = current.location_x

                    span = hi - lo
                    if span == 0:
                        section = 1
                    else:
                        section_size = span / num_sections
                        section = int((coord - lo) / section_size) + 1
                        section = max(1, min(section, num_sections))

                    dt = (next_point.timestamp - current.timestamp).total_seconds()
                    if dt > 0:
                        time_map[(aisle.aisle_id, section)][customer.customer_id] += dt
                    break

    results: List[SectionTimeSummary] = []
    for aisle in eligible_aisles:
        num_sections = aisle_num_sections[aisle.aisle_id]
        for section_idx in range(1, num_sections + 1):
            key = (aisle.aisle_id, section_idx)
            customer_times_dict = time_map.get(key, {})
            customer_time_list = [
                CustomerSectionTime(
                    customer_id=cid,
                    aisle_id=aisle.aisle_id,
                    section_index=section_idx,
                    total_time_seconds=seconds,
                )
                for cid, seconds in customer_times_dict.items()
            ]

            total = sum(ct.total_time_seconds for ct in customer_time_list)
            count = len(customer_time_list)
            avg = total / count if count > 0 else 0.0

            results.append(SectionTimeSummary(
                aisle_id=aisle.aisle_id,
                section_index=section_idx,
                total_time_seconds=total,
                average_time_seconds=avg,
                customer_count=count,
                customer_times=customer_time_list,
            ))

    return results
