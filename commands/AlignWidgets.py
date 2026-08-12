from collections.abc import Iterable

from model import BaseWidget
from utility import Edge, BoundingBox, clamped_delta

from AppState import AppState
from .BaseCommand import Command


class AlignWidgets(Command):
    """Encapsulates widget alignment as an undoable command."""
    def __init__(
        self,
        widgets: Iterable[BaseWidget],
        reference_widget_id: str,
        edge: Edge,
        app_state: AppState
    ) -> None:
        self._reference_widget_id: str = reference_widget_id
        self._edge: Edge = edge
        self._app_state: AppState = app_state

        widgets = tuple(widgets)                                            #freezes iteration order for deterministic undo and redo behaviour
        self._widget_ids: list[str] = [widget.id for widget in widgets]     #storing IDs and retrieving widgets protects against stale widget references

        reference_widget = self._app_state.get_widget_from_widget_id(reference_widget_id)
        self._reference_widget_bbox: BoundingBox = self._app_state.get_widget_bounding_box(reference_widget)

        self._original_positions: dict[str, tuple[int, int]] = {
            widget.id: (widget.x, widget.y)
            for widget in widgets
        }

        self._final_positions: dict[str, tuple[int, int]] = {}
        for widget in widgets:
            if widget.id != self._reference_widget_id:
                widget_bbox = self._app_state.get_widget_bounding_box(widget)

                if self._edge == Edge.LEFT:
                    dx, dy = self._reference_widget_bbox.left - widget_bbox.left, 0
                elif self._edge == Edge.RIGHT:
                    dx, dy = self._reference_widget_bbox.right - widget_bbox.right, 0
                elif self._edge == Edge.TOP:
                    dx, dy = 0, self._reference_widget_bbox.top - widget_bbox.top
                elif self._edge == Edge.BOTTOM:
                    dx, dy = 0, self._reference_widget_bbox.bottom - widget_bbox.bottom
                else:
                    dx, dy = 0, 0
            else:
                dx, dy = 0, 0

            dx, dy = clamped_delta(     #keeps widgets within canvas bounds
                canvas_width=self._app_state.project.width,
                canvas_height=self._app_state.project.height,
                bounding_box=self._app_state.get_widget_bounding_box(widget),
                dx=dx,
                dy=dy
            )

            original_x, original_y = self._original_positions[widget.id]
            self._final_positions[widget.id] = (original_x + dx, original_y + dy)

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one widget's position."""
        return any(
            self._original_positions[widget_id] != self._final_positions[widget_id]
            for widget_id in self._widget_ids
        )

    def execute(
        self
    ) -> None:
        """Apply the snapshotted final positions to the widgets through AppState."""
        with self._app_state.batch():
            for widget_id, (x, y) in self._final_positions.items():
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                self._app_state.set_widget_position(widget, x, y)

    def undo(
        self
    ) -> None:
        """Restore the snapshotted original positions to the widgets through AppState."""
        with self._app_state.batch():
            for widget_id, (x, y) in self._original_positions.items():
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                self._app_state.set_widget_position(widget, x, y)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[AlignWidgets]"
        s += f"\n\twidget IDs:\t\t\t{self._widget_ids}"
        s += f"\n\treference widget ID:\t{self._reference_widget_id}"
        s += f"\n\tedge:\t\t\t\t{self._edge}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s
