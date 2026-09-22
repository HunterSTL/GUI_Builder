from utility import format_field

from AppState import AppState
from .BaseCommand import Command


class SetGridColor(Command):
    """Encapsulates setting the grid color as an undoable command."""
    def __init__(
        self,
        app_state: AppState,
        new_color: str
    ) -> None:
        self._app_state: AppState = app_state
        self._new_color: str = new_color

        self._previous_color: str = self._app_state.project.grid.color

    def has_effect(
        self
    ) -> bool:
        """Return True if the new color differs from the previous color."""
        return self._new_color != self._previous_color

    def execute(
        self
    ) -> None:
        """Set the grid color to the new value."""
        self._app_state.set_grid_color(
            color=self._new_color
        )

    def undo(
        self
    ) -> None:
        """Restore the previous grid color."""
        self._app_state.set_grid_color(
            color=self._previous_color
        )

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[SetGridColor]",
            format_field(
                label="previous color",
                value=self._previous_color
            ),
            format_field(
                label="new color",
                value=self._new_color
            )
        ]
        return "\n".join(lines)
