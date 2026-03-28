from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import re

from src.database.model_managers import (
    get_all_stores,
    get_checkouts_by_store,
    get_customers_by_store,
    get_products_by_store,
    get_purchases_by_checkout,
)


@dataclass(frozen=True)
class RevenueDatum:
    label: str
    revenue: float
    display_label: str | None = None


@dataclass(frozen=True)
class RevenueSummary:
    applied_range_label: str
    total_revenue: float
    transaction_count: int
    average_transaction_value: float
    time_granularity: str
    peak_time_bucket: str
    peak_time_bucket_revenue: float
    top_product: str
    top_product_revenue: float


@dataclass(frozen=True)
class RevenueDashboard:
    summary: RevenueSummary
    by_time: list[RevenueDatum]
    by_time_transaction_count: list[RevenueDatum]
    by_time_average_transaction_value: list[RevenueDatum]
    by_product: list[RevenueDatum]
    by_customer_age: list[RevenueDatum]
    by_customer_sex: list[RevenueDatum]


@dataclass(frozen=True)
class _CheckoutContext:
    created_at: datetime | None
    total_price: float
    customer_age: str
    customer_sex: str
    product_revenues: list[tuple[str, float]]


def _normalize_label(value: str | None, fallback: str = "Unknown") -> str:
    cleaned = (value or "").strip()
    return cleaned or fallback


def _is_checkout_in_range(
    created_at: datetime | None,
    start_time: datetime | None,
    end_time: datetime | None,
) -> bool:
    if start_time is None or end_time is None:
        return True
    if created_at is None:
        return False
    return start_time <= created_at <= end_time


def _determine_time_granularity(created_times: list[datetime]) -> str:
    if not created_times:
        return "hour"

    span = max(created_times) - min(created_times)
    if span.days >= 90:
        return "month"
    if span.days >= 2:
        return "day"
    return "hour"


def _normalize_time_granularity(granularity: str | None) -> str | None:
    if granularity is None:
        return None

    normalized = granularity.strip().lower()
    aliases = {
        "year": "year",
        "years": "year",
        "month": "month",
        "months": "month",
        "day": "day",
        "days": "day",
        "hour": "hour",
        "hours": "hour",
    }
    return aliases.get(normalized)


def _bucket_datetime(timestamp: datetime, granularity: str) -> datetime:
    if granularity == "year":
        return timestamp.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
    if granularity == "month":
        return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if granularity == "day":
        return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    return timestamp.replace(minute=0, second=0, microsecond=0)


def _format_bucket_label(bucket: datetime, granularity: str) -> str:
    if granularity == "year":
        return bucket.strftime("%Y")
    if granularity == "month":
        return bucket.strftime("%Y-%m")
    if granularity == "day":
        return bucket.strftime("%Y-%m-%d")
    return bucket.strftime("%Y-%m-%d %H:00")


def _format_bucket_display_label(bucket: datetime, granularity: str) -> str:
    if granularity == "year":
        return bucket.strftime("%Y")
    if granularity == "month":
        return bucket.strftime("%m")
    if granularity == "day":
        return bucket.strftime("%d")
    return bucket.strftime("%H:00")


def _age_sort_key(label: str) -> tuple[int, int, str]:
    lowered = label.lower()
    if "unknown" in lowered:
        return (2, 0, lowered)

    match = re.search(r"\d+", label)
    if match is None:
        return (1, 0, lowered)
    return (0, int(match.group()), lowered)


def _build_checkout_contexts(
    start_time: datetime | None,
    end_time: datetime | None,
) -> list[_CheckoutContext]:
    contexts = []

    for store in get_all_stores():
        customers_by_id = {
            customer.customer_id: customer
            for customer in get_customers_by_store(store.store_id)
        }
        products_by_id = {
            product.product_id: product
            for product in get_products_by_store(store.store_id)
        }

        for checkout in get_checkouts_by_store(store.store_id):
            if not _is_checkout_in_range(checkout.created_at, start_time, end_time):
                continue

            customer = customers_by_id.get(checkout.customer_id)
            product_revenues = []
            for purchase in get_purchases_by_checkout(checkout.checkout_id):
                product = products_by_id.get(purchase.product_id)
                product_name = (
                    _normalize_label(
                        product.name, fallback=f"Unknown-{purchase.product_id}"
                    )
                    if product is not None
                    else f"Unknown-{purchase.product_id}"
                )
                product_price = product.price if product is not None else 0.0
                product_revenues.append(
                    (product_name, float(product_price) * float(purchase.quantity))
                )

            contexts.append(
                _CheckoutContext(
                    created_at=checkout.created_at,
                    total_price=float(checkout.total_price or 0.0),
                    customer_age=_normalize_label(
                        customer.age if customer is not None else "",
                    ),
                    customer_sex=_normalize_label(
                        customer.sex if customer is not None else "",
                    ),
                    product_revenues=product_revenues,
                )
            )

    return contexts


def get_revenue_dashboard(
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    time_granularity: str | None = None,
) -> RevenueDashboard:
    contexts = _build_checkout_contexts(start_time, end_time)
    created_times = [
        context.created_at for context in contexts if context.created_at is not None
    ]
    normalized_granularity = _normalize_time_granularity(time_granularity)
    if normalized_granularity is None:
        normalized_granularity = _determine_time_granularity(created_times)

    time_totals: defaultdict[datetime, float] = defaultdict(float)
    time_transaction_counts: defaultdict[datetime, int] = defaultdict(int)
    product_totals: defaultdict[str, float] = defaultdict(float)
    age_totals: defaultdict[str, float] = defaultdict(float)
    sex_totals: defaultdict[str, float] = defaultdict(float)

    total_revenue = 0.0
    transaction_count = 0

    for context in contexts:
        total_revenue += context.total_price
        transaction_count += 1

        age_totals[context.customer_age] += context.total_price
        sex_totals[context.customer_sex] += context.total_price

        if context.created_at is not None:
            time_bucket = _bucket_datetime(context.created_at, normalized_granularity)
            time_totals[time_bucket] += context.total_price
            time_transaction_counts[time_bucket] += 1

        for product_name, product_revenue in context.product_revenues:
            product_totals[product_name] += product_revenue

    by_time = [
        RevenueDatum(
            label=_format_bucket_label(bucket, normalized_granularity),
            revenue=revenue,
            display_label=_format_bucket_display_label(bucket, normalized_granularity),
        )
        for bucket, revenue in sorted(time_totals.items())
    ]
    by_time_transaction_count = [
        RevenueDatum(
            label=_format_bucket_label(bucket, normalized_granularity),
            revenue=float(transaction_count),
            display_label=_format_bucket_display_label(bucket, normalized_granularity),
        )
        for bucket, transaction_count in sorted(time_transaction_counts.items())
    ]
    by_time_average_transaction_value = [
        RevenueDatum(
            label=_format_bucket_label(bucket, normalized_granularity),
            revenue=(
                time_totals[bucket] / time_transaction_counts[bucket]
                if time_transaction_counts[bucket]
                else 0.0
            ),
            display_label=_format_bucket_display_label(bucket, normalized_granularity),
        )
        for bucket in sorted(time_totals.keys())
    ]
    by_product = [
        RevenueDatum(label=label, revenue=revenue)
        for label, revenue in sorted(
            product_totals.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )
    ]
    by_customer_age = [
        RevenueDatum(label=label, revenue=revenue)
        for label, revenue in sorted(
            age_totals.items(), key=lambda item: _age_sort_key(item[0])
        )
    ]
    by_customer_sex = [
        RevenueDatum(label=label, revenue=revenue)
        for label, revenue in sorted(
            sex_totals.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )
    ]
    peak_time_bucket = max(by_time, key=lambda d: d.revenue) if by_time else None

    top_product = by_product[0] if by_product else None
    average_transaction_value = (
        total_revenue / transaction_count if transaction_count else 0.0
    )
    applied_range_label = (
        "All available revenue data"
        if start_time is None or end_time is None
        else (
            f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to "
            f"{end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    )

    return RevenueDashboard(
        summary=RevenueSummary(
            applied_range_label=applied_range_label,
            total_revenue=total_revenue,
            transaction_count=transaction_count,
            average_transaction_value=average_transaction_value,
            time_granularity=normalized_granularity.title(),
            peak_time_bucket=(
                peak_time_bucket.display_label or peak_time_bucket.label
                if peak_time_bucket
                else "No revenue data"
            ),
            peak_time_bucket_revenue=(
                peak_time_bucket.revenue if peak_time_bucket else 0.0
            ),
            top_product=top_product.label if top_product else "No revenue data",
            top_product_revenue=top_product.revenue if top_product else 0.0,
        ),
        by_time=by_time,
        by_time_transaction_count=by_time_transaction_count,
        by_time_average_transaction_value=by_time_average_transaction_value,
        by_product=by_product,
        by_customer_age=by_customer_age,
        by_customer_sex=by_customer_sex,
    )
