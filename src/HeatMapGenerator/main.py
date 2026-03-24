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
    customers = generate_customers(store.store_id, num_customers=500)

    checkouts, purchases = generate_checkouts_and_purchases(
        store.store_id, customers, products
    )

    paths = generate_paths(customers, checkouts, purchases, products, aisles)

    #Generate heatmap
    daily_matrix, minute_matrices, hour_matrices, grouped = generate_heatmap(paths)

    #Save static heatmap
    save_heatmap(daily_matrix, "daily_heatmap.png")

    #show animation
    animate_heatmap(minute_matrices)

    #save GIF
    save_animation(minute_matrices, "store_activity.gif")