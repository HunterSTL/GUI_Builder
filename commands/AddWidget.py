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

        self._widget_data: dict[str, str | int | None] = widget.to_dict()   #storing snapshot as commands must not depend on externally mutable state

    def execute(
        self
    ) -> None:
        """Create a widget from the stored widget data, assign it a new ID and add it to the project."""
        widget = BaseWidget.from_dict(self._widget_data)
        widget.id = self._app_state.project.id_counters.generate_id(widget.type)
        self._app_state.add_widget(widget)
        self._widget_data["id"] = widget.id

    def undo(
        self
    ) -> None:
        """Remove the previously added widget from the project."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_data["id"])
        self._app_state.project.id_counters.decrement_counter(widget.type)
        self._app_state.remove_widget(widget)
        self._widget_data["id"] = None

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        widget_data = self._widget_data.copy()  #prevents mutating the snapshot
        widget_id = widget_data.pop("id")
        lines = [
            "[AddWidget]",
            format_mapping(
                label=widget_id,
                mapping=widget_data
            )
        ]
        return "\n".join(lines)
