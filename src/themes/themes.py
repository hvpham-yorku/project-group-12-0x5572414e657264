from typing import List, Any, Callable, Union, Tuple
import dearpygui.dearpygui as dpg

# inspired from https://www.reddit.com/r/DearPyGui/comments/x8l9g4/pre_built_themes/
# inspired from https://github.com/hoffstadt/DearPyGui_Ext/blob/master/dearpygui_ext/themes.py


def create_theme_dark() -> Union[str, int]:

    with dpg.theme() as theme_id:
        with dpg.theme_component(0):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (255, 255, 255, 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TextDisabled,
                (127, 127, 127, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_WindowBg,
                (15, 15, 15, 239),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ChildBg, (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PopupBg, (0.08 * 255, 0.08 * 255, 0.08 * 255, 239)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Border, (0.43 * 255, 0.43 * 255, 127, 127)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_BorderShadow,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBg, (0.16 * 255, 0.29 * 255, 0.48 * 255, 0.54 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgHovered,
                (66, 150, 249, 0.40 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgActive,
                (66, 150, 249, 0.67 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBg, (0.04 * 255, 0.04 * 255, 0.04 * 255, 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBgActive,
                (0.16 * 255, 0.29 * 255, 0.48 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBgCollapsed,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.51 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_MenuBarBg,
                (0.14 * 255, 0.14 * 255, 0.14 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarBg,
                (0.02 * 255, 0.02 * 255, 0.02 * 255, 0.53 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarGrab,
                (0.31 * 255, 0.31 * 255, 0.31 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarGrabHovered,
                (0.41 * 255, 0.41 * 255, 0.41 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarGrabActive,
                (0.51 * 255, 0.51 * 255, 0.51 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_CheckMark,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SliderGrab,
                (0.24 * 255, 0.52 * 255, 0.88 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SliderGrabActive,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Button, (66, 150, 249, 0.40 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,
                (15, 0.53 * 255, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Header, (66, 150, 249, 0.31 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderHovered,
                (66, 150, 249, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderActive,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Separator,
                (0.43 * 255, 0.43 * 255, 127, 127),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SeparatorHovered,
                (0.10 * 255, 0.40 * 255, 0.75 * 255, 0.78 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SeparatorActive,
                (0.10 * 255, 0.40 * 255, 0.75 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ResizeGrip,
                (66, 150, 249, 0.20 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ResizeGripHovered,
                (66, 150, 249, 0.67 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ResizeGripActive,
                (66, 150, 249, 0.95 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Tab, (0.18 * 255, 0.35 * 255, 0.58 * 255, 0.86 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabHovered,
                (66, 150, 249, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabActive,
                (0.20 * 255, 0.41 * 255, 0.68 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabUnfocused,
                (0.07 * 255, 0.10 * 255, 0.15 * 255, 0.97 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabUnfocusedActive,
                (0.14 * 255, 66, 0.42 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_DockingPreview,
                (66, 150, 249, 0.70 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_DockingEmptyBg,
                (0.20 * 255, 0.20 * 255, 0.20 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotLines,
                (0.61 * 255, 0.61 * 255, 0.61 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotLinesHovered,
                (255, 0.43 * 255, 0.35 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotHistogram,
                (0.90 * 255, 0.70 * 255, 0.00 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotHistogramHovered,
                (255, 0.60 * 255, 0.00 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableHeaderBg,
                (0.19 * 255, 0.19 * 255, 0.20 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableBorderStrong,
                (0.31 * 255, 0.31 * 255, 0.35 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableBorderLight,
                (0.23 * 255, 0.23 * 255, 0.25 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableRowBg,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableRowBgAlt,
                (255, 255, 255, 15),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TextSelectedBg,
                (66, 150, 249, 0.35 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_DragDropTarget,
                (255, 255, 0.00 * 255, 0.90 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_NavHighlight,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_NavWindowingHighlight,
                (255, 255, 255, 0.70 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_NavWindowingDimBg,
                (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.20 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ModalWindowDimBg,
                (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.35 * 255),
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_FrameBg,
                (255, 255, 255, 0.07 * 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_PlotBg,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 127),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_PlotBorder,
                (0.43 * 255, 0.43 * 255, 127, 127),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_LegendBg,
                (0.08 * 255, 0.08 * 255, 0.08 * 255, 239),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_LegendBorder,
                (0.43 * 255, 0.43 * 255, 127, 127),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_LegendText,
                (255, 255, 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_TitleText,
                (255, 255, 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_InlayText,
                (255, 255, 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisBg,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisBgActive,
                (15, 0.53 * 255, 249, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisBgHovered,
                (66, 150, 249, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisGrid,
                (255, 255, 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisText,
                (255, 255, 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_Selection,
                (255, 0.60 * 255, 0.00 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_Crosshairs,
                (255, 255, 255, 127),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackground,
                (50, 50, 50, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackgroundHovered,
                (75, 75, 75, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackgroundSelected,
                (75, 75, 75, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeOutline,
                (100, 100, 100, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBar,
                (41, 74, 122, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBarHovered,
                (66, 150, 250, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBarSelected,
                (66, 150, 250, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_Link, (61, 133, 224, 200), category=dpg.mvThemeCat_Nodes
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_LinkHovered,
                (66, 150, 250, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_LinkSelected,
                (66, 150, 250, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_Pin, (53, 150, 250, 180), category=dpg.mvThemeCat_Nodes
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_PinHovered,
                (53, 150, 250, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_BoxSelector,
                (61, 133, 224, 30),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_BoxSelectorOutline,
                (61, 133, 224, 150),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_GridBackground,
                (40, 40, 50, 200),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_GridLine,
                (200, 200, 200, 40),
                category=dpg.mvThemeCat_Nodes,
            )

    return theme_id


def create_theme_light() -> Union[str, int]:

    with dpg.theme() as theme_id:
        with dpg.theme_component(0):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (0.00 * 255, 0.00 * 255, 0.00 * 255, 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TextDisabled,
                (0.60 * 255, 0.60 * 255, 0.60 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_WindowBg,
                (239, 239, 239, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ChildBg, (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PopupBg, (255, 255, 255, 249)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Border, (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.30 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_BorderShadow,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBg, (255, 255, 255, 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgHovered,
                (66, 150, 249, 0.40 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBgActive,
                (66, 150, 249, 0.67 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBg, (0.96 * 255, 0.96 * 255, 0.96 * 255, 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBgActive,
                (0.82 * 255, 0.82 * 255, 0.82 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBgCollapsed,
                (255, 255, 255, 0.51 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_MenuBarBg,
                (0.86 * 255, 0.86 * 255, 0.86 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarBg,
                (249, 249, 249, 0.53 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarGrab,
                (0.69 * 255, 0.69 * 255, 0.69 * 255, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarGrabHovered,
                (0.49 * 255, 0.49 * 255, 0.49 * 255, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ScrollbarGrabActive,
                (0.49 * 255, 0.49 * 255, 0.49 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_CheckMark,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SliderGrab,
                (66, 150, 249, 0.78 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SliderGrabActive,
                (0.46 * 255, 0.54 * 255, 0.80 * 255, 0.60 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Button, (66, 150, 249, 0.40 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive,
                (15, 0.53 * 255, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Header, (66, 150, 249, 0.31 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderHovered,
                (66, 150, 249, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_HeaderActive,
                (66, 150, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Separator,
                (0.39 * 255, 0.39 * 255, 0.39 * 255, 0.62 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SeparatorHovered,
                (0.14 * 255, 0.44 * 255, 0.80 * 255, 0.78 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_SeparatorActive,
                (0.14 * 255, 0.44 * 255, 0.80 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ResizeGrip,
                (0.35 * 255, 0.35 * 255, 0.35 * 255, 0.17 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ResizeGripHovered,
                (66, 150, 249, 0.67 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ResizeGripActive,
                (66, 150, 249, 0.95 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_Tab, (0.76 * 255, 0.80 * 255, 0.84 * 255, 0.93 * 255)
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabHovered,
                (66, 150, 249, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabActive,
                (0.60 * 255, 0.73 * 255, 0.88 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabUnfocused,
                (0.92 * 255, 0.93 * 255, 239, 0.99 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TabUnfocusedActive,
                (0.74 * 255, 0.82 * 255, 0.91 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_DockingPreview,
                (66, 150, 249, 0.22 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_DockingEmptyBg,
                (0.20 * 255, 0.20 * 255, 0.20 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotLines,
                (0.39 * 255, 0.39 * 255, 0.39 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotLinesHovered,
                (255, 0.43 * 255, 0.35 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotHistogram,
                (0.90 * 255, 0.70 * 255, 0.00 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_PlotHistogramHovered,
                (255, 0.45 * 255, 0.00 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableHeaderBg,
                (0.78 * 255, 0.87 * 255, 249, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableBorderStrong,
                (0.57 * 255, 0.57 * 255, 0.64 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableBorderLight,
                (0.68 * 255, 0.68 * 255, 0.74 * 255, 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableRowBg,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TableRowBgAlt,
                (0.30 * 255, 0.30 * 255, 0.30 * 255, 0.09 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TextSelectedBg,
                (66, 150, 249, 0.35 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_DragDropTarget,
                (66, 150, 249, 0.95 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_NavHighlight,
                (66, 150, 249, 0.80 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_NavWindowingHighlight,
                (0.70 * 255, 0.70 * 255, 0.70 * 255, 0.70 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_NavWindowingDimBg,
                (0.20 * 255, 0.20 * 255, 0.20 * 255, 0.20 * 255),
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ModalWindowDimBg,
                (0.20 * 255, 0.20 * 255, 0.20 * 255, 0.35 * 255),
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_FrameBg,
                (255, 255, 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_PlotBg,
                (0.42 * 255, 0.57 * 255, 255, 0.13 * 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_PlotBorder,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_LegendBg,
                (255, 255, 255, 249),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_LegendBorder,
                (0.82 * 255, 0.82 * 255, 0.82 * 255, 0.80 * 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_LegendText,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_TitleText,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_InlayText,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisBg,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisBgActive,
                (15, 0.53 * 255, 249, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisBgHovered,
                (66, 150, 249, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisGrid,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_AxisText,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_Selection,
                (0.82 * 255, 0.64 * 255, 0.03 * 255, 255),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvPlotCol_Crosshairs,
                (0.00 * 255, 0.00 * 255, 0.00 * 255, 127),
                category=dpg.mvThemeCat_Plots,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackground,
                (240, 240, 240, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackgroundHovered,
                (240, 240, 240, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeBackgroundSelected,
                (240, 240, 240, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_NodeOutline,
                (100, 100, 100, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBar,
                (248, 248, 248, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBarHovered,
                (209, 209, 209, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBarSelected,
                (209, 209, 209, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_Link, (66, 150, 250, 100), category=dpg.mvThemeCat_Nodes
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_LinkHovered,
                (66, 150, 250, 242),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_LinkSelected,
                (66, 150, 250, 242),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_Pin, (66, 150, 250, 160), category=dpg.mvThemeCat_Nodes
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_PinHovered,
                (66, 150, 250, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_BoxSelector,
                (90, 170, 250, 30),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_BoxSelectorOutline,
                (90, 170, 250, 150),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_GridBackground,
                (225, 225, 225, 255),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_GridLine,
                (180, 180, 180, 100),
                category=dpg.mvThemeCat_Nodes,
            )

    return theme_id


def create_theme_default() -> Union[str, int]:
    with dpg.theme() as theme_id:
        with dpg.theme_component(0):
            # Set text color
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))  # White text
            # Set button color
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 122, 204))  # Blue button
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered, (0, 150, 255)
            )  # Lighter blue on hover
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonActive, (0, 92, 184)
            )  # Darker blue on click
            # Set window background color
            dpg.add_theme_color(
                dpg.mvThemeCol_WindowBg, (45, 45, 48)
            )  # Dark gray background
            # Set frame rounding (makes buttons and other widgets rounded)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
    return theme_id


def create_theme_retro() -> Union[str, int]:
    with dpg.theme() as theme_id:
        with dpg.theme_component(0):
            # Neon green text
            dpg.add_theme_color(dpg.mvThemeCol_Text, (57, 255, 20))
            # Black window background with a subtle grid-like pattern
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 20))
            # Retro-style button color (electric blue)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 110, 255))
            # Lighter blue on hover to simulate a glowing effect
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 150, 255))
            # Magenta on active to imitate the click feedback in retro consoles
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 0, 255))
            # Frame rounding for a slight retro curve
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
            # Add a subtle grid-like effect with border colors
            dpg.add_theme_color(dpg.mvThemeCol_Border, (85, 85, 85))
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            # Scrollbar to have a glowing neon effect
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (25, 25, 25))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (0, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (255, 255, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (255, 20, 147))
            # Retro-style header colors
            dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 255, 127))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (255, 165, 0))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (255, 69, 0))
            # Text entry fields with a subtle blue tint
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 50))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (40, 40, 70))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (50, 50, 90))
            # Plot lines to simulate retro graph paper
            dpg.add_theme_color(dpg.mvThemeCol_PlotLines, (0, 255, 0))
            dpg.add_theme_color(dpg.mvThemeCol_PlotLinesHovered, (255, 0, 0))
    return theme_id
