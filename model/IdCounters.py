from dataclasses import dataclass

from utility import WidgetType

MINIMUM_COUNTER_VALUE = 1

@dataclass
class IdCounters:
    label: int = 1  #represents the next counter value that will be used for the ID generation
    entry: int = 1
    button: int = 1

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "entry": self.entry,
            "button": self.button
        }

    @classmethod
    def from_dict(cls, id_counter_data: dict) -> "IdCounters":
        def _parse_counter_value(value):
            try:
                value = int(value)
            except (TypeError, ValueError):
                return MINIMUM_COUNTER_VALUE
            return max(value, MINIMUM_COUNTER_VALUE)

        id_counter_data = id_counter_data or {} #fallback to default values if empty
        return IdCounters(
            label=_parse_counter_value(id_counter_data.get("label")),
            entry=_parse_counter_value(id_counter_data.get("entry")),
            button=_parse_counter_value(id_counter_data.get("button"))
        )

    def generate_id(self, widget_type: WidgetType) -> str:
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

    def __repr__(self):
        lines = []
        for counter, value in self.__dict__.items():
            lines.append(f"{counter}:\t{value}")
        return "\n".join(lines)
