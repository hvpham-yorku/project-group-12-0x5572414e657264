# TODO Refactor into own class maybe?

import ast
from pathlib import Path

import dearpygui.dearpygui as dpg
from src.database.model_managers import get_all_stores
from src.logic import (
    customerAisleAnalytics,
    customerProductAnalytics,
    sectionTimeAnalysis,
)
from src.pages.popupWindow import display_modal_popup
from src.logic.singleton import Singleton

START_TIME_PLACEHOLDER = "Select Start Time"
END_TIME_PLACEHOLDER = "Select End Time"
GRAPH_VIEW_TAB_BAR_TAG = "graph_view_tabs"
GRAPH_PIE_TAB_TAG = "graph_pie_tab"
GRAPH_ANALYTICS_TAB_TAG = "graph_analytics_tab"

CUSTOMER_AISLE_GENDER_TABLE_TAG = "customer_aisle_gender_table"
CUSTOMER_AISLE_AGE_TABLE_TAG = "customer_aisle_age_table"
CUSTOMER_PRODUCT_GENDER_TABLE_TAG = "customer_product_gender_table"
CUSTOMER_PRODUCT_AGE_TABLE_TAG = "customer_product_age_table"
CUSTOMER_ATTRIBUTES_TABLE_TAG = "customer_attributes_estimator_table"
SECTION_TIME_TABLE_TAG = "section_time_analysis_table"


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


def callback_startTimeSelected(sender, app_data, user_data):
    selected = dpg.get_value("StartTimes")
    s = Singleton().get_graphWindowObj()

    if selected == START_TIME_PLACEHOLDER:
        if dpg.does_item_exist("EndTimes"):
            dpg.configure_item("EndTimes", items=[END_TIME_PLACEHOLDER])
            dpg.set_value("EndTimes", END_TIME_PLACEHOLDER)
        s.resetSelectedTimeFrame()
        return

    possibleDateTimes = s._get_possibleDateTimes()
    strDateTimeDic = {str(date): date for date in possibleDateTimes}
    selected_datetime = strDateTimeDic.get(selected)
    if selected_datetime is None:
        _reset_time_selectors(
            [START_TIME_PLACEHOLDER] + [str(x) for x in possibleDateTimes]
        )
        return

    selected_index = possibleDateTimes.index(selected_datetime)
    end_items = [END_TIME_PLACEHOLDER] + [
        str(x) for x in possibleDateTimes[selected_index:]
    ]
    if dpg.does_item_exist("EndTimes"):
        dpg.configure_item("EndTimes", items=end_items)
        dpg.set_value("EndTimes", END_TIME_PLACEHOLDER)
    s.resetSelectedTimeFrame()


def callback_EndTimeSelected(sender, app_data, user_data):
    s = Singleton().get_graphWindowObj()
    start = dpg.get_value("StartTimes")
    end = dpg.get_value("EndTimes")

    if start == START_TIME_PLACEHOLDER or end == END_TIME_PLACEHOLDER:
        s.resetSelectedTimeFrame()
        return

    possibleDateTimes = s._get_possibleDateTimes()
    strDateTimeDic = {str(date): date for date in possibleDateTimes}
    start_time = strDateTimeDic.get(start)
    end_time = strDateTimeDic.get(end)
    if start_time is None or end_time is None:
        s.resetSelectedTimeFrame()
        return

    s.setSelectedTimeFrame(start_time, end_time)


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


def refresh_analytics_data_tables() -> None:
    if not dpg.does_item_exist(CUSTOMER_AISLE_GENDER_TABLE_TAG):
        return

    _populate_table_rows(
        CUSTOMER_AISLE_GENDER_TABLE_TAG,
        _load_mapping_rows(customerAisleAnalytics.get_product_category_most_common_gender),
        "No aisle gender analytics available.",
        2,
    )
    _populate_table_rows(
        CUSTOMER_AISLE_AGE_TABLE_TAG,
        _load_mapping_rows(customerAisleAnalytics.get_product_category_most_common_age),
        "No aisle age analytics available.",
        2,
    )
    _populate_table_rows(
        CUSTOMER_PRODUCT_GENDER_TABLE_TAG,
        _load_mapping_rows(customerProductAnalytics.get_product_most_common_gender),
        "No product gender analytics available.",
        2,
    )
    _populate_table_rows(
        CUSTOMER_PRODUCT_AGE_TABLE_TAG,
        _load_mapping_rows(customerProductAnalytics.get_product_most_common_age),
        "No product age analytics available.",
        2,
    )
    _populate_table_rows(
        CUSTOMER_ATTRIBUTES_TABLE_TAG,
        _load_customer_attribute_estimator_rows(),
        "No estimator labels available.",
        2,
    )
    _populate_table_rows(
        SECTION_TIME_TABLE_TAG,
        _load_section_time_analysis_rows(),
        "No section time analytics available.",
        7,
    )


def callback_refresh_analytics_data(sender, app_data, user_data):
    refresh_analytics_data_tables()


def callback_graph_view_changed(sender, app_data, user_data):
    selected_tab = dpg.get_value(GRAPH_VIEW_TAB_BAR_TAG)
    if selected_tab == GRAPH_ANALYTICS_TAB_TAG:
        refresh_analytics_data_tables()


def create_analytics_data_view(parent: str) -> None:
    with dpg.child_window(parent=parent, border=False, width=-1, height=-1):
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Refresh Analytics Data",
                callback=callback_refresh_analytics_data,
            )
            dpg.add_text(
                "Use the tabs above to switch between the chart and live analytics data."
            )

        with dpg.collapsing_header(
            label="customerAisleAnalytics.py",
            default_open=True,
        ) as aisle_header:
            dpg.add_text("Most common customer gender by aisle")
            _add_stretch_table(
                CUSTOMER_AISLE_GENDER_TABLE_TAG,
                ["Aisle ID", "Most Common Gender"],
                aisle_header,
            )
            dpg.add_spacer(height=6)
            dpg.add_text("Most common customer age by aisle")
            _add_stretch_table(
                CUSTOMER_AISLE_AGE_TABLE_TAG,
                ["Aisle ID", "Most Common Age"],
                aisle_header,
            )

        with dpg.collapsing_header(
            label="customerAttributesEstimator.py",
            default_open=True,
        ) as estimator_header:
            dpg.add_text("Estimator label sets declared in the module")
            _add_stretch_table(
                CUSTOMER_ATTRIBUTES_TABLE_TAG,
                ["Label Type", "Value"],
                estimator_header,
            )

        with dpg.collapsing_header(
            label="customerProductAnalytics.py",
            default_open=True,
        ) as product_header:
            dpg.add_text("Most common customer gender by product")
            _add_stretch_table(
                CUSTOMER_PRODUCT_GENDER_TABLE_TAG,
                ["Product", "Most Common Gender"],
                product_header,
            )
            dpg.add_spacer(height=6)
            dpg.add_text("Most common customer age by product")
            _add_stretch_table(
                CUSTOMER_PRODUCT_AGE_TABLE_TAG,
                ["Product", "Most Common Age"],
                product_header,
            )

        with dpg.collapsing_header(
            label="sectionTimeAnalysis.py",
            default_open=True,
        ) as section_header:
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
                section_header,
            )

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
