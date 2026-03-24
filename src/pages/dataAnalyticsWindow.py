# TODO Refactor into own class maybe?

import dearpygui.dearpygui as dpg


def callback_update_pie_chart(sender, app_data, user_data):
    pass


def callback_save_checked_boxes(sender, app_data, user_data):
    print()


def create_data_analytics_window(parent: str):
    with dpg.child_window(
        label="Sales Data From POS",
        parent=parent,
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        with dpg.group(horizontal=True):
            dpg.add_combo(
                ["Select Chart Type", "Pie Chart", "Line Chart"],
                label="Chart Type",
                default_value="Select Chart Type",
                tag="chart_dropdown",
            )
        # with dpg.group(horizontal=True):
        with dpg.table(
            tag="dataSelectorOfSelector",
            policy=dpg.mvTable_SizingStretchProp,
            borders_innerV=True,
        ):
            dpg.add_table_column(label="Count", init_width_or_weight=0.5)
            dpg.add_table_column(label="Category", init_width_or_weight=0.5)
            with dpg.table_row(parent="dataSelectorOfSelector"):
                with dpg.table(
                    tag="dataSelector",
                    label="dataSelector",
                    show=True,
                ):
                    dpg.add_table_column()
                    # dpg.add_table_column(label="Categories", init_width_or_weight=0.5)
                    with dpg.table_row(parent="multipleSelector"):
                        # dpg.add_text("test")
                        dpg.add_radio_button(
                            label="testing",
                            items=["test1", "test2"],
                            callback=callback_save_checked_boxes,
                        )
                with dpg.table(
                    tag="dataSelector2",
                    label="dataSelector",
                    show=True,
                ):
                    dpg.add_table_column()
                    # dpg.add_table_column(label="Categories", init_width_or_weight=0.5)
                    with dpg.table_row(parent="multipleSelector2"):
                        # dpg.add_text("test")
                        dpg.add_checkbox(
                            callback=callback_save_checked_boxes,
                            default_value=False,
                        )
                        dpg.add_checkbox(
                            callback=callback_save_checked_boxes,
                            default_value=False,
                        )
                        dpg.add_checkbox(
                            callback=callback_save_checked_boxes,
                            default_value=False,
                        )

        dpg.add_button(label="Update Chart", callback=callback_update_pie_chart)
        # 1. Create a plot environment
        with dpg.plot(label="Fruit Distribution", width=-1, height=-1):
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
