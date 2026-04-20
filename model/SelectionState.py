from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SelectionState:
    selected_models: set[str] = field(default_factory=set)
    last_selected_model: Optional[str] = None

    def __repr__(self):
        """called automatically when printing this object"""
        return f"selected models:\t\t{self.selected_models}\nlast selected model:\t{self.last_selected_model}"