#initial values for user theme (can be changed in setup wizard)
user_BACKGROUND_COLOR = "#404040"
user_TITLEBAR_COLOR = "#202020"
user_TITLEBAR_TEXT_COLOR = "#FFFFFF"
user_LABEL_COLOR = "#404040"
user_LABEL_TEXT_COLOR = "#FFFFFF"
user_ENTRY_COLOR = "#606060"
user_ENTRY_TEXT_COLOR = "#FFFFFF"
user_BUTTON_COLOR = "#505050"
user_BUTTON_TEXT_COLOR = "#FFFFFF"

USER_THEME = {
    "background": {
        "color": user_BACKGROUND_COLOR
    },
    "titlebar": {
        "bg": user_TITLEBAR_COLOR,
        "fg": user_TITLEBAR_TEXT_COLOR
    },
    "label": {
        "bg": user_LABEL_COLOR,
        "fg": user_LABEL_TEXT_COLOR
    },
    "entry": {
        "bg": user_ENTRY_COLOR,
        "fg": user_ENTRY_TEXT_COLOR
    },
    "button": {
        "bg": user_BUTTON_COLOR,
        "fg": user_BUTTON_TEXT_COLOR
    }
}

#theme for program theme (static)
program_BACKGROUND_COLOR = "#404040"
program_TITLEBAR_COLOR = "#202020"
program_TITLEBAR_TEXT_COLOR = "#FFFFFF"
program_TOOLBAR_COLOR = "#666666"
program_TOOLBAR_TEXT_COLOR = "#FFFFFF"
program_MENU_COLOR = "#666666"
program_MENU_TEXT_COLOR = "#FFFFFF"
program_ATTRIBUTES_PANEL_COLOR = "#666666"
program_ATTRIBUTES_PANEL_WIDGET_COLOR = "#606060"
program_ATTRIBUTES_PANEL_TEXT_COLOR = "#FFFFFF"
program_GRID_COLOR = "#888888"
program_SELECTION_COLOR = "#33A1FD"
program_LAST_SELECTED_COLOR = "#FF0000"
program_LABEL_COLOR = "#404040"
program_LABEL_TEXT_COLOR = "#FFFFFF"
program_ENTRY_COLOR = "#606060"
program_ENTRY_TEXT_COLOR = "#FFFFFF"
program_BUTTON_COLOR = "#505050"
program_BUTTON_TEXT_COLOR = "#FFFFFF"
program_SCROLLBAR_TROUGH_COLOR = "#303030"
program_SCROLLBAR_BACKGROUND_COLOR = "#666666"
program_SCROLLBAR_ARROW_COLOR = "#000000"
program_SCROLLBAR_BORDER_COLOR = "#000000"

PROGRAM_THEME = {
    "background": {
        "color": program_BACKGROUND_COLOR
    },
    "titlebar": {
        "bg": program_TITLEBAR_COLOR,
        "fg": program_TITLEBAR_TEXT_COLOR
    },
    "toolbar": {
        "bg": program_TOOLBAR_COLOR,
        "fg": program_TOOLBAR_TEXT_COLOR
    },
    "menu": {
        "bg": program_MENU_COLOR,
        "fg": program_MENU_TEXT_COLOR
    },
    "attributes_panel": {
        "color": program_ATTRIBUTES_PANEL_COLOR,
        "widget_color": program_ATTRIBUTES_PANEL_WIDGET_COLOR,
        "text_color": program_ATTRIBUTES_PANEL_TEXT_COLOR
    },
    "grid": {
        "color": program_GRID_COLOR
    },
    "selection": {
        "color": program_SELECTION_COLOR,
        "last_selected_color": program_LAST_SELECTED_COLOR
    },
    "label": {
        "bg": program_LABEL_COLOR,
        "fg": program_LABEL_TEXT_COLOR
    },
    "entry": {
        "bg": program_ENTRY_COLOR,
        "fg": program_ENTRY_TEXT_COLOR
    },
    "button": {
        "bg": program_BUTTON_COLOR,
        "fg": program_BUTTON_TEXT_COLOR
    },
    "scrollbar": {
        "trough_color": program_SCROLLBAR_TROUGH_COLOR,
        "background_color": program_SCROLLBAR_BACKGROUND_COLOR,
        "arrow_color": program_SCROLLBAR_ARROW_COLOR,
        "border_color": program_SCROLLBAR_BORDER_COLOR
    }
}

#constants
MINIMUM_WINDOW_WIDTH = 600
MINIMUM_WINDOW_HEIGHT = 400
MAXIMUM_WINDOW_WIDTH = 1200
MAXIMUM_WINDOW_HEIGHT = 800
MINIMUM_CANVAS_WIDTH = 200
MINIMUM_CANVAS_HEIGHT = 200
MAXIMUM_CANVAS_WIDTH = 5000
MAXIMUM_CANVAS_HEIGHT = 5000
TITLEBAR_HEIGHT = 25
TOOLBAR_HEIGHT = 25
ATTRIBUTES_PANEL_WIDTH = 200
ATTRIBUTES_PANEL_HEIGHT = 500
NUDGE_SMALL = 1
NUDGE_BIG = 10
SELECTION_WIDTH = 2
SELECTION_DASH = (3, 2)
SELECTION_PADDING = 3
GRID_SIZE = 10
CTRL_KEY = 0x0004
DRAG_THRESHOLD = 10
FULL_RENDER_THRESHOLD = 10

CONSTANTS = {
    "window": {
        "min_width": MINIMUM_WINDOW_WIDTH,
        "min_height": MINIMUM_WINDOW_HEIGHT,
        "max_width": MAXIMUM_WINDOW_WIDTH,
        "max_height": MAXIMUM_WINDOW_HEIGHT
    },
    "canvas": {
        "min_width": MINIMUM_CANVAS_WIDTH,
        "min_height": MINIMUM_CANVAS_HEIGHT,
        "max_width": MAXIMUM_CANVAS_WIDTH,
        "max_height": MAXIMUM_CANVAS_HEIGHT
    },
    "titlebar_height": TITLEBAR_HEIGHT,
    "toolbar_height": TOOLBAR_HEIGHT,
    "attributes_panel": {
        "width": ATTRIBUTES_PANEL_WIDTH,
        "height": ATTRIBUTES_PANEL_HEIGHT
    },
    "nudge": {
        "small": NUDGE_SMALL,
        "big": NUDGE_BIG
    },
    "selection": {
        "width": SELECTION_WIDTH,
        "dash": SELECTION_DASH,
        "padding": SELECTION_PADDING
    },
    "grid_size": GRID_SIZE,
    "ctrl_key": CTRL_KEY,
    "drag_threshold": DRAG_THRESHOLD,
    "full_render_threshold": FULL_RENDER_THRESHOLD
}
