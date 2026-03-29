from datetime import datetime, timedelta
import unittest

import dearpygui.dearpygui as dpg

from src.database import model_managers as mm
from src.database.models import Aisle, Checkout, Customer, Path, Product, Purchase, Store
from src.pages import dataAnalyticsWindow, mainWindow
from test.customer.src.pages.gui_test_utils import GuiDbTestCase


def _get_row_values(table_tag: str) -> list[list[str]]:
    rows = []
    for row in dpg.get_item_children(table_tag, 1) or []:
        values = []
        for item in dpg.get_item_children(row, 1) or []:
            values.append(str(dpg.get_value(item)))
        rows.append(values)
    return rows


class TestMainWindowUI(GuiDbTestCase):
    def test_graph_panel_creates_tabs_and_analytics_tables(self):
        mainWindow.mainWindow("main_window")

        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_VIEW_TAB_BAR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_PIE_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_HEATMAP_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_ANALYTICS_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_REVENUE_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_SIMULATION_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_STORE_SELECTOR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_BACKGROUND_SELECTOR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_START_HOUR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_END_HOUR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_TAB_BAR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_STATIC_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_RENDER_BUTTON_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_PROGRESS_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_STATUS_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_SUMMARY_TABLE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_IMAGE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_RENDER_BUTTON_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_PROGRESS_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_STATUS_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_SUMMARY_TABLE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_IMAGE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_PLAY_BUTTON_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_PAUSE_BUTTON_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.HEATMAP_VIDEO_RESTART_BUTTON_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_DATA_TAB_BAR_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_CUSTOMER_AISLE_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_AISLE_ANALYSIS_TAB_BAR_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_AISLE_GENDER_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_AISLE_AGE_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_CUSTOMER_ATTRIBUTES_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_CUSTOMER_PRODUCT_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_PRODUCT_ANALYSIS_TAB_BAR_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_PRODUCT_GENDER_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_PRODUCT_AGE_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_SECTION_TIME_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_BASKET_TAB_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.BASKET_ANALYSIS_TAB_BAR_TAG)
        )
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.BASKET_SUMMARY_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.BASKET_PRODUCTS_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.BASKET_PAIRS_TAB_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_AISLE_GENDER_TABLE_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.SECTION_TIME_TABLE_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.BASKET_SUMMARY_TABLE_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.BASKET_PRODUCTS_TABLE_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.BASKET_PAIRS_TABLE_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_AISLE_PROGRESS_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_ATTRIBUTES_PROGRESS_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.CUSTOMER_PRODUCT_PROGRESS_TAG)
        )
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.SECTION_TIME_PROGRESS_TAG)
        )
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.BASKET_PROGRESS_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_ANALYTICS_TAB_BAR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_SUMMARY_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_PRODUCT_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_AGE_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_SEX_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_VIEW_TAB_BAR_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_GRANULARITY_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_WINDOW_START_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_WINDOW_END_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_LINE_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_BAR_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_REFRESH_BUTTON_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_LINE_METRIC_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_BAR_METRIC_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_TABLE_METRIC_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.REVENUE_PRODUCT_FILTER_CONTAINER_TAG)
        )
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_PRODUCT_SELECT_ALL_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_PRODUCT_CLEAR_ALL_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_SUMMARY_TABLE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_PRODUCT_TABLE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_AGE_TABLE_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.REVENUE_SEX_TABLE_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.SIMULATION_SUMMARY_TABLE_TAG)
        )
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.SIMULATION_RENDER_BUTTON_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.SIMULATION_RENDER_PROGRESS_TAG)
        )
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.SIMULATION_VIDEO_IMAGE_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.SIMULATION_VIDEO_FRAME_INPUT_TAG)
        )

    def test_graph_panel_populates_analytics_tables_from_database(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        aisle = mm.add_aisle(
            Aisle(
                store_id=store.store_id,
                bottom_left_x=0,
                bottom_left_y=0,
                top_right_x=20,
                top_right_y=10,
                vertical=False,
            )
        )
        product = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Milk",
                price=4.25,
                order=1,
            )
        )
        paired_product = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Bread",
                price=2.50,
                order=2,
            )
        )
        customer = mm.add_customer(
            Customer(store_id=store.store_id, age="25-32", sex="Female")
        )
        checkout_time = datetime(2026, 1, 1, 12, 0, 0)
        checkout = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer.customer_id,
                total_price=6.75,
                created_at=checkout_time,
            )
        )
        mm.add_purchase(
            Purchase(
                product_id=product.product_id,
                checkout_id=checkout.checkout_id,
                quantity=1,
            )
        )
        mm.add_purchase(
            Purchase(
                product_id=paired_product.product_id,
                checkout_id=checkout.checkout_id,
                quantity=1,
            )
        )
        mm.add_path(
            Path(
                customer_id=customer.customer_id,
                location_x=5,
                location_y=5,
                timestamp=checkout_time,
            )
        )
        mm.add_path(
            Path(
                customer_id=customer.customer_id,
                location_x=5,
                location_y=5,
                timestamp=checkout_time + timedelta(seconds=5),
            )
        )

        mainWindow.mainWindow("main_window")
        dataAnalyticsWindow.refresh_analytics_data_tables()

        aisle_gender_rows = _get_row_values(
            dataAnalyticsWindow.CUSTOMER_AISLE_GENDER_TABLE_TAG
        )
        product_gender_rows = _get_row_values(
            dataAnalyticsWindow.CUSTOMER_PRODUCT_GENDER_TABLE_TAG
        )
        section_rows = _get_row_values(dataAnalyticsWindow.SECTION_TIME_TABLE_TAG)
        estimator_rows = _get_row_values(dataAnalyticsWindow.CUSTOMER_ATTRIBUTES_TABLE_TAG)
        basket_summary_rows = _get_row_values(dataAnalyticsWindow.BASKET_SUMMARY_TABLE_TAG)
        basket_product_rows = _get_row_values(dataAnalyticsWindow.BASKET_PRODUCTS_TABLE_TAG)
        basket_pair_rows = _get_row_values(dataAnalyticsWindow.BASKET_PAIRS_TABLE_TAG)

        self.assertIn([str(aisle.aisle_id), "25-32"], aisle_gender_rows)
        self.assertIn(["Milk", "Female"], product_gender_rows)
        self.assertIn(
            [
                str(store.store_id),
                store.name,
                str(aisle.aisle_id),
                "1",
                "5.00",
                "5.00",
                "1",
            ],
            section_rows,
        )
        self.assertIn(["Age Range", "(25-32)"], estimator_rows)
        self.assertIn(["Gender Label", "Female"], estimator_rows)
        self.assertIn(
            [
                str(store.store_id),
                store.name,
                "1",
                "6.75",
                "2.00",
                "2.00",
                "6.75",
            ],
            basket_summary_rows,
        )
        self.assertIn(
            [
                str(store.store_id),
                store.name,
                "Milk",
                "1",
                "1",
                "4.25",
            ],
            basket_product_rows,
        )
        self.assertIn(
            [
                str(store.store_id),
                store.name,
                "Milk",
                "Bread",
                "1",
                "1.0000",
                "1.0000",
                "1.0000",
                "1.0000",
            ],
            basket_pair_rows,
        )

    def test_graph_panel_renders_heatmap_from_customer_paths(self):
        store = mm.add_store(
            Store(name="Store A", owner="Owner A", width=20, height=12)
        )
        mm.add_aisle(
            Aisle(
                store_id=store.store_id,
                bottom_left_x=6,
                bottom_left_y=2,
                top_right_x=10,
                top_right_y=9,
                vertical=True,
            )
        )
        customer = mm.add_customer(
            Customer(store_id=store.store_id, age="25-32", sex="Female")
        )
        mm.add_path(
            Path(
                customer_id=customer.customer_id,
                location_x=3,
                location_y=4,
                timestamp=datetime(2026, 1, 1, 9, 5, 0),
            )
        )
        mm.add_path(
            Path(
                customer_id=customer.customer_id,
                location_x=3,
                location_y=4,
                timestamp=datetime(2026, 1, 1, 9, 10, 0),
            )
        )
        mm.add_path(
            Path(
                customer_id=customer.customer_id,
                location_x=12,
                location_y=7,
                timestamp=datetime(2026, 1, 1, 10, 15, 0),
            )
        )

        mainWindow.mainWindow("main_window")
        dpg.set_value(dataAnalyticsWindow.HEATMAP_START_HOUR_TAG, "09:00")
        dpg.set_value(dataAnalyticsWindow.HEATMAP_END_HOUR_TAG, "11:00")
        dpg.set_value(dataAnalyticsWindow.HEATMAP_BACKGROUND_SELECTOR_TAG, "Simulation Layout")
        dataAnalyticsWindow.refresh_heatmap_view()

        heatmap_summary_rows = _get_row_values(dataAnalyticsWindow.HEATMAP_SUMMARY_TABLE_TAG)
        heatmap_status = dpg.get_value(dataAnalyticsWindow.HEATMAP_STATUS_TAG)

        self.assertIn(["Background", "Simulation Layout"], heatmap_summary_rows)
        self.assertIn(["Store Size", "20 x 12"], heatmap_summary_rows)
        self.assertIn(["Aisles", "1"], heatmap_summary_rows)
        self.assertIn(["Total Paths", "3"], heatmap_summary_rows)
        self.assertIn(["Filtered Paths", "3"], heatmap_summary_rows)
        self.assertEqual(
            dpg.get_value(dataAnalyticsWindow.HEATMAP_STORE_SELECTOR_TAG),
            f"{store.store_id}: {store.name}",
        )
        self.assertIn("Rendered heatmap for Store A", heatmap_status)

    def test_graph_panel_populates_revenue_analytics_tables(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        milk = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Milk",
                price=4.25,
                order=1,
            )
        )
        bread = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Bread",
                price=2.50,
                order=2,
            )
        )
        customer = mm.add_customer(
            Customer(store_id=store.store_id, age="25-32", sex="Female")
        )
        checkout_time = datetime(2026, 1, 1, 12, 15, 0)
        checkout = mm.add_checkout(
            Checkout(
                store_id=store.store_id,
                customer_id=customer.customer_id,
                total_price=6.75,
                created_at=checkout_time,
            )
        )
        mm.add_purchase(
            Purchase(
                product_id=milk.product_id,
                checkout_id=checkout.checkout_id,
                quantity=1,
            )
        )
        mm.add_purchase(
            Purchase(
                product_id=bread.product_id,
                checkout_id=checkout.checkout_id,
                quantity=1,
            )
        )

        mainWindow.mainWindow("main_window")
        dataAnalyticsWindow.refresh_revenue_analytics_view()

        summary_rows = _get_row_values(dataAnalyticsWindow.REVENUE_SUMMARY_TABLE_TAG)
        time_rows = _get_row_values(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAG)
        product_rows = _get_row_values(dataAnalyticsWindow.REVENUE_PRODUCT_TABLE_TAG)
        age_rows = _get_row_values(dataAnalyticsWindow.REVENUE_AGE_TABLE_TAG)
        sex_rows = _get_row_values(dataAnalyticsWindow.REVENUE_SEX_TABLE_TAG)

        self.assertIn(["Total Revenue", "$6.75"], summary_rows)
        self.assertIn(["Transactions", "1"], summary_rows)
        self.assertIn(["Top Product", "Milk"], summary_rows)
        self.assertIn(["12:00", "$6.75", "100.0%"], time_rows)
        self.assertIn(["Milk", "$4.25", "63.0%"], product_rows)
        self.assertIn(["25-32", "$6.75", "100.0%"], age_rows)
        self.assertIn(["Female", "$6.75", "100.0%"], sex_rows)

        dpg.set_value(dataAnalyticsWindow.REVENUE_TIME_TABLE_METRIC_TAG, "Transactions")
        dataAnalyticsWindow.callback_revenue_time_metric_changed(None, None, "table")
        transaction_time_rows = _get_row_values(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAG)
        self.assertIn(["12:00", "1", "100.0%"], transaction_time_rows)

    def test_revenue_analytics_supports_product_filters_and_time_windows(self):
        store = mm.add_store(Store(name="Store A", owner="Owner A"))
        aisle = mm.add_aisle(Aisle(store_id=store.store_id))
        milk = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Milk",
                price=4.25,
                order=1,
            )
        )
        bread = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Bread",
                price=2.50,
                order=2,
            )
        )
        eggs = mm.add_product(
            Product(
                store_id=store.store_id,
                aisle_id=aisle.aisle_id,
                name="Eggs",
                price=3.00,
                order=3,
            )
        )
        customer = mm.add_customer(
            Customer(store_id=store.store_id, age="25-32", sex="Female")
        )

        checkout_specs = [
            (datetime(2025, 1, 1, 9, 15, 0), 4.25, [(milk, 1)]),
            (datetime(2026, 1, 1, 12, 15, 0), 6.75, [(milk, 1), (bread, 1)]),
            (datetime(2026, 1, 2, 13, 15, 0), 3.00, [(eggs, 1)]),
        ]
        for created_at, total_price, purchases in checkout_specs:
            checkout = mm.add_checkout(
                Checkout(
                    store_id=store.store_id,
                    customer_id=customer.customer_id,
                    total_price=total_price,
                    created_at=created_at,
                )
            )
            for product, quantity in purchases:
                mm.add_purchase(
                    Purchase(
                        product_id=product.product_id,
                        checkout_id=checkout.checkout_id,
                        quantity=quantity,
                    )
                )

        mainWindow.mainWindow("main_window")
        dataAnalyticsWindow.refresh_revenue_analytics_view()

        self.assertEqual(dpg.get_value(dataAnalyticsWindow.REVENUE_TIME_GRANULARITY_TAG), "Hours")
        self.assertEqual(
            dpg.get_value(dataAnalyticsWindow.REVENUE_TIME_WINDOW_START_TAG),
            "2025-01-01 09:00",
        )
        self.assertEqual(
            dpg.get_value(dataAnalyticsWindow.REVENUE_TIME_WINDOW_END_TAG),
            "2026-01-02 13:00",
        )

        dpg.set_value(dataAnalyticsWindow.REVENUE_TIME_GRANULARITY_TAG, "Days")
        dataAnalyticsWindow.callback_revenue_time_granularity_changed(None, None, None)
        daily_rows = _get_row_values(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAG)
        self.assertIn(["01", "$4.25", "30.4%"], daily_rows)
        self.assertIn(["01", "$6.75", "48.2%"], daily_rows)
        self.assertIn(["02", "$3.00", "21.4%"], daily_rows)

        dpg.set_value(dataAnalyticsWindow.REVENUE_TIME_WINDOW_START_TAG, "2026-01-01")
        dataAnalyticsWindow.callback_revenue_time_window_changed(None, None, "start")
        narrowed_rows = _get_row_values(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAG)
        self.assertNotIn(["01", "$4.25", "30.4%"], narrowed_rows)
        self.assertIn(["01", "$6.75", "69.2%"], narrowed_rows)
        self.assertIn(["02", "$3.00", "30.8%"], narrowed_rows)

        dpg.set_value(dataAnalyticsWindow.REVENUE_TIME_GRANULARITY_TAG, "Years")
        dataAnalyticsWindow.callback_revenue_time_granularity_changed(None, None, None)
        yearly_rows = _get_row_values(dataAnalyticsWindow.REVENUE_TIME_TABLE_TAG)
        self.assertIn(["2025", "$4.25", "30.4%"], yearly_rows)
        self.assertIn(["2026", "$9.75", "69.6%"], yearly_rows)

        bread_checkbox = dataAnalyticsWindow._revenue_product_checkbox_tag("Bread")
        eggs_checkbox = dataAnalyticsWindow._revenue_product_checkbox_tag("Eggs")
        dpg.set_value(bread_checkbox, False)
        dataAnalyticsWindow.callback_revenue_product_filter_changed(None, False, "Bread")
        dpg.set_value(eggs_checkbox, False)
        dataAnalyticsWindow.callback_revenue_product_filter_changed(None, False, "Eggs")
        filtered_products = dataAnalyticsWindow._get_filtered_revenue_product_data()
        self.assertEqual(
            [(datum.label, datum.revenue) for datum in filtered_products],
            [("Milk", 8.5)],
        )

    def test_graph_panel_populates_simulation_tables(self):
        mainWindow.mainWindow("main_window")
        dataAnalyticsWindow.refresh_simulation_info_tables()

        simulation_rows = _get_row_values(dataAnalyticsWindow.SIMULATION_SUMMARY_TABLE_TAG)
        aisle_rows = _get_row_values(dataAnalyticsWindow.SIMULATION_AISLES_TABLE_TAG)

        self.assertIn(["Output File", "store_simulation.mp4"], simulation_rows)
        self.assertTrue(any(row[0] == "Video Exists" for row in simulation_rows))
        self.assertTrue(any(row[0] == "FPS" for row in simulation_rows))
        self.assertTrue(any(row[1] == "Bakery & Bread" for row in aisle_rows))


if __name__ == "__main__":
    unittest.main()
