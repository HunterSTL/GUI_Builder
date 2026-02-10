from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    #this import is only used by the type checker and discarded at runtime
    from _commands import MoveWidgetsTo

@dataclass
class DesignerState:
    last_click_coords: Optional[Tuple[int, int]] = None         #last right click coords for adding new widgets
    drag_start_coords: Optional[Tuple[int, int]] = None         #drag start coords for moving the designer window
    window_coords: Optional[Tuple[int, int]] = None             #current designer window coords
    is_dirty: bool = False
    is_deleting: bool = False
    active_widget_drag_command: Optional["MoveWidgetsTo"] = None  #MoveWidgetsTo command while dragging widgets