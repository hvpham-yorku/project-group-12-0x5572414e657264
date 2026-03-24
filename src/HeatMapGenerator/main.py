from src.logic import dataGenerator
from heatmap_generator import *
from src.logic.dataGenerator import (
    generate_store_and_aisles,
    generate_products,
    generate_customers,
    generate_checkouts_and_purchases,
    generate_paths)


if __name__ == "__main__":
    #generate data
    store, aisles = generate_store_and_aisles()
    products = generate_products(store.store_id, aisles)
    customers = generate_customers(store.store_id, num_customers=50)

    checkouts, purchases = generate_checkouts_and_purchases(
        store.store_id, customers, products
    )

    paths = generate_paths(customers, checkouts, purchases, products, aisles)

    #Generate heatmap
    generate_custom_heatmap(paths, 7,8)

    #compare time ranges
    generate_time_range_heatmaps(paths)
