# TODO Refactor into own class

import dearpygui.dearpygui as dpg


def create_sales_data_window(parent: str):
    with dpg.child_window(
        label="Sales Data From POS",
        parent=parent,
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        dpg.add_text("Import Sales Data")
        # dpg.add_button(label="Refresh Table", callback=refresh_table_callback)
        with dpg.table(
            tag="posData",
            show=True,
            header_row=True,
            resizable=True,
            borders_innerV=True,
            borders_outerV=True,
        ):
            dpg.add_table_column(label="01", init_width_or_weight=0.25)
            dpg.add_table_column(label="02", init_width_or_weight=0.25)
            dpg.add_table_column(label="03", init_width_or_weight=0.25)
            dpg.add_table_column(label="04", init_width_or_weight=0.25)
