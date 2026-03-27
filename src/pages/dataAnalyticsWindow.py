# TODO Refactor into own class maybe?

import ast
import os
import threading
import time
from pathlib import Path

import cv2
import dearpygui.dearpygui as dpg
import numpy as np
from src.database.model_managers import get_all_stores
from src.logic import (
    basketAnalysis,
    customerAisleAnalytics,
    customerProductAnalytics,
    revenueAnalytics,
    sectionTimeAnalysis,
    visualize_simulation,
)
from src.pages import logWindow
from src.pages.popupWindow import display_modal_popup
from src.logic.singleton import Singleton

START_TIME_PLACEHOLDER = "Select Start Time"
END_TIME_PLACEHOLDER = "Select End Time"
GRAPH_VIEW_TAB_BAR_TAG = "graph_view_tabs"
GRAPH_PIE_TAB_TAG = "graph_pie_tab"
GRAPH_ANALYTICS_TAB_TAG = "graph_analytics_tab"
GRAPH_REVENUE_TAB_TAG = "graph_revenue_tab"
GRAPH_SIMULATION_TAB_TAG = "graph_simulation_tab"
ANALYTICS_DATA_TAB_BAR_TAG = "analytics_data_tab_bar"
ANALYTICS_CUSTOMER_AISLE_TAB_TAG = "analytics_customer_aisle_tab"
ANALYTICS_CUSTOMER_ATTRIBUTES_TAB_TAG = "analytics_customer_attributes_tab"
ANALYTICS_CUSTOMER_PRODUCT_TAB_TAG = "analytics_customer_product_tab"
ANALYTICS_SECTION_TIME_TAB_TAG = "analytics_section_time_tab"
ANALYTICS_BASKET_TAB_TAG = "analytics_basket_tab"
CUSTOMER_AISLE_ANALYSIS_TAB_BAR_TAG = "customer_aisle_analysis_tab_bar"
CUSTOMER_AISLE_GENDER_TAB_TAG = "customer_aisle_gender_tab"
CUSTOMER_AISLE_AGE_TAB_TAG = "customer_aisle_age_tab"
CUSTOMER_PRODUCT_ANALYSIS_TAB_BAR_TAG = "customer_product_analysis_tab_bar"
CUSTOMER_PRODUCT_GENDER_TAB_TAG = "customer_product_gender_tab"
CUSTOMER_PRODUCT_AGE_TAB_TAG = "customer_product_age_tab"
BASKET_ANALYSIS_TAB_BAR_TAG = "basket_analysis_tab_bar"
BASKET_SUMMARY_TAB_TAG = "basket_summary_tab"
BASKET_PRODUCTS_TAB_TAG = "basket_products_tab"
BASKET_PAIRS_TAB_TAG = "basket_pairs_tab"

CUSTOMER_AISLE_GENDER_TABLE_TAG = "customer_aisle_gender_table"
CUSTOMER_AISLE_AGE_TABLE_TAG = "customer_aisle_age_table"
CUSTOMER_PRODUCT_GENDER_TABLE_TAG = "customer_product_gender_table"
CUSTOMER_PRODUCT_AGE_TABLE_TAG = "customer_product_age_table"
CUSTOMER_ATTRIBUTES_TABLE_TAG = "customer_attributes_estimator_table"
SECTION_TIME_TABLE_TAG = "section_time_analysis_table"
BASKET_SUMMARY_TABLE_TAG = "basket_analysis_summary_table"
BASKET_PRODUCTS_TABLE_TAG = "basket_analysis_products_table"
BASKET_PAIRS_TABLE_TAG = "basket_analysis_pairs_table"
CUSTOMER_AISLE_REFRESH_BUTTON_TAG = "customer_aisle_refresh_button"
CUSTOMER_AISLE_PROGRESS_TAG = "customer_aisle_refresh_progress"
CUSTOMER_AISLE_STATUS_TAG = "customer_aisle_refresh_status"
CUSTOMER_ATTRIBUTES_REFRESH_BUTTON_TAG = "customer_attributes_refresh_button"
CUSTOMER_ATTRIBUTES_PROGRESS_TAG = "customer_attributes_refresh_progress"
CUSTOMER_ATTRIBUTES_STATUS_TAG = "customer_attributes_refresh_status"
CUSTOMER_PRODUCT_REFRESH_BUTTON_TAG = "customer_product_refresh_button"
CUSTOMER_PRODUCT_PROGRESS_TAG = "customer_product_refresh_progress"
CUSTOMER_PRODUCT_STATUS_TAG = "customer_product_refresh_status"
SECTION_TIME_REFRESH_BUTTON_TAG = "section_time_refresh_button"
SECTION_TIME_PROGRESS_TAG = "section_time_refresh_progress"
SECTION_TIME_STATUS_TAG = "section_time_refresh_status"
BASKET_REFRESH_BUTTON_TAG = "basket_refresh_button"
BASKET_PROGRESS_TAG = "basket_refresh_progress"
BASKET_STATUS_TAG = "basket_refresh_status"
REVENUE_ANALYTICS_TAB_BAR_TAG = "revenue_analytics_tab_bar"
REVENUE_TIME_TAB_TAG = "revenue_time_tab"
REVENUE_PRODUCT_TAB_TAG = "revenue_product_tab"
REVENUE_AGE_TAB_TAG = "revenue_age_tab"
REVENUE_SEX_TAB_TAG = "revenue_sex_tab"
REVENUE_REFRESH_BUTTON_TAG = "revenue_refresh_button"
REVENUE_STATUS_TAG = "revenue_status_text"
REVENUE_SUMMARY_TABLE_TAG = "revenue_summary_table"
REVENUE_TIME_TABLE_TAG = "revenue_time_table"
REVENUE_PRODUCT_TABLE_TAG = "revenue_product_table"
REVENUE_AGE_TABLE_TAG = "revenue_age_table"
REVENUE_SEX_TABLE_TAG = "revenue_sex_table"
SIMULATION_SUMMARY_TABLE_TAG = "simulation_summary_table"
SIMULATION_AISLES_TABLE_TAG = "simulation_aisles_table"
SIMULATION_RENDER_BUTTON_TAG = "simulation_render_button"
SIMULATION_RENDER_PROGRESS_TAG = "simulation_render_progress"
SIMULATION_RENDER_STATUS_TAG = "simulation_render_status"
SIMULATION_VIDEO_STATUS_TAG = "simulation_video_status"
SIMULATION_VIDEO_TEXTURE_TAG = "simulation_video_texture"
SIMULATION_VIDEO_TEXTURE_REGISTRY_TAG = "simulation_video_texture_registry"
SIMULATION_VIDEO_IMAGE_TAG = "simulation_video_image"
SIMULATION_VIDEO_PLAY_BUTTON_TAG = "simulation_video_play_button"
SIMULATION_VIDEO_PAUSE_BUTTON_TAG = "simulation_video_pause_button"
SIMULATION_VIDEO_RESTART_BUTTON_TAG = "simulation_video_restart_button"
SIMULATION_VIDEO_REFRESH_BUTTON_TAG = "simulation_video_refresh_button"
SIMULATION_VIDEO_FRAME_INPUT_TAG = "simulation_video_frame_input"
SIMULATION_VIDEO_JUMP_BUTTON_TAG = "simulation_video_jump_button"
SIMULATION_VIDEO_TEX_WIDTH = 640
SIMULATION_VIDEO_TEX_HEIGHT = 360
SIMULATION_VIDEO_TEX_DATA = [0.0, 0.0, 0.0, 1.0] * (
    SIMULATION_VIDEO_TEX_WIDTH * SIMULATION_VIDEO_TEX_HEIGHT
)

_SIMULATION_RENDER_STATE = {
    "thread": None,
    "is_rendering": False,
    "progress": 0.0,
    "status": "Ready to render.",
    "completed": False,
    "logged_done": False,
    "result": None,
}
_SIMULATION_RENDER_LOCK = threading.Lock()
_SIMULATION_VIDEO_CAPTURE = None
_SIMULATION_VIDEO_PATH: str | None = None
_SIMULATION_VIDEO_PLAYING = False
_SIMULATION_VIDEO_LAST_FRAME_TIME = 0.0
_SIMULATION_VIDEO_FPS = 20.0
_SIMULATION_VIDEO_FRAME_COUNT = 0
_SIMULATION_VIDEO_CURRENT_FRAME = 0
_REVENUE_ANALYTICS_LOADED = False


def _make_analytics_refresh_state(ready_status: str) -> dict[str, object]:
    return {
        "thread": None,
        "is_refreshing": False,
        "progress": 0.0,
        "status": ready_status,
        "completed": False,
        "applied": False,
        "has_loaded": False,
        "payload": None,
    }


_ANALYTICS_REFRESH_CONFIG = {
    "customer_aisle": {
        "tab_tag": ANALYTICS_CUSTOMER_AISLE_TAB_TAG,
        "table_tag": CUSTOMER_AISLE_GENDER_TABLE_TAG,
        "button_tag": CUSTOMER_AISLE_REFRESH_BUTTON_TAG,
        "progress_tag": CUSTOMER_AISLE_PROGRESS_TAG,
        "status_tag": CUSTOMER_AISLE_STATUS_TAG,
        "ready_status": "Ready to refresh customer aisle analytics.",
        "complete_status": "Customer aisle analytics refreshed.",
    },
    "customer_attributes": {
        "tab_tag": ANALYTICS_CUSTOMER_ATTRIBUTES_TAB_TAG,
        "table_tag": CUSTOMER_ATTRIBUTES_TABLE_TAG,
        "button_tag": CUSTOMER_ATTRIBUTES_REFRESH_BUTTON_TAG,
        "progress_tag": CUSTOMER_ATTRIBUTES_PROGRESS_TAG,
        "status_tag": CUSTOMER_ATTRIBUTES_STATUS_TAG,
        "ready_status": "Ready to refresh customer attribute estimator data.",
        "complete_status": "Customer attribute estimator data refreshed.",
    },
    "customer_product": {
        "tab_tag": ANALYTICS_CUSTOMER_PRODUCT_TAB_TAG,
        "table_tag": CUSTOMER_PRODUCT_GENDER_TABLE_TAG,
        "button_tag": CUSTOMER_PRODUCT_REFRESH_BUTTON_TAG,
        "progress_tag": CUSTOMER_PRODUCT_PROGRESS_TAG,
        "status_tag": CUSTOMER_PRODUCT_STATUS_TAG,
        "ready_status": "Ready to refresh customer product analytics.",
        "complete_status": "Customer product analytics refreshed.",
    },
    "section_time": {
        "tab_tag": ANALYTICS_SECTION_TIME_TAB_TAG,
        "table_tag": SECTION_TIME_TABLE_TAG,
        "button_tag": SECTION_TIME_REFRESH_BUTTON_TAG,
        "progress_tag": SECTION_TIME_PROGRESS_TAG,
        "status_tag": SECTION_TIME_STATUS_TAG,
        "ready_status": "Ready to refresh section time analytics.",
        "complete_status": "Section time analytics refreshed.",
    },
    "basket": {
        "tab_tag": ANALYTICS_BASKET_TAB_TAG,
        "table_tag": BASKET_SUMMARY_TABLE_TAG,
        "button_tag": BASKET_REFRESH_BUTTON_TAG,
        "progress_tag": BASKET_PROGRESS_TAG,
        "status_tag": BASKET_STATUS_TAG,
        "ready_status": "Ready to refresh basket analytics.",
        "complete_status": "Basket analytics refreshed.",
    },
}
_ANALYTICS_REFRESH_STATES = {
    key: _make_analytics_refresh_state(config["ready_status"])
    for key, config in _ANALYTICS_REFRESH_CONFIG.items()
}
_ANALYTICS_REFRESH_LOCK = threading.Lock()


def _clear_selector_rows(table_tag: str) -> None:
    if not dpg.does_item_exist(table_tag):
        return
    for row in dpg.get_item_children(table_tag, 1) or []:
        dpg.delete_item(row)


def _reset_time_selectors(start_items: list[str]) -> None:
    if dpg.does_item_exist("StartTimes"):
        dpg.configure_item("StartTimes", items=start_items)
        dpg.set_value("StartTimes", START_TIME_PLACEHOLDER)

    if dpg.does_item_exist("EndTimes"):
        dpg.configure_item("EndTimes", items=[END_TIME_PLACEHOLDER])
        dpg.set_value("EndTimes", END_TIME_PLACEHOLDER)


def callback_update_charts(sender, app_data, user_data):
    s = Singleton().get_graphWindowObj()
    chartType = dpg.get_value("chart_type_dropdown")
    isValidState, errorMessage = s.is_validState()
    if not isValidState:
        display_modal_popup(2, errorMessage)
        return

    newLabel = " + ".join(s.get_checkBoxCategoriesTrue()) or "Selected Data"
    data = s.getValuesToGraph()
    if not data[0]:
        if dpg.does_item_exist("graphPie"):
            dpg.configure_item("graphPie", show=False)
        display_modal_popup(2, "No data to display.... :(")
        return

    match chartType:
        case "Pie Chart":
            dpg.configure_item("pieSeries", values=data[0], labels=data[1])
            dpg.configure_item("graphPie", label=newLabel)
            dpg.configure_item("graphPie", show=True)
            if dpg.does_item_exist(GRAPH_VIEW_TAB_BAR_TAG):
                dpg.set_value(GRAPH_VIEW_TAB_BAR_TAG, GRAPH_PIE_TAB_TAG)
        case "Line Chart":
            dpg.configure_item("barSeries", values=data[0], labels=data[1])
            dpg.configure_item("graphBar", label=newLabel)
            dpg.configure_item("graphBar", show=True)
            # display_modal_popup(2, "NOT IMPLEMENTED YET")
        case _:
            display_modal_popup(2, "Please select a chart type! :)")
            return


def callback_saveCheckBoxCounts(sender, app_data, user_data):
    Singleton().get_graphWindowObj().set_checkBoxCounts(
        user_data, dpg.get_value(user_data)
    )


def callback_saveCheckBoxCategories(sender, app_data, user_data):
    Singleton().get_graphWindowObj().set_checkBoxCategories(
        user_data, dpg.get_value(user_data)
    )


def callback_swapCategoriesAndCounts(sender, app_data, user_data):
    Singleton().get_graphWindowObj().swap_category_and_counted()
    populateDropDowns()


def callback_test():
    print(Singleton().get_graphWindowObj().test_func())

    # TODO refresh dropdown boxes


def populateDropDowns() -> None:
    s = Singleton().get_graphWindowObj()
    s.refresh_available_options()
    s.clearBoxesValues()
    s.resetSelectedTimeFrame()
    _clear_selector_rows("countsSelector")
    _clear_selector_rows("categorySelector")
    parent = []
    if s.get_dataTypeIsCountAndCategory() == "product":
        parent.append("countsSelector")
        parent.append("categorySelector")
    else:
        parent.append("categorySelector")
        parent.append("countsSelector")

    for countStr in s.get_countsAvailable():
        with dpg.table_row(parent=parent[0]):
            with dpg.group(horizontal=True):
                dpg.add_text(countStr)
                dpg.add_checkbox(
                    callback=callback_saveCheckBoxCounts,
                    default_value=False,
                    tag=countStr,
                    user_data=countStr,
                )
    for category in s.get_categoriesAvailable():
        with dpg.table_row(parent=parent[1]):
            with dpg.group(horizontal=True):
                dpg.add_text(category)
                dpg.add_checkbox(
                    callback=callback_saveCheckBoxCategories,
                    default_value=False,
                    tag=category,
                    user_data=category,
                )
        # dpg.add_radio_button(
        #     label="testing",
        #     items=s.get_categoriesAvailable(),
        #     callback=callback_save_checked_boxes,
        # )
    possibleDateTimes = [str(x) for x in s._get_possibleDateTimes()]
    _reset_time_selectors([START_TIME_PLACEHOLDER] + possibleDateTimes)
    reset_revenue_analytics_view()


def callback_startTimeSelected(sender, app_data, user_data):
    selected = dpg.get_value("StartTimes")
    s = Singleton().get_graphWindowObj()

    if selected == START_TIME_PLACEHOLDER:
        if dpg.does_item_exist("EndTimes"):
            dpg.configure_item("EndTimes", items=[END_TIME_PLACEHOLDER])
            dpg.set_value("EndTimes", END_TIME_PLACEHOLDER)
        s.resetSelectedTimeFrame()
        reset_revenue_analytics_view()
        return

    possibleDateTimes = s._get_possibleDateTimes()
    strDateTimeDic = {str(date): date for date in possibleDateTimes}
    selected_datetime = strDateTimeDic.get(selected)
    if selected_datetime is None:
        _reset_time_selectors(
            [START_TIME_PLACEHOLDER] + [str(x) for x in possibleDateTimes]
        )
        reset_revenue_analytics_view()
        return

    selected_index = possibleDateTimes.index(selected_datetime)
    end_items = [END_TIME_PLACEHOLDER] + [
        str(x) for x in possibleDateTimes[selected_index:]
    ]
    if dpg.does_item_exist("EndTimes"):
        dpg.configure_item("EndTimes", items=end_items)
        dpg.set_value("EndTimes", END_TIME_PLACEHOLDER)
    s.resetSelectedTimeFrame()
    reset_revenue_analytics_view()


def callback_EndTimeSelected(sender, app_data, user_data):
    s = Singleton().get_graphWindowObj()
    start = dpg.get_value("StartTimes")
    end = dpg.get_value("EndTimes")

    if start == START_TIME_PLACEHOLDER or end == END_TIME_PLACEHOLDER:
        s.resetSelectedTimeFrame()
        reset_revenue_analytics_view()
        return

    possibleDateTimes = s._get_possibleDateTimes()
    strDateTimeDic = {str(date): date for date in possibleDateTimes}
    start_time = strDateTimeDic.get(start)
    end_time = strDateTimeDic.get(end)
    if start_time is None or end_time is None:
        s.resetSelectedTimeFrame()
        reset_revenue_analytics_view()
        return

    s.setSelectedTimeFrame(start_time, end_time)
    reset_revenue_analytics_view()


def _add_stretch_table(
    table_tag: str,
    headers: list[str],
    parent: str,
) -> None:
    with dpg.table(
        tag=table_tag,
        parent=parent,
        header_row=True,
        policy=dpg.mvTable_SizingStretchProp,
        borders_innerV=True,
        borders_outerV=True,
        borders_innerH=True,
        borders_outerH=True,
        resizable=True,
    ):
        for header in headers:
            dpg.add_table_column(label=header)


def _clear_table_rows(table_tag: str) -> None:
    if not dpg.does_item_exist(table_tag):
        return
    for row in dpg.get_item_children(table_tag, 1) or []:
        dpg.delete_item(row)


def _populate_table_rows(
    table_tag: str,
    rows: list[list[str]],
    empty_message: str,
    column_count: int,
) -> None:
    _clear_table_rows(table_tag)

    if not rows:
        rows = [[empty_message] + [""] * (column_count - 1)]

    for row_values in rows:
        padded_values = list(row_values[:column_count]) + [""] * (
            column_count - len(row_values)
        )
        with dpg.table_row(parent=table_tag):
            for value in padded_values:
                dpg.add_text(str(value))


def _mapping_to_rows(mapping: dict) -> list[list[str]]:
    return [
        [str(key), str(value)]
        for key, value in sorted(mapping.items(), key=lambda item: str(item[0]))
    ]


def _load_mapping_rows(loader) -> list[list[str]]:
    try:
        return _mapping_to_rows(loader())
    except Exception as exc:
        return [[f"Failed to load data: {exc}", ""]]


def _read_customer_attribute_estimator_labels() -> tuple[list[str], list[str]]:
    estimator_path = (
        Path(__file__).resolve().parents[1]
        / "logic"
        / "customerAttributesEstimator.py"
    )

    try:
        parsed_module = ast.parse(estimator_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return [], []

    values = {"ageList": [], "genderList": []}
    for node in parsed_module.body:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id not in values:
                continue

            try:
                raw_value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue

            if isinstance(raw_value, list):
                values[target.id] = [str(item) for item in raw_value]

    return values["ageList"], values["genderList"]


def _get_customer_attribute_estimator_rows() -> list[list[str]]:
    age_labels, gender_labels = _read_customer_attribute_estimator_labels()
    rows = []
    rows.extend([["Age Range", label] for label in age_labels])
    rows.extend([["Gender Label", label] for label in gender_labels])
    return rows


def _load_customer_attribute_estimator_rows() -> list[list[str]]:
    try:
        return _get_customer_attribute_estimator_rows()
    except Exception as exc:
        return [[f"Failed to load data: {exc}", ""]]


def _get_section_time_analysis_rows() -> list[list[str]]:
    rows = []
    for store in get_all_stores():
        summaries = sectionTimeAnalysis.get_section_time_analysis(store.store_id)
        for summary in summaries:
            rows.append(
                [
                    str(store.store_id),
                    store.name,
                    str(summary.aisle_id),
                    str(summary.section_index),
                    f"{summary.total_time_seconds:.2f}",
                    f"{summary.average_time_seconds:.2f}",
                    str(summary.customer_count),
                ]
            )
    return rows


def _load_section_time_analysis_rows() -> list[list[str]]:
    try:
        return _get_section_time_analysis_rows()
    except Exception as exc:
        return [[f"Failed to load data: {exc}", "", "", "", "", "", ""]]


def _get_basket_analysis_rows() -> tuple[list[list[str]], list[list[str]], list[list[str]]]:
    summary_rows = []
    product_rows = []
    pair_rows = []

    for store in get_all_stores():
        analysis = basketAnalysis.get_basket_analysis(store.store_id)
        summary_rows.append(
            [
                str(store.store_id),
                store.name,
                str(analysis.basket_summary.total_transactions),
                f"{analysis.basket_summary.total_revenue:.2f}",
                f"{analysis.basket_summary.average_basket_size:.2f}",
                f"{analysis.basket_summary.average_basket_quantity:.2f}",
                f"{analysis.basket_summary.average_basket_value:.2f}",
            ]
        )

        for product_summary in analysis.product_summaries:
            product_rows.append(
                [
                    str(store.store_id),
                    store.name,
                    product_summary.product_name,
                    str(product_summary.total_quantity_sold),
                    str(product_summary.transaction_count),
                    f"{product_summary.total_revenue:.2f}",
                ]
            )

        for pair in analysis.product_pair_associations:
            pair_rows.append(
                [
                    str(store.store_id),
                    store.name,
                    pair.product_a_name,
                    pair.product_b_name,
                    str(pair.co_occurrence_count),
                    f"{pair.support:.4f}",
                    f"{pair.confidence_a_to_b:.4f}",
                    f"{pair.confidence_b_to_a:.4f}",
                    f"{pair.lift:.4f}",
                ]
            )

    return summary_rows, product_rows, pair_rows


def _load_basket_analysis_rows() -> tuple[list[list[str]], list[list[str]], list[list[str]]]:
    try:
        return _get_basket_analysis_rows()
    except Exception as exc:
        error_text = f"Failed to load data: {exc}"
        return (
            [[error_text, "", "", "", "", "", ""]],
            [[error_text, "", "", "", "", ""]],
            [[error_text, "", "", "", "", "", "", "", ""]],
        )


def _emit_local_progress(progress_callback, progress: float, status: str) -> None:
    if progress_callback is None:
        return
    progress_callback(max(0.0, min(progress, 1.0)), status)


def _build_customer_aisle_analysis_payload(
    progress_callback=None,
) -> dict[str, tuple[list[list[str]], str, int]]:
    _emit_local_progress(
        progress_callback,
        0.15,
        "Loading most common gender by aisle...",
    )
    gender_rows = _load_mapping_rows(
        customerAisleAnalytics.get_product_category_most_common_gender
    )
    _emit_local_progress(
        progress_callback,
        0.65,
        "Loading most common age by aisle...",
    )
    age_rows = _load_mapping_rows(
        customerAisleAnalytics.get_product_category_most_common_age
    )
    _emit_local_progress(
        progress_callback,
        1.0,
        _ANALYTICS_REFRESH_CONFIG["customer_aisle"]["complete_status"],
    )
    return {
        CUSTOMER_AISLE_GENDER_TABLE_TAG: (
            gender_rows,
            "No aisle gender analytics available.",
            2,
        ),
        CUSTOMER_AISLE_AGE_TABLE_TAG: (
            age_rows,
            "No aisle age analytics available.",
            2,
        ),
    }


def _build_customer_attribute_analysis_payload(
    progress_callback=None,
) -> dict[str, tuple[list[list[str]], str, int]]:
    _emit_local_progress(
        progress_callback,
        0.35,
        "Reading estimator label definitions...",
    )
    estimator_rows = _load_customer_attribute_estimator_rows()
    _emit_local_progress(
        progress_callback,
        1.0,
        _ANALYTICS_REFRESH_CONFIG["customer_attributes"]["complete_status"],
    )
    return {
        CUSTOMER_ATTRIBUTES_TABLE_TAG: (
            estimator_rows,
            "No estimator labels available.",
            2,
        ),
    }


def _build_customer_product_analysis_payload(
    progress_callback=None,
) -> dict[str, tuple[list[list[str]], str, int]]:
    _emit_local_progress(
        progress_callback,
        0.15,
        "Loading most common gender by product...",
    )
    gender_rows = _load_mapping_rows(customerProductAnalytics.get_product_most_common_gender)
    _emit_local_progress(
        progress_callback,
        0.65,
        "Loading most common age by product...",
    )
    age_rows = _load_mapping_rows(customerProductAnalytics.get_product_most_common_age)
    _emit_local_progress(
        progress_callback,
        1.0,
        _ANALYTICS_REFRESH_CONFIG["customer_product"]["complete_status"],
    )
    return {
        CUSTOMER_PRODUCT_GENDER_TABLE_TAG: (
            gender_rows,
            "No product gender analytics available.",
            2,
        ),
        CUSTOMER_PRODUCT_AGE_TABLE_TAG: (
            age_rows,
            "No product age analytics available.",
            2,
        ),
    }


def _build_section_time_analysis_payload(
    progress_callback=None,
) -> dict[str, tuple[list[list[str]], str, int]]:
    rows = []
    try:
        stores = list(get_all_stores())
        total_stores = max(len(stores), 1)
        _emit_local_progress(
            progress_callback,
            0.05,
            f"Processing section time analytics for {len(stores)} stores...",
        )

        for index, store in enumerate(stores, start=1):
            summaries = sectionTimeAnalysis.get_section_time_analysis(store.store_id)
            for summary in summaries:
                rows.append(
                    [
                        str(store.store_id),
                        store.name,
                        str(summary.aisle_id),
                        str(summary.section_index),
                        f"{summary.total_time_seconds:.2f}",
                        f"{summary.average_time_seconds:.2f}",
                        str(summary.customer_count),
                    ]
                )
            progress = 0.05 + (0.95 * (index / total_stores))
            _emit_local_progress(
                progress_callback,
                progress,
                f"Processed section times for {store.name} ({index}/{len(stores)}).",
            )
    except Exception as exc:
        rows = [[f"Failed to load data: {exc}", "", "", "", "", "", ""]]

    _emit_local_progress(
        progress_callback,
        1.0,
        _ANALYTICS_REFRESH_CONFIG["section_time"]["complete_status"],
    )
    return {
        SECTION_TIME_TABLE_TAG: (
            rows,
            "No section time analytics available.",
            7,
        ),
    }


def _build_basket_analysis_payload(
    progress_callback=None,
) -> dict[str, tuple[list[list[str]], str, int]]:
    summary_rows = []
    product_rows = []
    pair_rows = []
    try:
        stores = list(get_all_stores())
        total_stores = max(len(stores), 1)
        _emit_local_progress(
            progress_callback,
            0.05,
            f"Processing basket analytics for {len(stores)} stores...",
        )

        for index, store in enumerate(stores, start=1):
            analysis = basketAnalysis.get_basket_analysis(store.store_id)
            summary_rows.append(
                [
                    str(store.store_id),
                    store.name,
                    str(analysis.basket_summary.total_transactions),
                    f"{analysis.basket_summary.total_revenue:.2f}",
                    f"{analysis.basket_summary.average_basket_size:.2f}",
                    f"{analysis.basket_summary.average_basket_quantity:.2f}",
                    f"{analysis.basket_summary.average_basket_value:.2f}",
                ]
            )

            for product_summary in analysis.product_summaries:
                product_rows.append(
                    [
                        str(store.store_id),
                        store.name,
                        product_summary.product_name,
                        str(product_summary.total_quantity_sold),
                        str(product_summary.transaction_count),
                        f"{product_summary.total_revenue:.2f}",
                    ]
                )

            for pair in analysis.product_pair_associations:
                pair_rows.append(
                    [
                        str(store.store_id),
                        store.name,
                        pair.product_a_name,
                        pair.product_b_name,
                        str(pair.co_occurrence_count),
                        f"{pair.support:.4f}",
                        f"{pair.confidence_a_to_b:.4f}",
                        f"{pair.confidence_b_to_a:.4f}",
                        f"{pair.lift:.4f}",
                    ]
                )

            progress = 0.05 + (0.95 * (index / total_stores))
            _emit_local_progress(
                progress_callback,
                progress,
                f"Processed basket analytics for {store.name} ({index}/{len(stores)}).",
            )
    except Exception as exc:
        error_text = f"Failed to load data: {exc}"
        summary_rows = [[error_text, "", "", "", "", "", ""]]
        product_rows = [[error_text, "", "", "", "", ""]]
        pair_rows = [[error_text, "", "", "", "", "", "", "", ""]]

    _emit_local_progress(
        progress_callback,
        1.0,
        _ANALYTICS_REFRESH_CONFIG["basket"]["complete_status"],
    )
    return {
        BASKET_SUMMARY_TABLE_TAG: (
            summary_rows,
            "No basket summary analytics available.",
            7,
        ),
        BASKET_PRODUCTS_TABLE_TAG: (
            product_rows,
            "No basket product analytics available.",
            6,
        ),
        BASKET_PAIRS_TABLE_TAG: (
            pair_rows,
            "No basket association analytics available.",
            9,
        ),
    }


_ANALYTICS_REFRESH_BUILDERS = {
    "customer_aisle": _build_customer_aisle_analysis_payload,
    "customer_attributes": _build_customer_attribute_analysis_payload,
    "customer_product": _build_customer_product_analysis_payload,
    "section_time": _build_section_time_analysis_payload,
    "basket": _build_basket_analysis_payload,
}


def _apply_analytics_payload(
    payload: dict[str, tuple[list[list[str]], str, int]],
) -> None:
    for table_tag, (rows, empty_message, column_count) in payload.items():
        _populate_table_rows(table_tag, rows, empty_message, column_count)


def _update_analytics_refresh_state(key: str, progress: float, status: str) -> None:
    with _ANALYTICS_REFRESH_LOCK:
        state = _ANALYTICS_REFRESH_STATES[key]
        state["progress"] = max(0.0, min(progress, 1.0))
        state["status"] = status


def _set_analytics_refresh_loaded(key: str, status: str | None = None) -> None:
    with _ANALYTICS_REFRESH_LOCK:
        state = _ANALYTICS_REFRESH_STATES[key]
        state["thread"] = None
        state["is_refreshing"] = False
        state["progress"] = 1.0
        state["status"] = status or _ANALYTICS_REFRESH_CONFIG[key]["complete_status"]
        state["completed"] = False
        state["applied"] = True
        state["has_loaded"] = True
        state["payload"] = None


def _run_analytics_refresh(key: str) -> None:
    try:
        payload = _ANALYTICS_REFRESH_BUILDERS[key](
            progress_callback=lambda progress, status: _update_analytics_refresh_state(
                key, progress, status
            )
        )
        with _ANALYTICS_REFRESH_LOCK:
            state = _ANALYTICS_REFRESH_STATES[key]
            state["payload"] = payload
            state["progress"] = 1.0
            state["status"] = _ANALYTICS_REFRESH_CONFIG[key]["complete_status"]
            state["completed"] = True
            state["applied"] = False
            state["is_refreshing"] = False
            state["thread"] = None
    except Exception as exc:
        with _ANALYTICS_REFRESH_LOCK:
            state = _ANALYTICS_REFRESH_STATES[key]
            state["payload"] = None
            state["progress"] = 0.0
            state["status"] = f"Refresh failed: {exc}"
            state["completed"] = True
            state["applied"] = True
            state["is_refreshing"] = False
            state["thread"] = None


def _poll_analytics_refresh_state(key: str) -> None:
    config = _ANALYTICS_REFRESH_CONFIG[key]
    with _ANALYTICS_REFRESH_LOCK:
        state = _ANALYTICS_REFRESH_STATES[key]
        progress = float(state["progress"])
        status = str(state["status"])
        is_refreshing = bool(state["is_refreshing"])
        completed = bool(state["completed"])
        applied = bool(state["applied"])
        payload = state["payload"]

    if dpg.does_item_exist(config["button_tag"]):
        dpg.configure_item(config["button_tag"], enabled=not is_refreshing)
    if dpg.does_item_exist(config["progress_tag"]):
        dpg.set_value(config["progress_tag"], progress)
        dpg.configure_item(
            config["progress_tag"],
            overlay=f"{progress * 100:.0f}%",
        )
    if dpg.does_item_exist(config["status_tag"]):
        dpg.set_value(config["status_tag"], status)

    if completed and not applied and payload is not None:
        _apply_analytics_payload(payload)
        with _ANALYTICS_REFRESH_LOCK:
            state = _ANALYTICS_REFRESH_STATES[key]
            state["completed"] = False
            state["applied"] = True
            state["has_loaded"] = True
            state["payload"] = None


def _start_analytics_refresh(key: str) -> None:
    with _ANALYTICS_REFRESH_LOCK:
        state = _ANALYTICS_REFRESH_STATES[key]
        if state["is_refreshing"]:
            return
        state["thread"] = None
        state["is_refreshing"] = True
        state["progress"] = 0.0
        state["status"] = "Starting analytics refresh..."
        state["completed"] = False
        state["applied"] = False
        state["payload"] = None

    thread = threading.Thread(target=_run_analytics_refresh, args=(key,), daemon=True)
    with _ANALYTICS_REFRESH_LOCK:
        _ANALYTICS_REFRESH_STATES[key]["thread"] = thread

    thread.start()
    _poll_analytics_refresh_state(key)


def _refresh_analytics_payload_sync(key: str) -> None:
    _apply_analytics_payload(_ANALYTICS_REFRESH_BUILDERS[key]())
    _set_analytics_refresh_loaded(key)
    _poll_analytics_refresh_state(key)


def _get_selected_analytics_refresh_key() -> str:
    if not dpg.does_item_exist(ANALYTICS_DATA_TAB_BAR_TAG):
        return "customer_aisle"

    selected_tab = dpg.get_value(ANALYTICS_DATA_TAB_BAR_TAG)
    for key, config in _ANALYTICS_REFRESH_CONFIG.items():
        if config["tab_tag"] == selected_tab:
            return key
    return "customer_aisle"


def _analytics_table_has_rows(table_tag: str) -> bool:
    return bool(
        dpg.does_item_exist(table_tag)
        and (dpg.get_item_children(table_tag, 1) or [])
    )


def _ensure_selected_analytics_subtab_loaded() -> None:
    key = _get_selected_analytics_refresh_key()
    config = _ANALYTICS_REFRESH_CONFIG[key]
    with _ANALYTICS_REFRESH_LOCK:
        state = _ANALYTICS_REFRESH_STATES[key]
        has_loaded = bool(state["has_loaded"])
        is_refreshing = bool(state["is_refreshing"])

    if not has_loaded or not _analytics_table_has_rows(config["table_tag"]):
        if not is_refreshing:
            _start_analytics_refresh(key)


def _format_bytes(num_bytes: int) -> str:
    if num_bytes <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{num_bytes} B"


def _format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def _revenue_plot_tag(base: str) -> str:
    return f"{base}_plot"


def _revenue_x_axis_tag(base: str) -> str:
    return f"{base}_x_axis"


def _revenue_y_axis_tag(base: str) -> str:
    return f"{base}_y_axis"


def _clear_plot_axis_series(axis_tag: str) -> None:
    if not dpg.does_item_exist(axis_tag):
        return
    for child in dpg.get_item_children(axis_tag, 1) or []:
        dpg.delete_item(child)


def _reset_xy_plot(base: str) -> None:
    _clear_plot_axis_series(_revenue_y_axis_tag(base))
    if dpg.does_item_exist(_revenue_x_axis_tag(base)):
        dpg.set_axis_ticks(_revenue_x_axis_tag(base), ())


def _reset_pie_plot(base: str) -> None:
    _clear_plot_axis_series(_revenue_y_axis_tag(base))


def _create_xy_revenue_plot(parent: str | None, base: str, label: str) -> None:
    plot_kwargs = {
        "tag": _revenue_plot_tag(base),
        "label": label,
        "width": -1,
        "height": 260,
    }
    if parent is not None:
        plot_kwargs["parent"] = parent

    with dpg.plot(**plot_kwargs):
        dpg.add_plot_legend()
        dpg.add_plot_axis(
            dpg.mvXAxis,
            label="Category",
            tag=_revenue_x_axis_tag(base),
        )
        dpg.add_plot_axis(
            dpg.mvYAxis,
            label="Revenue ($)",
            tag=_revenue_y_axis_tag(base),
        )


def _create_pie_revenue_plot(parent: str | None, base: str, label: str) -> None:
    plot_kwargs = {
        "tag": _revenue_plot_tag(base),
        "label": label,
        "width": -1,
        "height": 260,
    }
    if parent is not None:
        plot_kwargs["parent"] = parent

    with dpg.plot(**plot_kwargs):
        dpg.add_plot_legend()
        dpg.add_plot_axis(
            dpg.mvXAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
            tag=_revenue_x_axis_tag(base),
        )
        dpg.set_axis_limits(_revenue_x_axis_tag(base), 0, 1)
        with dpg.plot_axis(
            dpg.mvYAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
            tag=_revenue_y_axis_tag(base),
        ):
            dpg.set_axis_limits(_revenue_y_axis_tag(base), 0, 1)


def _update_xy_revenue_plot(
    base: str,
    data: list[revenueAnalytics.RevenueDatum],
    series_label: str,
    chart_type: str,
) -> None:
    x_axis_tag = _revenue_x_axis_tag(base)
    y_axis_tag = _revenue_y_axis_tag(base)
    _clear_plot_axis_series(y_axis_tag)
    if dpg.does_item_exist(x_axis_tag):
        dpg.set_axis_ticks(x_axis_tag, ())

    if not data or not dpg.does_item_exist(y_axis_tag):
        return

    x_values = list(range(len(data)))
    y_values = [datum.revenue for datum in data]
    if chart_type == "line":
        dpg.add_line_series(
            x=x_values,
            y=y_values,
            label=series_label,
            parent=y_axis_tag,
        )
    else:
        dpg.add_bar_series(
            x=x_values,
            y=y_values,
            label=series_label,
            weight=0.65,
            parent=y_axis_tag,
        )

    ticks = tuple((datum.label, x) for x, datum in zip(x_values, data))
    dpg.set_axis_ticks(x_axis_tag, ticks)
    dpg.fit_axis_data(x_axis_tag)
    dpg.fit_axis_data(y_axis_tag)


def _top_n_revenue_data(
    data: list[revenueAnalytics.RevenueDatum],
    limit: int,
) -> list[revenueAnalytics.RevenueDatum]:
    if len(data) <= limit:
        return data

    kept = data[: limit - 1]
    other_total = sum(datum.revenue for datum in data[limit - 1 :])
    return kept + [revenueAnalytics.RevenueDatum(label="Other", revenue=other_total)]


def _update_pie_revenue_plot(
    base: str,
    data: list[revenueAnalytics.RevenueDatum],
) -> None:
    y_axis_tag = _revenue_y_axis_tag(base)
    _clear_plot_axis_series(y_axis_tag)

    if not data or not dpg.does_item_exist(y_axis_tag):
        return

    labels = [
        f"{datum.label} ({_format_currency(datum.revenue)})"
        for datum in data
    ]
    values = [datum.revenue for datum in data]
    dpg.add_pie_series(
        x=0.5,
        y=0.5,
        radius=0.4,
        values=values,
        labels=labels,
        normalize=True,
        format="%.1f%%",
        parent=y_axis_tag,
    )


def _get_selected_graph_time_frame() -> tuple[object | None, object | None]:
    selected_time_frame = Singleton().get_graphWindowObj().get_selectedTimeFrame()
    if len(selected_time_frame) != 2:
        return None, None
    return selected_time_frame[0], selected_time_frame[1]


def _revenue_data_to_rows(
    data: list[revenueAnalytics.RevenueDatum],
) -> list[list[str]]:
    total_revenue = sum(datum.revenue for datum in data)
    rows = []
    for datum in data:
        share = (datum.revenue / total_revenue) if total_revenue else 0.0
        rows.append(
            [
                datum.label,
                _format_currency(datum.revenue),
                f"{share * 100:.1f}%",
            ]
        )
    return rows


def reset_revenue_analytics_view() -> None:
    global _REVENUE_ANALYTICS_LOADED
    _REVENUE_ANALYTICS_LOADED = False

    if dpg.does_item_exist(REVENUE_STATUS_TAG):
        dpg.set_value(
            REVENUE_STATUS_TAG,
            "Refresh revenue analytics to load the latest charts.",
        )

    if dpg.does_item_exist(REVENUE_SUMMARY_TABLE_TAG):
        _populate_table_rows(
            REVENUE_SUMMARY_TABLE_TAG,
            [],
            "Refresh revenue analytics to load data.",
            2,
        )
    for table_tag in (
        REVENUE_TIME_TABLE_TAG,
        REVENUE_PRODUCT_TABLE_TAG,
        REVENUE_AGE_TABLE_TAG,
        REVENUE_SEX_TABLE_TAG,
    ):
        if dpg.does_item_exist(table_tag):
            _populate_table_rows(
                table_tag,
                [],
                "Refresh revenue analytics to load data.",
                3,
            )

    for plot_base in (
        "revenue_time_line",
        "revenue_time_bar",
        "revenue_product_bar",
        "revenue_age_bar",
        "revenue_sex_bar",
    ):
        _reset_xy_plot(plot_base)
    for plot_base in (
        "revenue_product_pie",
        "revenue_age_pie",
        "revenue_sex_pie",
    ):
        _reset_pie_plot(plot_base)


def refresh_revenue_analytics_view() -> None:
    global _REVENUE_ANALYTICS_LOADED
    if not dpg.does_item_exist(REVENUE_SUMMARY_TABLE_TAG):
        return

    start_time, end_time = _get_selected_graph_time_frame()
    dashboard = revenueAnalytics.get_revenue_dashboard(start_time, end_time)
    summary = dashboard.summary

    summary_rows = [
        ["Applied Range", summary.applied_range_label],
        ["Total Revenue", _format_currency(summary.total_revenue)],
        ["Transactions", str(summary.transaction_count)],
        ["Average Transaction Value", _format_currency(summary.average_transaction_value)],
        ["Time Granularity", summary.time_granularity],
        ["Peak Time Bucket", summary.peak_time_bucket],
        ["Peak Time Revenue", _format_currency(summary.peak_time_bucket_revenue)],
        ["Top Product", summary.top_product],
        ["Top Product Revenue", _format_currency(summary.top_product_revenue)],
    ]
    _populate_table_rows(
        REVENUE_SUMMARY_TABLE_TAG,
        summary_rows,
        "No revenue summary available.",
        2,
    )
    _populate_table_rows(
        REVENUE_TIME_TABLE_TAG,
        _revenue_data_to_rows(dashboard.by_time),
        "No revenue by time data available.",
        3,
    )
    _populate_table_rows(
        REVENUE_PRODUCT_TABLE_TAG,
        _revenue_data_to_rows(dashboard.by_product),
        "No revenue by product data available.",
        3,
    )
    _populate_table_rows(
        REVENUE_AGE_TABLE_TAG,
        _revenue_data_to_rows(dashboard.by_customer_age),
        "No revenue by customer age data available.",
        3,
    )
    _populate_table_rows(
        REVENUE_SEX_TABLE_TAG,
        _revenue_data_to_rows(dashboard.by_customer_sex),
        "No revenue by customer sex data available.",
        3,
    )

    _update_xy_revenue_plot(
        "revenue_time_line",
        dashboard.by_time,
        "Revenue",
        "line",
    )
    _update_xy_revenue_plot(
        "revenue_time_bar",
        dashboard.by_time,
        "Revenue",
        "bar",
    )
    _update_xy_revenue_plot(
        "revenue_product_bar",
        _top_n_revenue_data(dashboard.by_product, 10),
        "Revenue",
        "bar",
    )
    _update_pie_revenue_plot(
        "revenue_product_pie",
        _top_n_revenue_data(dashboard.by_product, 8),
    )
    _update_xy_revenue_plot(
        "revenue_age_bar",
        dashboard.by_customer_age,
        "Revenue",
        "bar",
    )
    _update_pie_revenue_plot(
        "revenue_age_pie",
        dashboard.by_customer_age,
    )
    _update_xy_revenue_plot(
        "revenue_sex_bar",
        dashboard.by_customer_sex,
        "Revenue",
        "bar",
    )
    _update_pie_revenue_plot(
        "revenue_sex_pie",
        dashboard.by_customer_sex,
    )

    if dpg.does_item_exist(REVENUE_STATUS_TAG):
        time_filter_message = (
            "using the selected time range."
            if start_time is not None and end_time is not None
            else "using all available data."
        )
        dpg.set_value(
            REVENUE_STATUS_TAG,
            f"Revenue analytics refreshed {time_filter_message}",
        )

    _REVENUE_ANALYTICS_LOADED = True


def _get_simulation_summary_rows() -> list[list[str]]:
    overview = visualize_simulation.get_simulation_overview()
    return [
        ["Output File", overview.output_file],
        ["Output Path", overview.output_path],
        ["Video Exists", "Yes" if overview.output_exists else "No"],
        ["Video Size", _format_bytes(overview.output_size_bytes)],
        ["Last Modified", overview.output_modified_at or "Not generated yet"],
        ["Store Size", f"{overview.store_width} x {overview.store_height}"],
        ["Frame Size", f"{overview.image_width} x {overview.image_height}"],
        ["Aisle Count", str(overview.num_aisles)],
        ["Simulation Step", f"{overview.sim_step_seconds} seconds"],
        ["FPS", str(overview.fps)],
        ["Dot Radius", str(overview.dot_radius)],
    ]


def _load_simulation_summary_rows() -> list[list[str]]:
    try:
        return _get_simulation_summary_rows()
    except Exception as exc:
        return [[f"Failed to load simulation info: {exc}", ""]]


def _get_simulation_aisle_rows() -> list[list[str]]:
    overview = visualize_simulation.get_simulation_overview()
    return [
        [str(index + 1), name]
        for index, name in enumerate(overview.aisle_categories)
    ]


def _load_simulation_aisle_rows() -> list[list[str]]:
    try:
        return _get_simulation_aisle_rows()
    except Exception as exc:
        return [[f"Failed to load aisle categories: {exc}", ""]]


def _ensure_simulation_video_texture() -> None:
    if not dpg.does_item_exist(SIMULATION_VIDEO_TEXTURE_REGISTRY_TAG):
        with dpg.texture_registry(tag=SIMULATION_VIDEO_TEXTURE_REGISTRY_TAG):
            pass

    if dpg.does_item_exist(SIMULATION_VIDEO_TEXTURE_TAG):
        return

    dpg.add_dynamic_texture(
        width=SIMULATION_VIDEO_TEX_WIDTH,
        height=SIMULATION_VIDEO_TEX_HEIGHT,
        default_value=SIMULATION_VIDEO_TEX_DATA,
        tag=SIMULATION_VIDEO_TEXTURE_TAG,
        parent=SIMULATION_VIDEO_TEXTURE_REGISTRY_TAG,
    )


def _queue_simulation_video_update(data: list[float]) -> None:
    if not dpg.does_item_exist(SIMULATION_VIDEO_TEXTURE_TAG):
        return
    if len(data) != len(SIMULATION_VIDEO_TEX_DATA):
        return
    SIMULATION_VIDEO_TEX_DATA[:] = data
    dpg.set_value(SIMULATION_VIDEO_TEXTURE_TAG, SIMULATION_VIDEO_TEX_DATA)


def _frame_to_texture_data(frame: np.ndarray) -> list[float]:
    frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    frame_rgba = cv2.resize(
        frame_rgba,
        (SIMULATION_VIDEO_TEX_WIDTH, SIMULATION_VIDEO_TEX_HEIGHT),
        interpolation=cv2.INTER_AREA,
    )
    return (frame_rgba.astype("float32") / 255.0).reshape(-1).tolist()


def _set_simulation_video_frame(frame: np.ndarray) -> None:
    _ensure_simulation_video_texture()
    _queue_simulation_video_update(_frame_to_texture_data(frame))


def _set_simulation_video_blank_frame() -> None:
    blank_frame = np.zeros(
        (SIMULATION_VIDEO_TEX_HEIGHT, SIMULATION_VIDEO_TEX_WIDTH, 3),
        dtype=np.uint8,
    )
    _set_simulation_video_frame(blank_frame)


def _set_simulation_video_status(message: str) -> None:
    if dpg.does_item_exist(SIMULATION_VIDEO_STATUS_TAG):
        dpg.set_value(SIMULATION_VIDEO_STATUS_TAG, message)


def _sync_simulation_frame_input() -> None:
    if dpg.does_item_exist(SIMULATION_VIDEO_FRAME_INPUT_TAG):
        dpg.set_value(
            SIMULATION_VIDEO_FRAME_INPUT_TAG,
            max(1, _SIMULATION_VIDEO_CURRENT_FRAME or 1),
        )


def _release_simulation_video_capture() -> None:
    global _SIMULATION_VIDEO_CAPTURE, _SIMULATION_VIDEO_PATH
    if _SIMULATION_VIDEO_CAPTURE is not None:
        _SIMULATION_VIDEO_CAPTURE.release()
    _SIMULATION_VIDEO_CAPTURE = None
    _SIMULATION_VIDEO_PATH = None


def _load_simulation_video_capture(video_path: str) -> bool:
    global _SIMULATION_VIDEO_CAPTURE, _SIMULATION_VIDEO_PATH
    global _SIMULATION_VIDEO_FPS, _SIMULATION_VIDEO_FRAME_COUNT

    if (
        _SIMULATION_VIDEO_CAPTURE is not None
        and _SIMULATION_VIDEO_PATH == video_path
        and _SIMULATION_VIDEO_CAPTURE.isOpened()
    ):
        return True

    _release_simulation_video_capture()
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        return False

    _SIMULATION_VIDEO_CAPTURE = capture
    _SIMULATION_VIDEO_PATH = video_path
    _SIMULATION_VIDEO_FPS = capture.get(cv2.CAP_PROP_FPS) or 20.0
    _SIMULATION_VIDEO_FRAME_COUNT = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    return True


def _display_simulation_video_first_frame() -> bool:
    global _SIMULATION_VIDEO_CURRENT_FRAME, _SIMULATION_VIDEO_LAST_FRAME_TIME
    overview = visualize_simulation.get_simulation_overview()
    if not overview.output_exists or not os.path.exists(overview.output_path):
        _release_simulation_video_capture()
        _set_simulation_video_blank_frame()
        _set_simulation_video_status("No rendered simulation video found yet.")
        return False

    if not _load_simulation_video_capture(overview.output_path):
        _release_simulation_video_capture()
        _set_simulation_video_blank_frame()
        _set_simulation_video_status("Failed to open the rendered simulation video.")
        return False

    assert _SIMULATION_VIDEO_CAPTURE is not None
    _SIMULATION_VIDEO_CAPTURE.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, frame = _SIMULATION_VIDEO_CAPTURE.read()
    if not success:
        _release_simulation_video_capture()
        _set_simulation_video_blank_frame()
        _set_simulation_video_status("Failed to read the first video frame.")
        return False

    _set_simulation_video_frame(frame)
    _SIMULATION_VIDEO_CURRENT_FRAME = 1
    _SIMULATION_VIDEO_LAST_FRAME_TIME = time.monotonic()
    _sync_simulation_frame_input()
    frame_count_suffix = (
        f"/{_SIMULATION_VIDEO_FRAME_COUNT}" if _SIMULATION_VIDEO_FRAME_COUNT else ""
    )
    _set_simulation_video_status(
        f"Loaded video frame 1{frame_count_suffix}. Use Play to start playback."
    )
    return True


def _set_simulation_playback_button_state() -> None:
    overview = visualize_simulation.get_simulation_overview()
    has_video = overview.output_exists and os.path.exists(overview.output_path)
    if dpg.does_item_exist(SIMULATION_VIDEO_PLAY_BUTTON_TAG):
        dpg.configure_item(
            SIMULATION_VIDEO_PLAY_BUTTON_TAG,
            enabled=has_video and not _SIMULATION_RENDER_STATE["is_rendering"],
        )
    if dpg.does_item_exist(SIMULATION_VIDEO_PAUSE_BUTTON_TAG):
        dpg.configure_item(
            SIMULATION_VIDEO_PAUSE_BUTTON_TAG,
            enabled=_SIMULATION_VIDEO_PLAYING,
        )
    if dpg.does_item_exist(SIMULATION_VIDEO_RESTART_BUTTON_TAG):
        dpg.configure_item(
            SIMULATION_VIDEO_RESTART_BUTTON_TAG,
            enabled=has_video and not _SIMULATION_RENDER_STATE["is_rendering"],
        )
    if dpg.does_item_exist(SIMULATION_VIDEO_JUMP_BUTTON_TAG):
        dpg.configure_item(
            SIMULATION_VIDEO_JUMP_BUTTON_TAG,
            enabled=has_video and not _SIMULATION_RENDER_STATE["is_rendering"],
        )
    if dpg.does_item_exist(SIMULATION_VIDEO_FRAME_INPUT_TAG):
        dpg.configure_item(
            SIMULATION_VIDEO_FRAME_INPUT_TAG,
            enabled=has_video and not _SIMULATION_RENDER_STATE["is_rendering"],
        )


def _simulation_video_tick(sender=None, app_data=None) -> None:
    global _SIMULATION_VIDEO_PLAYING
    global _SIMULATION_VIDEO_LAST_FRAME_TIME, _SIMULATION_VIDEO_CURRENT_FRAME

    if not _SIMULATION_VIDEO_PLAYING:
        _set_simulation_playback_button_state()
        return

    if _SIMULATION_VIDEO_CAPTURE is None or not _SIMULATION_VIDEO_CAPTURE.isOpened():
        _SIMULATION_VIDEO_PLAYING = False
        _set_simulation_video_status("Video playback stopped; no video is loaded.")
        _set_simulation_playback_button_state()
        return

    now = time.monotonic()
    frame_interval = 1.0 / max(_SIMULATION_VIDEO_FPS, 1.0)
    if now - _SIMULATION_VIDEO_LAST_FRAME_TIME < frame_interval:
        return

    success, frame = _SIMULATION_VIDEO_CAPTURE.read()
    if not success:
        _SIMULATION_VIDEO_PLAYING = False
        _set_simulation_video_status("Playback finished.")
        _set_simulation_playback_button_state()
        return

    _set_simulation_video_frame(frame)
    _SIMULATION_VIDEO_LAST_FRAME_TIME = now
    _SIMULATION_VIDEO_CURRENT_FRAME = int(
        _SIMULATION_VIDEO_CAPTURE.get(cv2.CAP_PROP_POS_FRAMES) or 0
    )
    _sync_simulation_frame_input()
    frame_count_suffix = (
        f"/{_SIMULATION_VIDEO_FRAME_COUNT}" if _SIMULATION_VIDEO_FRAME_COUNT else ""
    )
    _set_simulation_video_status(
        f"Playing frame {_SIMULATION_VIDEO_CURRENT_FRAME}{frame_count_suffix}."
    )
    _set_simulation_playback_button_state()


def _jump_to_simulation_frame(frame_number: int) -> bool:
    global _SIMULATION_VIDEO_CURRENT_FRAME, _SIMULATION_VIDEO_LAST_FRAME_TIME
    overview = visualize_simulation.get_simulation_overview()
    if not overview.output_exists or not os.path.exists(overview.output_path):
        _set_simulation_video_status("No rendered simulation video found yet.")
        return False

    if not _load_simulation_video_capture(overview.output_path):
        _set_simulation_video_status("Failed to open the rendered simulation video.")
        return False

    assert _SIMULATION_VIDEO_CAPTURE is not None
    max_frame = _SIMULATION_VIDEO_FRAME_COUNT if _SIMULATION_VIDEO_FRAME_COUNT > 0 else 1
    target_frame = max(1, min(frame_number, max_frame))
    _SIMULATION_VIDEO_CAPTURE.set(cv2.CAP_PROP_POS_FRAMES, target_frame - 1)
    success, frame = _SIMULATION_VIDEO_CAPTURE.read()
    if not success:
        _set_simulation_video_status(f"Failed to jump to frame {target_frame}.")
        return False

    _set_simulation_video_frame(frame)
    _SIMULATION_VIDEO_CURRENT_FRAME = target_frame
    _SIMULATION_VIDEO_LAST_FRAME_TIME = time.monotonic()
    _sync_simulation_frame_input()
    frame_count_suffix = (
        f"/{_SIMULATION_VIDEO_FRAME_COUNT}" if _SIMULATION_VIDEO_FRAME_COUNT else ""
    )
    _set_simulation_video_status(
        f"Showing frame {target_frame}{frame_count_suffix}."
    )
    return True


def _update_simulation_render_state(progress: float, status: str) -> None:
    with _SIMULATION_RENDER_LOCK:
        _SIMULATION_RENDER_STATE["progress"] = progress
        _SIMULATION_RENDER_STATE["status"] = status


def _run_simulation_render() -> None:
    try:
        result = visualize_simulation.render_simulation(
            progress_callback=_update_simulation_render_state
        )
        with _SIMULATION_RENDER_LOCK:
            _SIMULATION_RENDER_STATE["result"] = result
            _SIMULATION_RENDER_STATE["progress"] = 1.0
            _SIMULATION_RENDER_STATE["status"] = (
                f"Render complete. Peak customers: {result.peak_count}."
            )
            _SIMULATION_RENDER_STATE["completed"] = True
            _SIMULATION_RENDER_STATE["is_rendering"] = False
    except Exception as exc:
        with _SIMULATION_RENDER_LOCK:
            _SIMULATION_RENDER_STATE["result"] = None
            _SIMULATION_RENDER_STATE["progress"] = 0.0
            _SIMULATION_RENDER_STATE["status"] = f"Render failed: {exc}"
            _SIMULATION_RENDER_STATE["completed"] = True
            _SIMULATION_RENDER_STATE["is_rendering"] = False


def _poll_simulation_render_state(sender=None, app_data=None) -> None:
    with _SIMULATION_RENDER_LOCK:
        progress = _SIMULATION_RENDER_STATE["progress"]
        status = _SIMULATION_RENDER_STATE["status"]
        is_rendering = _SIMULATION_RENDER_STATE["is_rendering"]
        completed = _SIMULATION_RENDER_STATE["completed"]
        logged_done = _SIMULATION_RENDER_STATE["logged_done"]
        result = _SIMULATION_RENDER_STATE["result"]

    if dpg.does_item_exist(SIMULATION_RENDER_PROGRESS_TAG):
        dpg.set_value(SIMULATION_RENDER_PROGRESS_TAG, progress)
        dpg.configure_item(
            SIMULATION_RENDER_PROGRESS_TAG,
            overlay=f"{progress * 100:.0f}%",
        )
    if dpg.does_item_exist(SIMULATION_RENDER_STATUS_TAG):
        dpg.set_value(SIMULATION_RENDER_STATUS_TAG, status)
    if dpg.does_item_exist(SIMULATION_RENDER_BUTTON_TAG):
        dpg.configure_item(SIMULATION_RENDER_BUTTON_TAG, enabled=not is_rendering)

    _set_simulation_playback_button_state()

    if completed and not logged_done:
        refresh_simulation_info_tables()
        _display_simulation_video_first_frame()
        if result is not None:
            logWindow.addLog(0, f"Simulation rendered to {result.output_path}")
        else:
            logWindow.addLog(2, status)
        with _SIMULATION_RENDER_LOCK:
            _SIMULATION_RENDER_STATE["logged_done"] = True


def refresh_analytics_data_tables() -> None:
    if not dpg.does_item_exist(CUSTOMER_AISLE_GENDER_TABLE_TAG):
        return

    for key in _ANALYTICS_REFRESH_CONFIG:
        _refresh_analytics_payload_sync(key)


def refresh_simulation_info_tables() -> None:
    if not dpg.does_item_exist(SIMULATION_SUMMARY_TABLE_TAG):
        return

    _populate_table_rows(
        SIMULATION_SUMMARY_TABLE_TAG,
        _load_simulation_summary_rows(),
        "No simulation summary available.",
        2,
    )
    _populate_table_rows(
        SIMULATION_AISLES_TABLE_TAG,
        _load_simulation_aisle_rows(),
        "No aisle categories available.",
        2,
    )
    _set_simulation_playback_button_state()


def callback_refresh_analytics_data(sender, app_data, user_data):
    key = str(user_data) if user_data else _get_selected_analytics_refresh_key()
    _start_analytics_refresh(key)


def callback_refresh_simulation_info(sender, app_data, user_data):
    refresh_simulation_info_tables()
    if not _SIMULATION_RENDER_STATE["is_rendering"]:
        _display_simulation_video_first_frame()
    _set_simulation_playback_button_state()


def callback_render_simulation(sender, app_data, user_data):
    global _SIMULATION_VIDEO_PLAYING
    with _SIMULATION_RENDER_LOCK:
        if _SIMULATION_RENDER_STATE["is_rendering"]:
            return
        _SIMULATION_RENDER_STATE["thread"] = None
        _SIMULATION_RENDER_STATE["is_rendering"] = True
        _SIMULATION_RENDER_STATE["progress"] = 0.0
        _SIMULATION_RENDER_STATE["status"] = "Starting simulation render..."
        _SIMULATION_RENDER_STATE["completed"] = False
        _SIMULATION_RENDER_STATE["logged_done"] = False
        _SIMULATION_RENDER_STATE["result"] = None

    _SIMULATION_VIDEO_PLAYING = False
    _release_simulation_video_capture()
    _set_simulation_video_blank_frame()
    _set_simulation_video_status("Rendering simulation video...")
    if dpg.does_item_exist(SIMULATION_RENDER_PROGRESS_TAG):
        dpg.set_value(SIMULATION_RENDER_PROGRESS_TAG, 0.0)
        dpg.configure_item(SIMULATION_RENDER_PROGRESS_TAG, overlay="0%")
    if dpg.does_item_exist(SIMULATION_RENDER_STATUS_TAG):
        dpg.set_value(SIMULATION_RENDER_STATUS_TAG, "Starting simulation render...")
    thread = threading.Thread(target=_run_simulation_render, daemon=True)
    with _SIMULATION_RENDER_LOCK:
        _SIMULATION_RENDER_STATE["thread"] = thread

    thread.start()
    _set_simulation_playback_button_state()


def callback_play_simulation_video(sender, app_data, user_data):
    global _SIMULATION_VIDEO_PLAYING, _SIMULATION_VIDEO_LAST_FRAME_TIME
    if _SIMULATION_RENDER_STATE["is_rendering"]:
        display_modal_popup(2, "Wait for the simulation render to finish first.")
        return

    if _SIMULATION_VIDEO_CAPTURE is None or not _SIMULATION_VIDEO_CAPTURE.isOpened():
        if not _display_simulation_video_first_frame():
            display_modal_popup(2, "No rendered simulation video is available yet.")
            return
    elif (
        _SIMULATION_VIDEO_FRAME_COUNT
        and _SIMULATION_VIDEO_CURRENT_FRAME >= _SIMULATION_VIDEO_FRAME_COUNT
    ):
        if not _display_simulation_video_first_frame():
            display_modal_popup(2, "No rendered simulation video is available yet.")
            return

    _SIMULATION_VIDEO_PLAYING = True
    _SIMULATION_VIDEO_LAST_FRAME_TIME = 0.0
    _set_simulation_video_status("Playing simulation video...")
    _set_simulation_playback_button_state()


def callback_pause_simulation_video(sender, app_data, user_data):
    global _SIMULATION_VIDEO_PLAYING
    _SIMULATION_VIDEO_PLAYING = False
    _set_simulation_video_status("Playback paused.")
    _set_simulation_playback_button_state()


def callback_restart_simulation_video(sender, app_data, user_data):
    global _SIMULATION_VIDEO_PLAYING
    _SIMULATION_VIDEO_PLAYING = False
    if not _display_simulation_video_first_frame():
        display_modal_popup(2, "No rendered simulation video is available yet.")
    _set_simulation_playback_button_state()


def callback_jump_simulation_video_frame(sender, app_data, user_data):
    global _SIMULATION_VIDEO_PLAYING
    _SIMULATION_VIDEO_PLAYING = False
    target_frame = dpg.get_value(SIMULATION_VIDEO_FRAME_INPUT_TAG)
    if not _jump_to_simulation_frame(int(target_frame)):
        display_modal_popup(2, "Unable to jump to that frame.")
    _set_simulation_playback_button_state()


def pump_analytics_view() -> None:
    for key in _ANALYTICS_REFRESH_CONFIG:
        _poll_analytics_refresh_state(key)


def pump_simulation_view() -> None:
    with _SIMULATION_RENDER_LOCK:
        is_rendering = _SIMULATION_RENDER_STATE["is_rendering"]
        completed = _SIMULATION_RENDER_STATE["completed"]
        logged_done = _SIMULATION_RENDER_STATE["logged_done"]

    if is_rendering or (completed and not logged_done):
        _poll_simulation_render_state()

    if _SIMULATION_VIDEO_PLAYING:
        _simulation_video_tick()


def callback_graph_view_changed(sender, app_data, user_data):
    selected_tab = dpg.get_value(GRAPH_VIEW_TAB_BAR_TAG)
    if selected_tab == GRAPH_ANALYTICS_TAB_TAG:
        _ensure_selected_analytics_subtab_loaded()
    elif selected_tab == GRAPH_REVENUE_TAB_TAG:
        if not _REVENUE_ANALYTICS_LOADED:
            refresh_revenue_analytics_view()
    elif selected_tab == GRAPH_SIMULATION_TAB_TAG:
        refresh_simulation_info_tables()
        if not _SIMULATION_RENDER_STATE["is_rendering"]:
            _display_simulation_video_first_frame()


def callback_analytics_subtab_changed(sender, app_data, user_data):
    _ensure_selected_analytics_subtab_loaded()


def _create_analytics_refresh_controls(
    button_tag: str,
    progress_tag: str,
    status_tag: str,
    button_label: str,
    refresh_key: str,
    helper_text: str,
) -> None:
    with dpg.group(horizontal=True):
        dpg.add_button(
            label=button_label,
            tag=button_tag,
            callback=callback_refresh_analytics_data,
            user_data=refresh_key,
        )
        dpg.add_text(helper_text)
    dpg.add_progress_bar(
        default_value=0.0,
        overlay="0%",
        width=-1,
        tag=progress_tag,
    )
    dpg.add_text(
        _ANALYTICS_REFRESH_CONFIG[refresh_key]["ready_status"],
        tag=status_tag,
    )


def create_analytics_data_view(parent: str) -> None:
    with dpg.child_window(parent=parent, border=False, width=-1, height=-1):
        dpg.add_text(
            "Use the subtabs below to inspect each analysis independently."
        )
        with dpg.tab_bar(
            tag=ANALYTICS_DATA_TAB_BAR_TAG,
            callback=callback_analytics_subtab_changed,
        ):
            with dpg.tab(
                label="customerAisleAnalytics.py",
                tag=ANALYTICS_CUSTOMER_AISLE_TAB_TAG,
            ):
                _create_analytics_refresh_controls(
                    CUSTOMER_AISLE_REFRESH_BUTTON_TAG,
                    CUSTOMER_AISLE_PROGRESS_TAG,
                    CUSTOMER_AISLE_STATUS_TAG,
                    "Refresh customerAisleAnalytics.py",
                    "customer_aisle",
                    "Refresh this analysis without reloading the others.",
                )
                dpg.add_spacer(height=6)
                with dpg.tab_bar(tag=CUSTOMER_AISLE_ANALYSIS_TAB_BAR_TAG):
                    with dpg.tab(
                        label="Most Common Gender",
                        tag=CUSTOMER_AISLE_GENDER_TAB_TAG,
                    ):
                        dpg.add_text("Most common customer gender by aisle")
                        _add_stretch_table(
                            CUSTOMER_AISLE_GENDER_TABLE_TAG,
                            ["Aisle ID", "Most Common Gender"],
                            CUSTOMER_AISLE_GENDER_TAB_TAG,
                        )

                    with dpg.tab(
                        label="Most Common Age",
                        tag=CUSTOMER_AISLE_AGE_TAB_TAG,
                    ):
                        dpg.add_text("Most common customer age by aisle")
                        _add_stretch_table(
                            CUSTOMER_AISLE_AGE_TABLE_TAG,
                            ["Aisle ID", "Most Common Age"],
                            CUSTOMER_AISLE_AGE_TAB_TAG,
                        )

            with dpg.tab(
                label="customerAttributesEstimator.py",
                tag=ANALYTICS_CUSTOMER_ATTRIBUTES_TAB_TAG,
            ):
                _create_analytics_refresh_controls(
                    CUSTOMER_ATTRIBUTES_REFRESH_BUTTON_TAG,
                    CUSTOMER_ATTRIBUTES_PROGRESS_TAG,
                    CUSTOMER_ATTRIBUTES_STATUS_TAG,
                    "Refresh customerAttributesEstimator.py",
                    "customer_attributes",
                    "Reload the estimator labels defined in the module.",
                )
                dpg.add_spacer(height=6)
                dpg.add_text("Estimator label sets declared in the module")
                _add_stretch_table(
                    CUSTOMER_ATTRIBUTES_TABLE_TAG,
                    ["Label Type", "Value"],
                    ANALYTICS_CUSTOMER_ATTRIBUTES_TAB_TAG,
                )

            with dpg.tab(
                label="customerProductAnalytics.py",
                tag=ANALYTICS_CUSTOMER_PRODUCT_TAB_TAG,
            ):
                _create_analytics_refresh_controls(
                    CUSTOMER_PRODUCT_REFRESH_BUTTON_TAG,
                    CUSTOMER_PRODUCT_PROGRESS_TAG,
                    CUSTOMER_PRODUCT_STATUS_TAG,
                    "Refresh customerProductAnalytics.py",
                    "customer_product",
                    "Refresh this product-level analysis only.",
                )
                dpg.add_spacer(height=6)
                with dpg.tab_bar(tag=CUSTOMER_PRODUCT_ANALYSIS_TAB_BAR_TAG):
                    with dpg.tab(
                        label="Most Common Gender",
                        tag=CUSTOMER_PRODUCT_GENDER_TAB_TAG,
                    ):
                        dpg.add_text("Most common customer gender by product")
                        _add_stretch_table(
                            CUSTOMER_PRODUCT_GENDER_TABLE_TAG,
                            ["Product", "Most Common Gender"],
                            CUSTOMER_PRODUCT_GENDER_TAB_TAG,
                        )

                    with dpg.tab(
                        label="Most Common Age",
                        tag=CUSTOMER_PRODUCT_AGE_TAB_TAG,
                    ):
                        dpg.add_text("Most common customer age by product")
                        _add_stretch_table(
                            CUSTOMER_PRODUCT_AGE_TABLE_TAG,
                            ["Product", "Most Common Age"],
                            CUSTOMER_PRODUCT_AGE_TAB_TAG,
                        )

            with dpg.tab(
                label="sectionTimeAnalysis.py",
                tag=ANALYTICS_SECTION_TIME_TAB_TAG,
            ):
                _create_analytics_refresh_controls(
                    SECTION_TIME_REFRESH_BUTTON_TAG,
                    SECTION_TIME_PROGRESS_TAG,
                    SECTION_TIME_STATUS_TAG,
                    "Refresh sectionTimeAnalysis.py",
                    "section_time",
                    "This can take a while because it walks each store's paths.",
                )
                dpg.add_spacer(height=6)
                dpg.add_text("Section time summaries across all stores")
                _add_stretch_table(
                    SECTION_TIME_TABLE_TAG,
                    [
                        "Store ID",
                        "Store",
                        "Aisle ID",
                        "Section",
                        "Total Seconds",
                        "Average Seconds",
                        "Customers",
                    ],
                    ANALYTICS_SECTION_TIME_TAB_TAG,
                )

            with dpg.tab(
                label="basketAnalysis.py",
                tag=ANALYTICS_BASKET_TAB_TAG,
            ):
                _create_analytics_refresh_controls(
                    BASKET_REFRESH_BUTTON_TAG,
                    BASKET_PROGRESS_TAG,
                    BASKET_STATUS_TAG,
                    "Refresh basketAnalysis.py",
                    "basket",
                    "Refresh basket metrics and association rules.",
                )
                dpg.add_spacer(height=6)
                with dpg.tab_bar(tag=BASKET_ANALYSIS_TAB_BAR_TAG):
                    with dpg.tab(label="Summary", tag=BASKET_SUMMARY_TAB_TAG):
                        dpg.add_text("Basket summary metrics across all stores")
                        _add_stretch_table(
                            BASKET_SUMMARY_TABLE_TAG,
                            [
                                "Store ID",
                                "Store",
                                "Transactions",
                                "Revenue",
                                "Avg Basket Size",
                                "Avg Quantity",
                                "Avg Value",
                            ],
                            BASKET_SUMMARY_TAB_TAG,
                        )

                    with dpg.tab(label="Per Product", tag=BASKET_PRODUCTS_TAB_TAG):
                        dpg.add_text("Per-product basket analysis")
                        _add_stretch_table(
                            BASKET_PRODUCTS_TABLE_TAG,
                            [
                                "Store ID",
                                "Store",
                                "Product",
                                "Quantity Sold",
                                "Transactions",
                                "Revenue",
                            ],
                            BASKET_PRODUCTS_TAB_TAG,
                        )

                    with dpg.tab(label="Product Pairs", tag=BASKET_PAIRS_TAB_TAG):
                        dpg.add_text("Product-pair association rules")
                        _add_stretch_table(
                            BASKET_PAIRS_TABLE_TAG,
                            [
                                "Store ID",
                                "Store",
                                "Product A",
                                "Product B",
                                "Co-Occurrences",
                                "Support",
                                "Confidence A->B",
                                "Confidence B->A",
                                "Lift",
                            ],
                            BASKET_PAIRS_TAB_TAG,
                        )

        for key in _ANALYTICS_REFRESH_CONFIG:
            _poll_analytics_refresh_state(key)


def create_simulation_view(parent: str) -> None:
    _ensure_simulation_video_texture()
    with dpg.child_window(parent=parent, border=False, width=-1, height=-1):
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Render Simulation",
                tag=SIMULATION_RENDER_BUTTON_TAG,
                callback=callback_render_simulation,
            )
            dpg.add_button(
                label="Refresh Simulation Info",
                tag=SIMULATION_VIDEO_REFRESH_BUTTON_TAG,
                callback=callback_refresh_simulation_info,
            )
        dpg.add_progress_bar(
            default_value=0.0,
            overlay="0%",
            width=-1,
            tag=SIMULATION_RENDER_PROGRESS_TAG,
        )
        dpg.add_text(
            "Render progress will appear here.",
            tag=SIMULATION_RENDER_STATUS_TAG,
        )

        with dpg.collapsing_header(
            label="Simulation Output",
            default_open=True,
        ) as simulation_header:
            dpg.add_text(
                "Run `python -m src.logic.visualize_simulation` from the project root to generate or refresh the simulation video."
            )
            _add_stretch_table(
                SIMULATION_SUMMARY_TABLE_TAG,
                ["Property", "Value"],
                simulation_header,
            )

        with dpg.collapsing_header(
            label="Simulation Aisles",
            default_open=True,
        ) as aisles_header:
            dpg.add_text("Aisle categories rendered in the simulation")
            _add_stretch_table(
                SIMULATION_AISLES_TABLE_TAG,
                ["Aisle", "Category"],
                aisles_header,
            )

        with dpg.collapsing_header(
            label="Video Playback",
            default_open=True,
        ) as playback_header:
            with dpg.group(horizontal=True, parent=playback_header):
                dpg.add_button(
                    label="Play",
                    tag=SIMULATION_VIDEO_PLAY_BUTTON_TAG,
                    callback=callback_play_simulation_video,
                )
                dpg.add_button(
                    label="Pause",
                    tag=SIMULATION_VIDEO_PAUSE_BUTTON_TAG,
                    callback=callback_pause_simulation_video,
                )
                dpg.add_button(
                    label="Restart",
                    tag=SIMULATION_VIDEO_RESTART_BUTTON_TAG,
                    callback=callback_restart_simulation_video,
                )
            with dpg.group(horizontal=True, parent=playback_header):
                dpg.add_text("Jump To Frame:")
                dpg.add_input_int(
                    tag=SIMULATION_VIDEO_FRAME_INPUT_TAG,
                    default_value=1,
                    min_value=1,
                    min_clamped=True,
                    width=120,
                )
                dpg.add_button(
                    label="Jump",
                    tag=SIMULATION_VIDEO_JUMP_BUTTON_TAG,
                    callback=callback_jump_simulation_video_frame,
                )
            dpg.add_text(
                "No rendered simulation video found yet.",
                parent=playback_header,
                tag=SIMULATION_VIDEO_STATUS_TAG,
            )
            dpg.add_image(
                SIMULATION_VIDEO_TEXTURE_TAG,
                parent=playback_header,
                tag=SIMULATION_VIDEO_IMAGE_TAG,
                width=SIMULATION_VIDEO_TEX_WIDTH,
                height=SIMULATION_VIDEO_TEX_HEIGHT,
            )

    _set_simulation_video_blank_frame()
    refresh_simulation_info_tables()
    _display_simulation_video_first_frame()
    _set_simulation_playback_button_state()


def _create_pie_chart_view(parent: str) -> None:
    dpg.add_text("Use Update Chart to render the selected data.", parent=parent)
    with dpg.plot(
        tag="graphPie",
        label="Fruit Distribution",
        parent=parent,
        width=-1,
        height=-1,
        show=False,
    ):
        dpg.add_plot_legend()

        dpg.add_plot_axis(
            dpg.mvXAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
        )
        dpg.set_axis_limits(dpg.last_item(), 0, 1)

        with dpg.plot_axis(
            dpg.mvYAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
        ) as y_axis:
            dpg.set_axis_limits(y_axis, 0, 1)

            dpg.add_pie_series(
                x=0.5,
                y=0.5,
                radius=0.4,
                values=[15, 30, 45, 10],
                labels=["Apples", "Bananas", "Cherries", "Dates"],
                normalize=True,
                format="%.1f%%",
                tag="pieSeries",
            )


def callback_refresh_revenue_analytics(sender, app_data, user_data):
    refresh_revenue_analytics_view()


def create_revenue_analytics_view(parent: str) -> None:
    with dpg.child_window(parent=parent, border=False, width=-1, height=-1):
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Refresh Revenue Analytics",
                tag=REVENUE_REFRESH_BUTTON_TAG,
                callback=callback_refresh_revenue_analytics,
            )
            dpg.add_text(
                "Uses the selected time range on the left when both start and end are set."
            )
        dpg.add_text(
            "Refresh revenue analytics to load the latest charts.",
            tag=REVENUE_STATUS_TAG,
        )

        with dpg.collapsing_header(label="Revenue Summary", default_open=True) as summary_header:
            _add_stretch_table(
                REVENUE_SUMMARY_TABLE_TAG,
                ["Metric", "Value"],
                summary_header,
            )

        with dpg.tab_bar(tag=REVENUE_ANALYTICS_TAB_BAR_TAG):
            with dpg.tab(label="Revenue by Time", tag=REVENUE_TIME_TAB_TAG):
                dpg.add_text("Checkout revenue trend over time")
                _create_xy_revenue_plot(
                    REVENUE_TIME_TAB_TAG,
                    "revenue_time_line",
                    "Revenue by Time (Line)",
                )
                dpg.add_spacer(height=6)
                _create_xy_revenue_plot(
                    REVENUE_TIME_TAB_TAG,
                    "revenue_time_bar",
                    "Revenue by Time (Bar)",
                )
                dpg.add_spacer(height=6)
                _add_stretch_table(
                    REVENUE_TIME_TABLE_TAG,
                    ["Time Bucket", "Revenue", "Share"],
                    REVENUE_TIME_TAB_TAG,
                )

            with dpg.tab(label="Revenue by Product", tag=REVENUE_PRODUCT_TAB_TAG):
                with dpg.table(policy=dpg.mvTable_SizingStretchProp, header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    with dpg.table_row():
                        with dpg.table_cell():
                            _create_xy_revenue_plot(
                                None,
                                "revenue_product_bar",
                                "Revenue by Product (Bar)",
                            )
                        with dpg.table_cell():
                            _create_pie_revenue_plot(
                                None,
                                "revenue_product_pie",
                                "Revenue by Product (Pie)",
                            )
                dpg.add_spacer(height=6)
                _add_stretch_table(
                    REVENUE_PRODUCT_TABLE_TAG,
                    ["Product", "Revenue", "Share"],
                    REVENUE_PRODUCT_TAB_TAG,
                )

            with dpg.tab(label="Revenue by Customer Age", tag=REVENUE_AGE_TAB_TAG):
                with dpg.table(policy=dpg.mvTable_SizingStretchProp, header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    with dpg.table_row():
                        with dpg.table_cell():
                            _create_xy_revenue_plot(
                                None,
                                "revenue_age_bar",
                                "Revenue by Customer Age (Bar)",
                            )
                        with dpg.table_cell():
                            _create_pie_revenue_plot(
                                None,
                                "revenue_age_pie",
                                "Revenue by Customer Age (Pie)",
                            )
                dpg.add_spacer(height=6)
                _add_stretch_table(
                    REVENUE_AGE_TABLE_TAG,
                    ["Age Group", "Revenue", "Share"],
                    REVENUE_AGE_TAB_TAG,
                )

            with dpg.tab(label="Revenue by Customer Sex", tag=REVENUE_SEX_TAB_TAG):
                with dpg.table(policy=dpg.mvTable_SizingStretchProp, header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    with dpg.table_row():
                        with dpg.table_cell():
                            _create_xy_revenue_plot(
                                None,
                                "revenue_sex_bar",
                                "Revenue by Customer Sex (Bar)",
                            )
                        with dpg.table_cell():
                            _create_pie_revenue_plot(
                                None,
                                "revenue_sex_pie",
                                "Revenue by Customer Sex (Pie)",
                            )
                dpg.add_spacer(height=6)
                _add_stretch_table(
                    REVENUE_SEX_TABLE_TAG,
                    ["Customer Sex", "Revenue", "Share"],
                    REVENUE_SEX_TAB_TAG,
                )

        reset_revenue_analytics_view()


def create_graph_panel(parent: str) -> None:
    with dpg.child_window(parent=parent, border=False, width=-1, height=-1):
        with dpg.tab_bar(
            tag=GRAPH_VIEW_TAB_BAR_TAG,
            callback=callback_graph_view_changed,
        ):
            with dpg.tab(label="Pie Chart", tag=GRAPH_PIE_TAB_TAG):
                _create_pie_chart_view(GRAPH_PIE_TAB_TAG)
            with dpg.tab(label="Analytics Data", tag=GRAPH_ANALYTICS_TAB_TAG):
                create_analytics_data_view(GRAPH_ANALYTICS_TAB_TAG)
            with dpg.tab(label="Revenue Analytics", tag=GRAPH_REVENUE_TAB_TAG):
                create_revenue_analytics_view(GRAPH_REVENUE_TAB_TAG)
            with dpg.tab(label="Simulation", tag=GRAPH_SIMULATION_TAB_TAG):
                create_simulation_view(GRAPH_SIMULATION_TAB_TAG)


def create_data_analytics_window(parent: str):
    with dpg.child_window(
        label="Graphs",
        parent=parent,
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        dpg.add_button(label="test", callback=callback_test, show=False)

        dpg.add_combo(
            ["Select Chart Type", "Pie Chart"],
            label="Chart Type",
            default_value="Select Chart Type",
            tag="chart_type_dropdown",
            fit_width=True,
        )
        with dpg.group(horizontal=True):
            dpg.add_combo(
                [START_TIME_PLACEHOLDER],
                tag="StartTimes",
                default_value=START_TIME_PLACEHOLDER,
                callback=callback_startTimeSelected,
                fit_width=True,
            )
            dpg.add_combo(
                [END_TIME_PLACEHOLDER],
                tag="EndTimes",
                default_value=END_TIME_PLACEHOLDER,
                callback=callback_EndTimeSelected,
                fit_width=True,
            )

        # with dpg.group(horizontal=True):
        #     dpg.add_combo(["poducts", "category"])
        #     dpg.add_combo(["age", "category"])
        dpg.add_button(
            label="Swap Categories and Counts Types",
            callback=callback_swapCategoriesAndCounts,
        )
        with dpg.table(
            tag="dataSelectorOfSelector",
            policy=dpg.mvTable_SizingStretchProp,
            borders_innerV=True,
        ):
            dpg.add_table_column(label="Count", init_width_or_weight=0.5)
            dpg.add_table_column(label="Category", init_width_or_weight=0.5)
            with dpg.table_row(parent="dataSelectorOfSelector"):
                with dpg.table(
                    tag="countsSelector",
                    label="countsSelector",
                    show=True,
                ):
                    dpg.add_table_column()
                with dpg.table(
                    tag="categorySelector",
                    label="categorySelector",
                    show=True,
                ):
                    dpg.add_table_column()
        populateDropDowns()

        dpg.add_button(label="Update Chart", callback=callback_update_charts)
        # 1. Create a plot environment
        # with dpg.plot(
        #     tag="graphPie", label="Fruit Distribution", width=-1, height=-1, show=False
        # ):
        #     dpg.add_plot_legend()

        #     # 2. Add an X axis and hide its gridlines and ticks
        #     dpg.add_plot_axis(
        #         dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True
        #     )
        #     dpg.set_axis_limits(dpg.last_item(), 0, 1)

        #     # 3. Add a Y axis (also hidden) - The pie series must be parented to this axis!
        #     with dpg.plot_axis(
        #         dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True
        #     ) as y_axis:
        #         dpg.set_axis_limits(y_axis, 0, 1)

        #         # The data for our slices
        #         slice_values = [15, 30, 45, 10]
        #         slice_labels = ["Apples", "Bananas", "Cherries", "Dates"]

        #         # 4. Add the pie series
        #         dpg.add_pie_series(
        #             x=0.5,  # X center coordinate
        #             y=0.5,  # Y center coordinate
        #             radius=0.4,  # Size of the pie
        #             values=slice_values,
        #             labels=slice_labels,
        #             normalize=True,  # Automatically calculates percentages
        #             format="%.1f%%",  # The text format shown when hovering over slices
        #             tag="pieSeries",
        #         )
