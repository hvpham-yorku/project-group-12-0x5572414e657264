import dearpygui.dearpygui as dpg
from src.themes.themes import *
from src.pages import salesDataWindow, dataAnalyticsWindow
from src.pages import logWindow

TOP_RATIO = 0.75  # top row = 35% of viewport height
GAP = 0  # optional spacing between rows (px)


def on_resize(sender, app_data):
    vh = dpg.get_viewport_client_height()
    top_h = max(50, int(vh * TOP_RATIO))  # min height safety

    dpg.configure_item("top_row", height=top_h)
    # bottom_row uses height=-1 so it fills whatever remains


def mainWindow(tag: str):
    """
    Docstring for mainWindow
    Initializes the main background window

    :param tag: The global tag name for this page
    :type tag: str
    """
    dpg.set_viewport_resize_callback(on_resize)  # does automatic reflow

    with dpg.window(tag=tag):

        # TOP
        with dpg.child_window(tag="top_row", width=-1, height=550, border=True):
            pass
        # BOTTOM
        with dpg.child_window(tag="bottom_row", width=-1, height=-1, border=True):
            dpg.add_text("Logs")
            logWindow.createWindow("bottom_row")

        with dpg.table(
            parent="top_row", resizable=True, policy=dpg.mvTable_SizingStretchProp
        ):
            dpg.add_table_column(label="Data Selection")
            dpg.add_table_column(label="Graph Window")

            with dpg.table_row():
                with dpg.table_cell(tag="dataSelection"):  # LEFT PANEL
                    dataAnalyticsWindow.create_data_analytics_window("temp")
                    # with dpg.child_window(border=True):
                    #     dpg.add_text("Empty Window")
                with dpg.table_cell(tag="graphPlot"):  # RIGHT PANEL
                    with dpg.plot(
                        tag="graphPie",
                        label="Fruit Distribution",
                        width=-1,
                        height=-1,
                        show=False,
                    ):
                        dpg.add_plot_legend()

                        # 2. Add an X axis and hide its gridlines and ticks
                        dpg.add_plot_axis(
                            dpg.mvXAxis,
                            no_gridlines=True,
                            no_tick_marks=True,
                            no_tick_labels=True,
                        )
                        dpg.set_axis_limits(dpg.last_item(), 0, 1)

                        # 3. Add a Y axis (also hidden) - The pie series must be parented to this axis!
                        with dpg.plot_axis(
                            dpg.mvYAxis,
                            no_gridlines=True,
                            no_tick_marks=True,
                            no_tick_labels=True,
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
                    # salesDataWindow.create_sales_data_window("posDataCell")
