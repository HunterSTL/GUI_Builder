from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    #this import is only used by the type checker and discarded at runtime
    from commands import MoveWidgetsTo

@dataclass
class DesignerState:
    last_click_coords: Optional[Tuple[int, int]] = None         #last right click coords for adding new widgets
    is_dirty: bool = False
    is_deleting: bool = False
    active_widget_drag_command: Optional["MoveWidgetsTo"] = None  #MoveWidgetsTo command while dragging widgets