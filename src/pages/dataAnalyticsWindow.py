# TODO Refactor into own class maybe?

import dearpygui.dearpygui as dpg
from src.pages.popupWindow import display_modal_popup
from src.logic.singleton import Singleton


def callback_update_charts(sender, app_data, user_data):
    chartType = dpg.get_value("chart_type_dropdown")
    match chartType:
        case "Pie Chart":
            dpg.configure_item("graphPie", show=True)
            display_modal_popup(2, "NOT IMPLEMENTED YET")
        case "Line Chart":
            dpg.configure_item("graphPie", show=False)
            display_modal_popup(2, "NOT IMPLEMENTED YET")
        case "_":
            display_modal_popup(2, "Please select a chart type! :)")


def callback_save_checked_boxes(sender, app_data, user_data):
    print()


def callback_swapCategoriesAndCounts(sender, app_data, user_data):
    Singleton().get_graphWindowObj().swap_category_and_counted()
    # TODO refresh dropdown boxes


def populateCountAndCategories() -> None:
    s = Singleton().get_graphWindowObj()
    for countStr in s.get_countsAvailable():
        with dpg.table_row(parent="countsSelector"):
            with dpg.group(horizontal=True):
                dpg.add_text(countStr)
                dpg.add_checkbox(
                    callback=callback_save_checked_boxes,
                    default_value=False,
                )
    with dpg.table_row(parent="categorySelector"):
        dpg.add_radio_button(
            label="testing",
            items=s.get_categoriesAvailable(),
            callback=callback_save_checked_boxes,
        )


def create_data_analytics_window(parent: str):
    with dpg.child_window(
        label="Graphs",
        parent=parent,
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        dpg.add_combo(
            ["Select Chart Type", "Pie Chart", "Line Chart"],
            label="Chart Type",
            default_value="Select Chart Type",
            tag="chart_type_dropdown",
        )

        # with dpg.group(horizontal=True):
        #     dpg.add_combo(["poducts", "category"])
        #     dpg.add_combo(["age", "category"])
        dpg.add_button(
            label="Swap Categories and Counts Types", callback=callback_update_charts
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
                    # dpg.add_table_column(label="Categories", init_width_or_weight=0.5)
                    # with dpg.table_row(parent="countsSelector"):
                    #     # dpg.add_text("test")
                    #     dpg.add_checkbox(
                    #         callback=callback_save_checked_boxes,
                    #         default_value=False,
                    #     )
                    #     dpg.add_checkbox(
                    #         callback=callback_save_checked_boxes,
                    #         default_value=False,
                    #     )
                    #     dpg.add_checkbox(
                    #         callback=callback_save_checked_boxes,
                    #         default_value=False,
                    #     )
                with dpg.table(
                    tag="categorySelector",
                    label="categorySelector",
                    show=True,
                ):
                    dpg.add_table_column()
                    # dpg.add_table_column(label="Categories", init_width_or_weight=0.5)
                    # with dpg.table_row(parent="categorySelector"):
                    #     # dpg.add_text("test")
                    #     dpg.add_radio_button(
                    #         label="testing",
                    #         items=["test1", "test2"],
                    #         callback=callback_save_checked_boxes,
                    #     )
        populateCountAndCategories()

        dpg.add_button(label="Update Chart", callback=callback_update_charts)
        # 1. Create a plot environment
        with dpg.plot(
            tag="graphPie", label="Fruit Distribution", width=-1, height=-1, show=False
        ):
            dpg.add_plot_legend()

            # 2. Add an X axis and hide its gridlines and ticks
            dpg.add_plot_axis(
                dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True
            )
            dpg.set_axis_limits(dpg.last_item(), 0, 1)

            # 3. Add a Y axis (also hidden) - The pie series must be parented to this axis!
            with dpg.plot_axis(
                dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True
            ) as y_axis:
                dpg.set_axis_limits(y_axis, 0, 1)

                # The data for our slices
                slice_values = [15, 30, 45, 10]
                slice_labels = ["Apples", "Bananas", "Cherries", "Dates"]

                # 4. Add the pie series
                dpg.add_pie_series(
                    x=0.5,  # X center coordinate
                    y=0.5,  # Y center coordinate
                    radius=0.4,  # Size of the pie
                    values=slice_values,
                    labels=slice_labels,
                    normalize=True,  # Automatically calculates percentages
                    format="%.1f%%",  # The text format shown when hovering over slices
                    tag="pieSeries",
                )
        # dpg.add_text("Import Sales Data")
        # # dpg.add_button(label="Refresh Table", callback=refresh_table_callback)
        # with dpg.table(
        #     tag="posData",
        #     show=True,
        #     header_row=True,
        #     resizable=True,
        #     borders_innerV=True,
        #     borders_outerV=True,
        # ):
        #     dpg.add_table_column(label="01", init_width_or_weight=0.25)
        #     dpg.add_table_column(label="02", init_width_or_weight=0.25)
        #     dpg.add_table_column(label="03", init_width_or_weight=0.25)
        #     dpg.add_table_column(label="04", init_width_or_weight=0.25)
