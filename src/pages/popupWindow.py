import dearpygui.dearpygui as dpg
from src.pages.logWindow import addLog, _play_customSound


def instantiate_popup():
    with dpg.window(
        tag="my_reusable_modal",
        modal=True,
        show=False,
        pos=[150, 150],
        # width=FRAME_WIDTH,
        # height=FRAME_HEIGHT,
    ):
        dpg.add_text("LOREN IPSUM", tag="modal_message_text")
        dpg.add_button(
            label="Ok.... I understand :(",
            callback=lambda: dpg.configure_item("my_reusable_modal", show=False),
        )


def callback_hidePopup():
    dpg.configure_item("my_reusable_modal", show=False)


# def display_modal_popup(severityLevel: int, message: str):
#     # dpg.configure_app("modal_id", show=True)
#     with dpg.popup(
#         dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True, tag="modal_id"
#     ):
#         dpg.add_button(
#             label="Ok.... I understand :(",
#             callback=lambda: dpg.configure_item("modal_id", show=False),
#         )
#     addLog(severityLevel, message)
#     _play_customSound()


def display_modal_popup(severityLevel: int, message: str):
    # 1. Update the text inside the modal
    dpg.configure_item("modal_message_text", default_value=message)

    # 2. Make the modal visible
    dpg.configure_item("my_reusable_modal", show=True)

    # 3. Run your background tasks
    addLog(severityLevel, message)
