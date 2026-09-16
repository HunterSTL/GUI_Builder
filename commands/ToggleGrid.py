from utility import format_field

from AppState import AppState
from .BaseCommand import Command


class ToggleGrid(Command):
    """Encapsulates toggling the grid as an undoable command."""
    def __init__(
        self,
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        self._previous_visibility: bool = self._app_state.project.grid.visible
        self._new_visibility: bool = not self._previous_visibility

    def execute(
        self
    ) -> None:
        """Set grid visibility to the new value."""
        self._app_state.set_grid_visible(
            visible=self._new_visibility
        )

    def undo(
        self
    ) -> None:
        """Reset the grid visibility to its previous value."""
        self._app_state.set_grid_visible(
            visible=self._previous_visibility
        )

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[ToggleGrid]",
            format_field(
                label="previous visibility",
                value=self._previous_visibility
            ),
            format_field(
                label="new visibility",
                value=self._new_visibility
            )
        ]
        return "\n".join(lines)
