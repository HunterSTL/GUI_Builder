from collections.abc import Iterable

from model import BaseWidget
from utility import format_mapping_changes

from AppState import AppState
from .BaseCommand import Command


class DragWidgets(Command):
    """Encapsulates widget dragging as an undoable command."""
    def __init__(
        self,
        widgets: Iterable[BaseWidget],
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        widgets = tuple(widgets)                                            #freezes iteration order for deterministic undo and redo behaviour
        self._widget_ids: list[str] = [widget.id for widget in widgets]     #storing IDs and retrieving widgets protects against stale widget references

        self._original_positions: dict[str, tuple[int, int]] = {
            widget.id: (widget.x, widget.y)
            for widget in widgets
        }
        self._final_positions: dict[str, tuple[int, int]] = {}

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one widget position."""
        if not self._final_positions:
            raise ValueError("DragWidgets - effect check failed: final positions were not recorded")

        return any(
            self._original_positions[widget_id] != self._final_positions[widget_id]
            for widget_id in self._widget_ids
        )

    def apply_drag_delta(
        self,
        dx: int,
        dy: int
    ) -> None:
        """Apply incremental drag movement to the widgets through AppState."""
        if dx == 0 and dy == 0:         #incremental deltas since last drag event
            return

        with self._app_state.batch():
            for widget_id in self._widget_ids:
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                self._app_state.offset_widget_position(widget, dx, dy)

    def record_final_positions(
        self
    ) -> None:
        """Record final positions."""
        final_positions = {}

        for widget_id in self._widget_ids:
            widget = self._app_state.get_widget_from_widget_id(widget_id)
            final_positions[widget_id] = (widget.x, widget.y)

        self._final_positions = final_positions

    def execute(
        self
    ) -> None:
        """Apply the snapshotted final positions to the widgets through AppState."""
        if not self._final_positions:
            raise ValueError("DragWidgets - execution failed: final positions were not recorded")

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
        lines = [
            "[DragWidgets]",
            format_mapping_changes(
                label="positions",
                before_mapping=self._original_positions,
                after_mapping=self._final_positions
            )
        ]
        return "\n".join(lines)
