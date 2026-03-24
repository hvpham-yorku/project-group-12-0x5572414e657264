import dearpygui.dearpygui as dpg
from src.pages.logWindow import addLog


def display_modal_popup(severityLevel: int, message: str):
    with dpg.popup(
        dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True, tag="modal_id"
    ):
        dpg.add_button(
            label="Ok.... I understand :(",
            callback=lambda: dpg.configure_item("modal_id", show=False),
        )
    addLog(severityLevel, message)
