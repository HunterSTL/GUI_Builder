from model import BaseWidgetData

from AppState import AppState
from .BaseCommand import Command


class AddWidget(Command):
    """Encapsulates adding a widget to the project as an undoable command."""
    def __init__(
        self,
        model: BaseWidgetData,
        app_state: AppState
    ) -> None:
        self._model: BaseWidgetData = model
        self._app_state: AppState = app_state

    def execute(
        self
    ) -> None:
        """Add the widget model to the project through AppState."""
        self._app_state.add_model(self._model)

    def undo(
        self
    ) -> None:
        """Remove the previously added widget model from the project through AppState."""
        self._app_state.remove_model(self._model)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[AddWidget]"
        s += f"\n\tmodel data:\t\t{self._model.to_dict()}"
        return s
