from dataclasses import dataclass

@dataclass
class IdCounters:
    label: int = 1
    entry: int = 1
    button: int = 1

    def set_next_label_id(self, next_id: int):
        self.label = next_id

    def set_next_entry_id(self, next_id: int):
        self.entry = next_id

    def set_next_button_id(self, next_id: int):
        self.button = next_id

    def next_label_id(self):
        label_id = f"label{self.label}"
        self.label += 1
        return label_id

    def next_entry_id(self):
        entry_id = f"entry{self.entry}"
        self.entry += 1
        return entry_id

    def next_button_id(self):
        button_id = f"button{self.button}"
        self.button += 1
        return button_id