from commands import Command
from AppState import AppState

class MoveWidgets(Command):
    def __init__(
        self,
        model_ids: frozenset,
        dx: int,
        dy: int,
        app_state: AppState
    ):
        """store affected model IDs, deltas and keep a reference of AppState (model mutator)"""
        self._model_ids = model_ids
        self._dx = dx
        self._dy = dy
        self._app_state = app_state

        self._original_positions = {}   #model_id -> (x, y)

    def execute(self):
        """apply movement deltas to all referenced widgets using AppState batching"""
        with self._app_state.batch():  #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                #record original position
                model = self._app_state.get_model_from_model_id(model_id)
                self._original_positions[model_id] = (model.x, model.y)

                #move the widget
                self._app_state.move_widget_by(model, self._dx, self._dy)

    def undo(self):
        """undo the widget movement by restoring original positions using AppState batching"""
        with self._app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                #move the widget to the original position
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.move_widget_to(model, x, y)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[MoveWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        return s