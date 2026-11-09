from dataclasses import dataclass

from utility import is_valid_hex_color_code


@dataclass
class ProjectTheme:
    """Stores the project colors."""
    background_color: str = "#404040"
    label_color: str = "#404040"
    label_text_color: str = "#FFFFFF"
    entry_color: str = "#606060"
    entry_text_color: str = "#FFFFFF"
    button_color: str = "#505050"
    button_text_color: str = "#FFFFFF"

    def to_dict(
        self
    ) -> dict[str, str]:
        """Serialize the project theme to theme data."""
        return {
            "background_color": self.background_color,
            "label_color": self.label_color,
            "label_text_color": self.label_text_color,
            "entry_color": self.entry_color,
            "entry_text_color": self.entry_text_color,
            "button_color": self.button_color,
            "button_text_color": self.button_text_color
        }

    @classmethod
    def from_dict(
        cls,
        theme_data: dict
    ) -> "ProjectTheme":
        """Validate and deserialize theme data into a project theme."""
        cls._validate_theme_data(theme_data)
        return cls(
            background_color=theme_data["background_color"],
            label_color=theme_data["label_color"],
            label_text_color=theme_data["label_text_color"],
            entry_color=theme_data["entry_color"],
            entry_text_color=theme_data["entry_text_color"],
            button_color=theme_data["button_color"],
            button_text_color=theme_data["button_text_color"]
        )

    @classmethod
    def _validate_theme_data(
        cls,
        theme_data: dict
    ) -> None:
        """Validate the schema and attribute values of the theme data."""
        #validate schema
        if not isinstance(theme_data, dict):
            raise ValueError("ProjectTheme - theme data deserialization failed: theme data is not a dictionary")

        for attribute in _REQUIRED_ATTRIBUTES:
            if attribute not in theme_data:
                raise ValueError(f"ProjectTheme - theme data deserialization failed: missing required attribute \"{attribute}\"")

        for attribute in theme_data:
            if attribute not in _EXPECTED_ATTRIBUTES:
                raise ValueError(f"ProjectTheme - theme data deserialization failed: invalid attribute set [got unexpected attribute \"{attribute}\"]")

        #validate attribute values
        theme_attribute_display_names = {
            "background_color": "background color",
            "label_color": "label color",
            "label_text_color": "label text color",
            "entry_color": "entry color",
            "entry_text_color": "entry text color",
            "button_color": "button color",
            "button_text_color": "button text color"
        }

        for attribute, display_name in theme_attribute_display_names.items():
            color = theme_data[attribute]
            if not is_valid_hex_color_code(color):
                raise ValueError(f"ProjectTheme - theme data deserialization failed: invalid {display_name} \"{color}\"")

_REQUIRED_ATTRIBUTES = {"background_color", "label_color", "label_text_color", "entry_color", "entry_text_color", "button_color", "button_text_color"}
_EXPECTED_ATTRIBUTES = _REQUIRED_ATTRIBUTES
