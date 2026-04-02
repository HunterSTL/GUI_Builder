from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SelectionState:
    #selection set
    selected_models: set[str] = field(default_factory=set)
    last_selected_model: Optional[str] = None