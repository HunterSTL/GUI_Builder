from dataclasses import dataclass

from utility import WidgetType, is_non_empty_string, is_valid_hex_color_code, is_valid_integer, is_positive_integer, is_valid_anchor


@dataclass
class BaseWidget:
    """Stores widget data."""
    id: str
    x: int
    y: int
    bg: str
    fg: str
    width: int
    height: int
    anchor: str = "sw"

    @property
    def type(
        self
    ) -> WidgetType:
        raise NotImplementedError

    def __post_init__(
        self
    ) -> None:
        if type(self) is BaseWidget:
            raise ValueError("Widgets - widget creation failed: base type (BaseWidget) cannot be instantiated directly")

    def to_dict(
        self
    ) -> dict[str, str | int]:
        """Serialize the widget to widget data."""
        widget_data = self.__dict__.copy()  #shallow copy is safe because widgets are flat
        widget_data["type"] = self.type.value
        return widget_data

    @classmethod
    def from_dict(
        cls,
        widget_data: dict
    ) -> "BaseWidget":
        """Validate and deserialize widget data into a widget."""
        widget_type = cls._validate_widget_data(widget_data)
        widget_data = widget_data.copy()    #prevents mutating input data
        widget_data.pop("type")             #type is an intrinsic property of the derived widget classes
        return _WIDGET_CLASSES[widget_type](**widget_data)

    @classmethod
    def _validate_widget_data(
        cls,
        widget_data: dict
    ) -> WidgetType:
        """Validate the schema and attribute values of the widget data and return its widget type."""
        #validate schema
        if not isinstance(widget_data, dict):
            raise ValueError("Widgets - widget data deserialization failed: widget data is not a dictionary")

        if "type" not in widget_data:
            raise ValueError("Widgets - widget data deserialization failed: missing required attribute \"type\"")

        raw_type = widget_data["type"]
        try:
            widget_type = WidgetType(raw_type)
        except ValueError:
            raise ValueError(f"Widgets - widget data deserialization failed: invalid type \"{raw_type}\"")

        for attribute in _REQUIRED_COMMON_ATTRIBUTES | _REQUIRED_TYPE_SPECIFIC_ATTRIBUTES[widget_type]:
            if attribute not in widget_data:
                raise ValueError(f"Widgets - widget data deserialization failed: missing required attribute \"{attribute}\"")

        for attribute in widget_data:
            if attribute not in _EXPECTED_COMMON_ATTRIBUTES | _EXPECTED_TYPE_SPECIFIC_ATTRIBUTES[widget_type]:
                raise ValueError(f"Widgets - widget data deserialization failed: invalid attribute set [got unexpected attribute \"{attribute}\"]")

        #validate attribute values
        widget_id = widget_data["id"]
        x = widget_data["x"]
        y = widget_data["y"]
        bg = widget_data["bg"]
        fg = widget_data["fg"]
        width = widget_data["width"]
        height = widget_data["height"]
        anchor = widget_data["anchor"]

        if not is_non_empty_string(widget_id):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid ID \"{widget_id}\"")

        if not is_valid_integer(x):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid X coordinate \"{x}\"")

        if not is_valid_integer(y):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid Y coordinate \"{y}\"")

        if not is_valid_hex_color_code(bg):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid background color \"{bg}\"")

        if not is_valid_hex_color_code(fg):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid foreground color \"{fg}\"")

        if not is_positive_integer(width):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid width \"{width}\"")

        if not is_positive_integer(height):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid height \"{height}\"")

        if not is_valid_anchor(anchor):
            raise ValueError(f"Widgets - widget data deserialization failed: invalid anchor \"{anchor}\"")

        if "text" in _REQUIRED_TYPE_SPECIFIC_ATTRIBUTES[widget_type]:
            text = widget_data["text"]
            if not is_non_empty_string(text):
                raise ValueError(f"Widgets - widget data deserialization failed: invalid text \"{text}\"")

        return widget_type


@dataclass
class LabelWidget(BaseWidget):
    """Stores label widget data."""
    text: str = ""

    @property
    def type(
        self
    ) -> WidgetType:
        return WidgetType.LABEL


@dataclass
class EntryWidget(BaseWidget):
    """Stores entry widget data."""
    @property
    def type(
        self
    ) -> WidgetType:
        return WidgetType.ENTRY


@dataclass
class ButtonWidget(BaseWidget):
    """Stores button widget data."""
    text: str = ""

    @property
    def type(
        self
    ) -> WidgetType:
        return WidgetType.BUTTON


_WIDGET_CLASSES = {
    WidgetType.LABEL: LabelWidget,
    WidgetType.ENTRY: EntryWidget,
    WidgetType.BUTTON: ButtonWidget
}

_REQUIRED_COMMON_ATTRIBUTES = {"type", "id", "x", "y", "bg", "fg", "width", "height", "anchor"}
_REQUIRED_TYPE_SPECIFIC_ATTRIBUTES = {
    WidgetType.LABEL: {"text"},
    WidgetType.ENTRY: set(),
    WidgetType.BUTTON: {"text"}
}
_EXPECTED_COMMON_ATTRIBUTES = _REQUIRED_COMMON_ATTRIBUTES
_EXPECTED_TYPE_SPECIFIC_ATTRIBUTES = _REQUIRED_TYPE_SPECIFIC_ATTRIBUTES
