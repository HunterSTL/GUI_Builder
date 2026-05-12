from enum import Enum

class WidgetType(Enum):
    """
    Defines the supported widget types.
    """
    LABEL = "Label" #string values for widget serialization
    ENTRY = "Entry"
    BUTTON = "Button"
