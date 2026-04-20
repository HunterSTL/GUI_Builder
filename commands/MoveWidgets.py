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
        """store affected model IDs, store movement deltas and snapshot original widget positions for undo"""
        self._model_ids = list(model_ids)   #freeze iteration order for deterministic undo/redo behaviour
        self._dx = dx
        self._dy = dy
        self._app_state = app_state

        #snapshot original positions
        self._original_positions = {
            model_id: self._app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }

    def execute(self):
        """apply the stored movement deltas to the widgets"""
        with self._app_state.batch():  #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)

                #move the widget
                self._app_state.move_widget_by(model, self._dx, self._dy)

    def undo(self):
        """restore original widget positions from the snapshot"""
        with self._app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)

                #move the widget to the original position
                self._app_state.move_widget_to(model, x, y)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[MoveWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        return s