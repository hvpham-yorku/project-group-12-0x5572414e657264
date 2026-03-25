import dearpygui.dearpygui as dpg

from src.database.database_setup import (
    db,
    StoreTable,
    CustomerTable,
    AisleTable,
    ProductTable,
    CameraTable,
    PathTable,
    CheckoutTable,
    PurchaseTable,
    LogTable,
)
from src.pages import logWindow
from src.logic.dataGenerator import clear_database

WINDOW_TAG = "wipe_database_popup"


def _close_popup() -> None:
    if dpg.does_item_exist(WINDOW_TAG):
        dpg.delete_item(WINDOW_TAG)


def _wipe_database(sender, app_data, user_data) -> None:
    try:
        clear_database()
        logWindow.addLog(0, "Database wiped.")
    except Exception as exc:
        logWindow.addLog(2, f"Database wipe failed: {exc}")
    finally:
        _close_popup()


def open_wipe_database_popup() -> None:
    if dpg.does_item_exist(WINDOW_TAG):
        dpg.show_item(WINDOW_TAG)
        return

    with dpg.window(
        tag=WINDOW_TAG,
        label="Wipe Database",
        modal=True,
        no_resize=True,
        width=420,
        height=170,
    ):
        dpg.add_text("This will permanently delete ALL database data.")
        dpg.add_text("Are you sure you want to continue?")
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Wipe", callback=_wipe_database)
            dpg.add_button(label="Cancel", callback=lambda s, a, u: _close_popup())
