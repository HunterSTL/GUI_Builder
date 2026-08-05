from dataclasses import dataclass

from utility import WidgetType, is_positive_integer


@dataclass
class IdCounters:
    """Stores ID counter values."""
    label: int = 1  #represents the next counter value that will be used for the ID generation
    entry: int = 1
    button: int = 1

    def to_dict(
        self
    ) -> dict[str, int]:
        """Serialize the ID counter values to ID counter data."""
        return {
            "label": self.label,
            "entry": self.entry,
            "button": self.button
        }

    @classmethod
    def from_dict(
        cls,
        id_counter_data: dict
    ) -> "IdCounters":
        """Validate and deserialize ID counter data into an ID counters instance."""
        cls._validate_id_counter_data(id_counter_data)
        return cls(
            label=id_counter_data["label"],
            entry=id_counter_data["entry"],
            button=id_counter_data["button"]
        )

    def generate_id(
        self,
        widget_type: WidgetType
    ) -> str:
        """Generate a unique ID for the given widget type."""
        if widget_type == WidgetType.LABEL:
            model_id = f"label_{self.label}"
            self.label += 1
            return model_id

        if widget_type == WidgetType.ENTRY:
            model_id = f"entry_{self.entry}"
            self.entry += 1
            return model_id

        if widget_type == WidgetType.BUTTON:
            model_id = f"button_{self.button}"
            self.button += 1
            return model_id

        raise ValueError(f"IdCounters - ID generation failed: unsupported type \"{widget_type}\"")

    @classmethod
    def _validate_id_counter_data(
        cls,
        id_counter_data: dict
    ) -> None:
        """Validate the schema and attribute values of the ID counter data."""
        #validate schema
        if not isinstance(id_counter_data, dict):
            raise ValueError("IdCounters - ID counter data deserialization failed: ID counter data is not a dictionary")

        for attribute in _REQUIRED_ATTRIBUTES:
            if attribute not in id_counter_data:
                raise ValueError(f"IdCounters - ID counter data deserialization failed: missing required attribute \"{attribute}\"")

        for attribute in id_counter_data:
            if attribute not in _EXPECTED_ATTRIBUTES:
                raise ValueError(f"IdCounters - ID counter data deserialization failed: invalid attribute set [got unexpected attribute \"{attribute}\"]")

        #validate attribute values
        label = id_counter_data["label"]
        entry = id_counter_data["entry"]
        button = id_counter_data["button"]

        if not is_positive_integer(label):
            raise ValueError(f"IdCounters - ID counter data deserialization failed: invalid label ID counter value \"{label}\"")

        if not is_positive_integer(entry):
            raise ValueError(f"IdCounters - ID counter data deserialization failed: invalid entry ID counter value \"{entry}\"")

        if not is_positive_integer(button):
            raise ValueError(f"IdCounters - ID counter data deserialization failed: invalid button ID counter value \"{button}\"")

    def __repr__(
        self
    ) -> str:
        lines = []
        for counter, value in self.__dict__.items():
            lines.append(f"{counter}:\t{value}")
        return "\n".join(lines)


_REQUIRED_ATTRIBUTES = {"label", "entry", "button"}
_EXPECTED_ATTRIBUTES = _REQUIRED_ATTRIBUTES
