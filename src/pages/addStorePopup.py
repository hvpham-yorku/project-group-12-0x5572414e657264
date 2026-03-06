import dearpygui.dearpygui as dpg

from src.database.model_managers import add_store
from src.database.models import Store
from src.pages import cameraZoneWindow
from src.pages import logWindow

WINDOW_TAG = "add_store_popup"
NAME_INPUT_TAG = "add_store_name_input"
OWNER_INPUT_TAG = "add_store_owner_input"


def _close_popup() -> None:
    if dpg.does_item_exist(WINDOW_TAG):
        dpg.delete_item(WINDOW_TAG)


def _create_store(sender, app_data, user_data) -> None:
    name = dpg.get_value(NAME_INPUT_TAG).strip()
    owner = dpg.get_value(OWNER_INPUT_TAG).strip()

    if not name:
        logWindow.addLog(1, "Store name is required.")
        return

    try:
        store = add_store(Store(name=name, owner=owner))
        logWindow.addLog(0, f"Created store {store.store_id}: {store.name}")
        cameraZoneWindow.refresh_store_dropdowns()
        _close_popup()
    except Exception as exc:
        logWindow.addLog(2, f"Failed to create store: {exc}")


def open_add_store_popup() -> None:
    if dpg.does_item_exist(WINDOW_TAG):
        dpg.show_item(WINDOW_TAG)
        return

    with dpg.window(
        tag=WINDOW_TAG,
        label="Add Store",
        modal=True,
        no_resize=True,
        width=360,
        height=170,
    ):
        dpg.add_text("Enter store details")
        dpg.add_input_text(label="Store Name", tag=NAME_INPUT_TAG, width=300)
        dpg.add_input_text(label="Owner", tag=OWNER_INPUT_TAG, width=300)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Create", callback=_create_store)
            dpg.add_button(label="Cancel", callback=lambda s, a, u: _close_popup())
