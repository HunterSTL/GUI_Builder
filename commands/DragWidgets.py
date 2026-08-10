from collections.abc import Iterable

from model import BaseWidgetData

from AppState import AppState
from .BaseCommand import Command


class DragWidgets(Command):
    """Encapsulates widget dragging as an undoable command."""
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        models = tuple(models)                                          #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids: list[str] = [model.id for model in models]     #storing IDs and retrieving models protects against stale models

        self._original_positions: dict[str, tuple[int, int]] = {
            model.id: (model.x, model.y)
            for model in models
        }
        self._final_positions: dict[str, tuple[int, int]] = {}

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one widget model position."""
        for model_id in self._model_ids:
            model = self._app_state.get_model_from_model_id(model_id)
            if self._original_positions[model_id] != (model.x, model.y):
                return True
        return False

    def apply_drag_delta(
        self,
        dx: int,
        dy: int
    ) -> None:
        """Apply incremental drag movement to the widget models through AppState."""
        if dx == 0 and dy == 0:         #incremental deltas since last drag event
            return

        with self._app_state.batch():
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.offset_model_position(model, dx, dy)

    def record_final_positions(
        self
    ) -> None:
        """Record final positions."""
        final_positions = {}

        for model_id in self._model_ids:
            model = self._app_state.get_model_from_model_id(model_id)
            final_positions[model_id] = (model.x, model.y)

        self._final_positions = final_positions

    def execute(
        self
    ) -> None:
        """Apply the snapshotted final positions to the widget models through AppState."""
        if not self._final_positions:
            raise ValueError("DragWidgets - execution failed: final positions were not recorded")

        with self._app_state.batch():
            for model_id, (x, y) in self._final_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.set_model_position(model, x, y)

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
        s = "[DragWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s
