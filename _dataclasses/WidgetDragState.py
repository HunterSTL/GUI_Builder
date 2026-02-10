from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class WidgetDragState:
    is_dragging: bool = False
    start_coords: Optional[Tuple[int, int]] = None
    end_coords: Optional[Tuple[int, int]] = None
    last_total_dx: Optional[int] = 0
    last_total_dy: Optional[int] = 0