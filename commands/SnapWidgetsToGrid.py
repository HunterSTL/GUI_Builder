from collections.abc import Iterable

from model import BaseWidget
from utility import allowed_x_range, allowed_y_range, nearest_in_bounds_grid_step, format_mapping_changes

from AppState import AppState
from .BaseCommand import Command


class SnapWidgetsToGrid(Command):
    """Encapsulates widget grid snapping as an undoable command."""
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
        for widget in widgets:
            min_x, max_x = allowed_x_range(self._app_state.project.width, widget.width, widget.anchor)
            min_y, max_y = allowed_y_range(self._app_state.project.height, widget.height, widget.anchor)
            new_x = nearest_in_bounds_grid_step(widget.x, self._app_state.project.grid.size, min_x, max_x)
            new_y = nearest_in_bounds_grid_step(widget.y, self._app_state.project.grid.size, min_y, max_y)
            self._final_positions[widget.id] = (new_x, new_y)

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one widget position."""
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
        lines = [
            "[SnapWidgetsToGrid]",
            format_mapping_changes(
                label="positions",
                before_mapping=self._original_positions,
                after_mapping=self._final_positions
            )
        ]
        return "\n".join(lines)
