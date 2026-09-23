from utility import format_field

from AppState import AppState
from .BaseCommand import Command


class SetProjectTitle(Command):
    """Encapsulates setting the project title as an undoable command."""
    def __init__(
        self,
        app_state: AppState,
        new_title: str
    ) -> None:
        self._app_state: AppState = app_state
        self._new_title: str = new_title

        self._previous_title: str = self._app_state.project.title

    def has_effect(
        self
    ) -> bool:
        """Return True if the new title differs from the previous title."""
        return self._new_title != self._previous_title

    def execute(
        self
    ) -> None:
        """Set the project title to the new value."""
        self._app_state.set_project_title(
            title=self._new_title
        )

    def undo(
        self
    ) -> None:
        """Restore the previous title."""
        self._app_state.set_project_title(
            title=self._previous_title
        )

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[SetProjectTitle]",
            format_field(
                label="previous title",
                value=self._previous_title
            ),
            format_field(
                label="new title",
                value=self._new_title
            )
        ]
        return "\n".join(lines)
