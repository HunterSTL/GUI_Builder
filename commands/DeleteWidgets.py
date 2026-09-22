from collections.abc import Iterable

from model import BaseWidget
from utility import format_mapping

from AppState import AppState
from .BaseCommand import Command


class DeleteWidgets(Command):
    """Encapsulates widget deletion as an undoable command."""
    def __init__(
        self,
        widgets: Iterable[BaseWidget],
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        widgets = tuple(widgets)                                            #freezes iteration order for deterministic undo and redo behaviour
        self._widget_ids: list[str] = [widget.id for widget in widgets]     #storing IDs and retrieving widgets protects against stale widget references

        self._widget_data_list: list[dict[str, str | int | None]] = [
            widget.to_dict()
            for widget in widgets
        ]

    def execute(
        self
    ) -> None:
        """Remove the widgets from the project."""
        with self._app_state.batch():
            for widget_id in self._widget_ids:
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                self._app_state.remove_widget(widget)

    def undo(
        self
    ) -> None:
        """Restore the previously removed widgets from the stored widget data and add them to the project."""
        with self._app_state.batch():
            for widget_data in self._widget_data_list:
                widget = BaseWidget.from_dict(widget_data)
                self._app_state.add_widget(widget)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[DeleteWidgets]"
        ]

        for widget_data in self._widget_data_list:
            widget_data = widget_data.copy()    #prevents mutating the snapshot
            widget_id = widget_data.pop("id")
            lines.append(
                format_mapping(
                    label=widget_id,
                    mapping=widget_data
                )
            )
        return "\n".join(lines)
