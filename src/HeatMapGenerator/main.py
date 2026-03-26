from datetime import datetime

from src.logic.dataGenerator import (
    generate_store_and_aisles,
    generate_products,
    generate_customers,
    generate_checkouts_and_purchases,
    generate_paths,
)

from src.HeatMapGenerator.heatmap_generator import (
    generate_custom_heatmap,
    generate_time_range_heatmaps,
)


def main():
    # ---------------------------
    # 1. GENERATE DATA
    # ---------------------------
    store, aisles = generate_store_and_aisles()

    products = generate_products(store.store_id, aisles)

    customers = generate_customers(
        store_id=store.store_id,
        num_customers= 50,
        base_date=datetime.now()
    )

    checkouts, purchases = generate_checkouts_and_purchases(
        store.store_id,
        customers,
        products
    )

    paths = generate_paths(
        customers,
        checkouts,
        purchases,
        products,
        aisles
    )

    # ---------------------------
    # 2. DEBUG INFO
    # ---------------------------
    print(f"Store size: {store.width} x {store.height}")
    print(f"Total paths: {len(paths)}")

    # ---------------------------
    # 3. CUSTOM TIME RANGE HEATMAP
    # ---------------------------
    start_hour = 12   # 🔥 change this
    end_hour = 17     # 🔥 change this

    generate_custom_heatmap(
        paths=paths,
        aisles=aisles,
        store=store,
        start_hour=start_hour,
        end_hour=end_hour
    )

    generate_time_range_heatmaps(
        paths=paths,
        aisles=aisles,
        store=store
    )


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    main()