from dataclasses import dataclass, field

@dataclass
class SelectionState:
    selected_model_ids: set[str] = field(default_factory=set)
    last_selected_model_id: str | None = None

    def __repr__(self):
        """called automatically when printing this object"""
        return f"selected model IDs:\t\t{self.selected_model_ids}\nlast selected model ID:\t{self.last_selected_model_id}"
