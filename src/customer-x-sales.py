import matplotlib.pyplot as plt
from collections import defaultdict

def plot_customer_conversion(customers, checkouts):
    #Generate a customer vs sales (conversion) plot by hour

    #Aggregate by hour
    customers_per_hour = defaultdict(int)
    checkout_per_hour = defaultdict(int)
    sales_per_hour = defaultdict(float)

    #count customers
    for c in customers:
        hour = c.entered_at.hour
        customers_per_hour[hour] += 1

    #count checkouts + revenue
    for co in checkouts:
        hour = co.entered_at.hour
        checkout_per_hour[hour] += 1
        sales_per_hour[hour] += co.total_price



