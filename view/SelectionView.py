import tkinter as tk

from utility import BoundingBox
from utility.AppTheme import SELECTION_COLOR, LAST_SELECTED_COLOR
from utility.Constants import SELECTION_WIDTH, SELECTION_DASH, SELECTION_PADDING


class SelectionView:
    """Renders widget selection outlines and the marquee selection rectangle."""
    def __init__(
        self,
        canvas: tk.Canvas
    ) -> None:
        self._canvas: tk.Canvas = canvas

        self._selection_rectangle_id: int | None = None
        self._selection_outline_ids_by_widget_id: dict[str, int] = {}

    def render_outline_for(
        self,
        widget_id: str,
        bounding_box: BoundingBox,
        is_last_selected: bool
    ) -> None:
        """Create or update the selection outline for the given widget ID."""
        outline_color = LAST_SELECTED_COLOR if is_last_selected else SELECTION_COLOR
        selection_outline_id = self._selection_outline_ids_by_widget_id.get(widget_id)

        if selection_outline_id is None:
            selection_outline_id = self._create_outline_for(widget_id)

        self._update_outline(selection_outline_id, bounding_box, outline_color)

    def delete_outline_for(
        self,
        widget_id: str
    ) -> None:
        """Delete the selection outline for the given widget ID."""
        if widget_id not in self._selection_outline_ids_by_widget_id:
            return

        selection_outline_id = self._selection_outline_ids_by_widget_id.pop(widget_id)
        self._canvas.delete(selection_outline_id)

    def delete_all_outlines(
        self
    ) -> None:
        """Delete all selection outlines."""
        self._canvas.delete("selection_outline")
        self._selection_outline_ids_by_widget_id.clear()

    def render_selection_rectangle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int
    ) -> None:
        """Create or update the marquee selection rectangle using the given canvas coordinates."""
        if self._selection_rectangle_id is None:
            self._selection_rectangle_id = self._canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=SELECTION_COLOR,
                width=SELECTION_WIDTH,
                dash=SELECTION_DASH,
                fill=""
            )
        else:
            self._canvas.coords(self._selection_rectangle_id, x1, y1, x2, y2)

        self._canvas.tag_raise(self._selection_rectangle_id)     #ensures marquee selection rectangle is on top

    def delete_selection_rectangle(
        self
    ) -> None:
        """Delete the marquee selection rectangle."""
        if self._selection_rectangle_id is not None:
            self._canvas.delete(self._selection_rectangle_id)
            self._selection_rectangle_id = None

    def _create_outline_for(
        self,
        widget_id: str
    ) -> int:
        """Create and register a selection outline for the given widget ID, then return its canvas item ID."""
        selection_outline_id = self._canvas.create_rectangle(
            0, 0, 0, 0,
            tags="selection_outline"
        )
        self._selection_outline_ids_by_widget_id[widget_id] = selection_outline_id
        return selection_outline_id

    def _update_outline(
        self,
        selection_outline_id: int,
        bounding_box: BoundingBox,
        outline_color: str
    ) -> None:
        """Update the selection outline using the given bounding box and color."""
        self._canvas.coords(
            selection_outline_id,
            bounding_box.left - SELECTION_PADDING,
            bounding_box.top - SELECTION_PADDING,
            bounding_box.right + SELECTION_PADDING,
            bounding_box.bottom + SELECTION_PADDING
        )

        self._canvas.itemconfig(
            selection_outline_id,
            outline=outline_color,
            width=SELECTION_WIDTH,
            dash=SELECTION_DASH,
            fill=""
        )
