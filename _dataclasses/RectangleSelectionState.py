from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class RectangleSelectionState:
    selection_rectangle_id: Optional[int] = None
    start_coords: Optional[Tuple[int, int]] = None
    is_dragging: bool = False
    is_additive: bool = False