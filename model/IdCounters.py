from dataclasses import dataclass

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

    def next_label_id(self):
        label_id = f"label_{self.label}"
        self.label += 1
        return label_id

    def next_entry_id(self):
        entry_id = f"entry_{self.entry}"
        self.entry += 1
        return entry_id

    def next_button_id(self):
        button_id = f"button_{self.button}"
        self.button += 1
        return button_id

    def __repr__(self):
        lines = []
        for counter, value in self.__dict__.items():
            lines.append(f"{counter}:\t{value}")
        return "\n".join(lines)
