from collections.abc import Iterable

from model import BaseWidgetData

from AppState import AppState
from .BaseCommand import Command


class MoveWidgets(Command):
    """Encapsulates widget nudging as an undoable command."""
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        dx: int,
        dy: int,
        app_state: AppState
    ) -> None:
        self._dx: int = dx
        self._dy: int = dy
        self._app_state: AppState = app_state

        models = tuple(models)                                          #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids: list[str] = [model.id for model in models]     #storing IDs and retrieving models protects against stale models

        self._original_positions: dict[str, tuple[int, int]] = {
            model.id: (model.x, model.y)
            for model in models
        }

    def execute(
        self
    ) -> None:
        """Apply the stored movement deltas to the widget models through AppState."""
        with self._app_state.batch():
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.offset_model_position(model, self._dx, self._dy)

    def undo(
        self
    ) -> None:
        """Restore the snapshotted original positions to the widget models through AppState."""
        with self._app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.set_model_position(model, x, y)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[MoveWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        return s
