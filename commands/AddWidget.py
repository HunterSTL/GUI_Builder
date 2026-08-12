from model import BaseWidget

from AppState import AppState
from .BaseCommand import Command


class AddWidget(Command):
    """Encapsulates adding a widget to the project as an undoable command."""
    def __init__(
        self,
        widget: BaseWidget,
        app_state: AppState
    ) -> None:
        self._widget: BaseWidget = widget
        self._app_state: AppState = app_state

    def execute(
        self
    ) -> None:
        """Add the widget to the project through AppState."""
        self._app_state.add_widget(self._widget)

    def undo(
        self
    ) -> None:
        """Remove the previously added widget from the project through AppState."""
        self._app_state.remove_widget(self._widget)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[AddWidget]"
        s += f"\n\twidget data:\t\t{self._widget.to_dict()}"
        return s
