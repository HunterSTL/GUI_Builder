from utility import format_field

from AppState import AppState
from .BaseCommand import Command


class SetGridSize(Command):
    """Encapsulates setting the grid size as an undoable command."""
    def __init__(
        self,
        app_state: AppState,
        new_size: int
    ) -> None:
        self._app_state: AppState = app_state
        self._new_size: int = new_size

        self._previous_size: int = self._app_state.project.grid.size

    def has_effect(
        self
    ) -> bool:
        """Return True if the new size differs from the previous size."""
        return self._new_size != self._previous_size

    def execute(
        self
    ) -> None:
        """Set the grid size to the new value."""
        self._app_state.set_grid_size(
            size=self._new_size
        )

    def undo(
        self
    ) -> None:
        """Restore the previous grid size."""
        self._app_state.set_grid_size(
            size=self._previous_size
        )

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[SetGridSize]",
            format_field(
                label="previous size",
                value=self._previous_size
            ),
            format_field(
                label="new size",
                value=self._new_size
            )
        ]
        return "\n".join(lines)
