#title bar
TITLE_BAR_COLOR = "#202020"
TITLE_BAR_TEXT_COLOR = "#FFFFFF"
TITLE_BAR_HEIGHT = 25

#background
BACKGROUND_COLOR = "#404040"

#button
BUTTON_COLOR = "#505050"

#entry
ENTRY_COLOR = "#606060"

#text
TEXT_COLOR = "#FFFFFF"

#toolbar
TOOLBAR_COLOR = "#666666"
TOOLBAR_HEIGHT = 25
MENU_COLOR = "#666666"

#selection
SELECTION_COLOR = "#33A1FD"
LAST_SELECTED_COLOR = "#FF0000"
SELECTION_WIDTH = 2
SELECTION_DASH = (3, 2)
SELECTION_PADDING = 3

#nudge steps
NUDGE_SMALL = 1
NUDGE_BIG = 10

#grid
GRID_COLOR = "#888888"
GRID_SIZE = 10

#attributes panel
ATTRIBUTES_PANEL_COLOR = "#666666"
ATTRIBUTES_PANEL_WIDTH = 200

#attributes that can be shown in the attributes panel including the type of widget to display the value with (text field, numeric input, color picker, dropwodn etc.)
ATTRIBUTE_CONFIG = {
    "Label": {
        "type": "label",
        "id": "entry",
        "x": "spinbox",
        "y": "spinbox",
        "width": "spinbox",
        "height": "spinbox",
        "text": "entry",
        "bg": "colorpicker",
        "fg": "colorpicker",
        "anchor": "combobox"
    },
    "Entry": {
        "type": "label",
        "id": "entry",
        "x": "spinbox",
        "y": "spinbox",
        "width": "spinbox",
        "height": "spinbox",
        "bg": "colorpicker",
        "fg": "colorpicker",
        "anchor": "combobox"
    },
    "Button": {
        "type": "label",
        "id": "entry",
        "x": "spinbox",
        "y": "spinbox",
        "width": "spinbox",
        "height": "spinbox",
        "text": "entry",
        "bg": "colorpicker",
        "fg": "colorpicker",
        "anchor": "combobox"
    }
}

#mapping internal attribute names to display names for the attribute panel
DISPLAY_NAMES = {
    "type": "Widget Type:",
    "id": "Widget Name:",
    "x": "X Position:",
    "y": "Y Position:",
    "width": "Width:",
    "height": "Height:",
    "text": "Text:",
    "bg": "BG Color:",
    "fg": "FG Color:",
    "anchor": "Anchor:"
}

#CTRL-Key
CTRL_KEY = 0x0004