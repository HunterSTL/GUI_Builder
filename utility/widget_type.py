from enum import Enum


class WidgetType(Enum):
    """Defines the supported widget types."""
    LABEL = "label"     #string values for widget serialization
    ENTRY = "entry"
    BUTTON = "button"

    @property
    def supports_text(
        self
    ) -> bool:
        return self in {WidgetType.LABEL, WidgetType.BUTTON}
