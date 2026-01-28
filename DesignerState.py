from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class DesignerState:
    last_click_coords: Optional[Tuple[int, int]] = None
    drag_start_coords: Optional[Tuple[int, int]] = None
    window_coords: Optional[Tuple[int, int]] = None
    is_dirty: bool = False
    is_deleting: bool = False