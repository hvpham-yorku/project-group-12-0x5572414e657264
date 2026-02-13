import dearpygui.dearpygui as dpg
from datetime import datetime

# TODO ADD A BUTTON TO CLEAR LOGS


class LogWindow:
    """
    Docstring for LogWindow

    This class is reponsible for displaying the logs that the software will display to the user
    """

    def __init__(self, tag: str = "logs") -> None:
        self.tag = tag

    def createWindow(self, parent: str) -> None:
        with dpg.child_window(
            # label="Sales Data From POS",
            parent=parent,
            # width=FRAME_WIDTH,
            # height=FRAME_HEIGHT,
        ):
            with dpg.table(
                tag=self.tag,
                show=True,
                header_row=True,
                resizable=True,
                borders_innerV=True,
                borders_outerV=True,
            ):
                dpg.add_table_column(label="Date", init_width_or_weight=0.33)
                dpg.add_table_column(label="Severity", init_width_or_weight=0.33)
                dpg.add_table_column(label="Message", init_width_or_weight=0.33)

    def addLog(self, severityLevel: int, message: str) -> None:
        """
        Docstring for addLog

        :param severityLevel: the smaller the number, the more severe
        :type severityLevel: int
        :param message: string messsage to display
        :type message: str
        """
        with dpg.table_row(parent=self.tag):
            dpg.add_text(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
            dpg.add_text(severityLevel)
            dpg.add_text(message)
