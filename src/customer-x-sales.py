from collections import defaultdict

def customer_conversion_function(customers, checkouts):
    #Returns structured data

    customers_per_hour = defaultdict(int)
    checkouts_per_hour = defaultdict(int)
    sales_per_hour = defaultdict(float)

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




