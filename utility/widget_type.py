from enum import Enum


class WidgetType(Enum):
    """Defines the supported widget types."""
    LABEL = "label"     #string values for widget serialization
    ENTRY = "entry"
    BUTTON = "button"
