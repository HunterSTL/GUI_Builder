from collections.abc import Iterable

from model import BaseWidget
from utility import format_field

from AppState import AppState
from .BaseCommand import Command


class NudgeWidgets(Command):
    """Encapsulates widget nudging as an undoable command."""
    def __init__(
        self,
        widgets: Iterable[BaseWidget],
        dx: int,
        dy: int,
        app_state: AppState
    ) -> None:
        self._dx: int = dx
        self._dy: int = dy
        self._app_state: AppState = app_state

        widgets = tuple(widgets)                                            #freezes iteration order for deterministic undo and redo behaviour
        self._widget_ids: list[str] = [widget.id for widget in widgets]     #storing IDs and retrieving widgets protects against stale widget references

        self._original_positions: dict[str, tuple[int, int]] = {
            widget.id: (widget.x, widget.y)
            for widget in widgets
        }

        self._final_positions: dict[str, tuple[int, int]] = {}
        for widget in widgets:
            self._final_positions[widget.id] = (widget.x + self._dx, widget.y + self._dy)

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
            "[NudgeWidgets]",
            format_field(
                label="ids",
                value=self._widget_ids
            ),
            format_field(
                label="delta",
                value=f"({self._dx}, {self._dy})"
            )
        ]
        return "\n".join(lines)
