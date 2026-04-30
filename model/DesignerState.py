from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class DesignerState:
    last_click_coords: Optional[Tuple[int, int]] = None         #last right click coords for adding new widgets
    is_dirty: bool = False