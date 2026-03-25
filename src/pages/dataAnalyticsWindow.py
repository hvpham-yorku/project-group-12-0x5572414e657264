# TODO Refactor into own class maybe?

import dearpygui.dearpygui as dpg
from src.pages.popupWindow import display_modal_popup
from src.logic.singleton import Singleton

START_TIME_PLACEHOLDER = "Select Start Time"
END_TIME_PLACEHOLDER = "Select End Time"


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
