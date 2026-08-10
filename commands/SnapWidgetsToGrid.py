from collections.abc import Iterable

from model import BaseWidgetData
from utility import allowed_x_range, allowed_y_range, nearest_in_bounds_grid_step

from AppState import AppState
from .BaseCommand import Command


class SnapWidgetsToGrid(Command):
    """Encapsulates widget grid snapping as an undoable command."""
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
        for model in models:
            min_x, max_x = allowed_x_range(self._app_state.project.width, model.width, model.anchor)
            min_y, max_y = allowed_y_range(self._app_state.project.height, model.height, model.anchor)
            new_x = nearest_in_bounds_grid_step(model.x, self._app_state.project.grid.size, min_x, max_x)
            new_y = nearest_in_bounds_grid_step(model.y, self._app_state.project.grid.size, min_y, max_y)
            self._final_positions[model.id] = (new_x, new_y)

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one widget model position."""
        return any(
            self._original_positions[model_id] != self._final_positions[model_id]
            for model_id in self._model_ids
        )

    def execute(
        self
    ) -> None:
        """Apply the snapshotted final positions to the widget models through AppState."""
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
        s = "[SnapWidgetsToGrid]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s
