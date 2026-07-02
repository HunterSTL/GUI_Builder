from collections.abc import Iterable
from model import BaseWidgetData
from commands import Command
from AppState import AppState

class MoveWidgetsTo(Command):
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        app_state: AppState
    ):
        """store affected model IDs and snapshot original widget positions; final positions are snapshotted at the end of a drag gesture"""
        self._app_state = app_state

        #store affected model IDs
        models = tuple(models)                              #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids = [model.id for model in models]    #storing IDs and retrieving models protects against stale models

        #snapshot original positions
        self._original_positions = {
            model.id: (model.x, model.y)
            for model in models
        }
        self._final_positions = {}

    def has_effect(self):
        """return True if widget positions changed since initialization"""
        for model_id in self._model_ids:
            model = self._app_state.get_model_from_model_id(model_id)
            if self._original_positions[model_id] != (model.x, model.y):
                return True
        return False

    def apply_drag_delta(self, dx: int, dy: int):
        """apply incremental drag movement"""
        if dx == 0 and dy == 0:         #incremental deltas since last drag event
            return

        with self._app_state.batch():   #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.offset_model_position(model, dx, dy)

    def record_final_positions(self):
        """record final positions at the end of a drag gesture"""
        final_positions = {}

        for model_id in self._model_ids:
            model = self._app_state.get_model_from_model_id(model_id)
            final_positions[model_id] = (model.x, model.y)

        self._final_positions = final_positions

    def execute(self):
        """apply the snapshotted final widget positions to AppState"""
        if not self._final_positions:
            raise ValueError("MoveWidgetsTo - execution failed: final positions were not recorded")

        with self._app_state.batch():
            for model_id, (x, y) in self._final_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)

                #set the model position to the snapshotted final position
                self._app_state.set_model_position(model, x, y)

    def undo(self):
        """restore original widget positions from the snapshot"""
        with self._app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)

                #set the model position to the original position
                self._app_state.set_model_position(model, x, y)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[MoveWidgetsTo]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s
