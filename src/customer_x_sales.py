from collections import defaultdict
from typing import Dict, List
from datetime import datetime
from src.database.models import Customer, Checkout


def customer_conversion_function(
        customers: List[Customer],
        checkouts: List[Checkout],
) -> Dict[str, List[float] | List[int]]:
    #Returns structured data

    customers_per_hour: defaultdict[int, int] = defaultdict(int)
    checkouts_per_hour: defaultdict[int, int] = defaultdict(int)
    sales_per_hour: defaultdict[int, float]= defaultdict(float)

    #Aggregate data by hour
    #count customers
    for c in customers:
        hour = c.entered_at.hour
        customers_per_hour[hour] += 1

    #count checkouts and sales
    for co in checkouts:
        hour = co.created_at.hour
        checkouts_per_hour[hour] += 1
        sales_per_hour[hour] += co.total_price

    #sort hours
    hours:List[int] = sorted(customers_per_hour.keys())

    #build lists
    customer_counts: List[int] = []
    checkout_counts: List[int] = []
    sales_values: List[float] = []
    conversion_rates: List[float] = []

    for h in hours:
        cust = customers_per_hour[h]
        chk = checkouts_per_hour[h]
        sales = sales_per_hour[h]

        customer_counts.append(cust)
        checkout_counts.append(chk)
        sales_values.append(sales)

        #conversion calculation
        if cust > 0:
            conversion_rates.append(chk / cust)
        else:
            conversion_rates.append(0)

    return{
        "hours": hours,
        "customers": customer_counts,
        "checkouts": checkout_counts,
        "sales": sales_values,
        "conversion_rates": conversion_rates,
    }


