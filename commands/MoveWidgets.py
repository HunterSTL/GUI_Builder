from collections.abc import Iterable
from model import BaseWidgetData
from .BaseCommand import Command
from AppState import AppState

class MoveWidgets(Command):
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        dx: int,
        dy: int,
        app_state: AppState
    ):
        """store affected model IDs, store movement deltas and snapshot original widget positions for undo"""
        self._dx = dx
        self._dy = dy
        self._app_state = app_state

        #store affected model IDs
        models = tuple(models)                              #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids = [model.id for model in models]    #storing IDs and retrieving models protects against stale models

        #snapshot original positions
        self._original_positions = {
            model.id: (model.x, model.y)
            for model in models
        }

    def execute(self):
        """apply the stored movement deltas to the widgets"""
        with self._app_state.batch():  #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)

                #offset the model position by a delta
                self._app_state.offset_model_position(model, self._dx, self._dy)

    def undo(self):
        """restore original widget positions from the snapshot"""
        with self._app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)

                #set the model position to the original position
                self._app_state.set_model_position(model, x, y)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[MoveWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        return s
