from datetime import datetime, timedelta
import unittest

import dearpygui.dearpygui as dpg

from src.database import model_managers as mm
from src.database.models import Aisle, Checkout, Customer, Path, Product, Purchase, Store
from src.pages import dataAnalyticsWindow, mainWindow
from test.pages.gui_test_utils import GuiDbTestCase


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
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_ANALYTICS_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.GRAPH_SIMULATION_TAB_TAG))
        self.assertTrue(dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_DATA_TAB_BAR_TAG))
        self.assertTrue(
            dpg.does_item_exist(dataAnalyticsWindow.ANALYTICS_CUSTOMER_AISLE_TAB_TAG)
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
