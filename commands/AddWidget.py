from model import BaseWidget
from utility import format_mapping

from AppState import AppState
from .BaseCommand import Command


class AddWidget(Command):
    """Encapsulates adding a widget to the project as an undoable command."""
    def __init__(
        self,
        widget: BaseWidget,
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        self._snapshot: dict[str, str | int] = widget.to_dict()     #storing snapshot as commands must not depend on externally mutable state

    def execute(
        self
    ) -> None:
        """Add the widget to the project through AppState."""
        widget = BaseWidget.from_dict(self._snapshot)
        self._app_state.add_widget(widget)

    def undo(
        self
    ) -> None:
        """Remove the previously added widget from the project through AppState."""
        widget_id = self._snapshot["id"]
        widget = self._app_state.get_widget_from_widget_id(widget_id)
        self._app_state.remove_widget(widget)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        widget_data = self._snapshot.copy()     #prevents mutating the snapshot
        widget_id = widget_data.pop("id")
        lines = [
            "[AddWidget]",
            format_mapping(
                label=widget_id,
                mapping=widget_data
            )
        ]
        return "\n".join(lines)
