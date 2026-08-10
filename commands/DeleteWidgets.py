from collections.abc import Iterable

from model import BaseWidgetData

from AppState import AppState
from .BaseCommand import Command


class DeleteWidgets(Command):
    """Encapsulates widget deletion as an undoable command."""
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        models = tuple(models)                                          #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids: list[str] = [model.id for model in models]     #storing IDs and retrieving models protects against stale models

        self._snapshot: list[dict[str, str | int]] = [
            model.to_dict()
            for model in models
        ]

    def execute(
        self
    ) -> None:
        """Remove the widget models from the project through AppState."""
        with self._app_state.batch():
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.remove_model(model)

    def undo(
        self
    ) -> None:
        """Restore the previously removed, snapshotted widget models to the project through AppState."""
        with self._app_state.batch():
            for model_data in self._snapshot:
                model = BaseWidgetData.from_dict(model_data)
                self._app_state.add_model(model)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[DeleteWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tmodel data:"
        for model_data in self._snapshot:
            s += f"\n\t\t{model_data}"
        return s
