from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class RectangleSelectionState:
    is_dragging: bool = False
    is_additive: bool = False
    drag_start_coords: Optional[Tuple[int, int]] = None