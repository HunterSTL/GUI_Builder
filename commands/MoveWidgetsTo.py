from commands import Command
from AppState import AppState

class MoveWidgetsTo(Command):
    def __init__(
        self,
        model_ids: frozenset,
        app_state: AppState
    ):
        """store affected model IDs and snapshot original widget positions; final positions are snapshotted at the end of a drag gesture"""
        self._model_ids = list(model_ids)   #freeze iteration order for deterministic undo/redo behaviour
        self._app_state = app_state

        #snapshot original positions
        self._original_positions = {
            model_id: self._app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }
        self._final_positions = {}

    def has_effect(self):
        """return True if widget positions changed since initialization"""
        return any(
            self._original_positions[model_id] != self._app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        )

    def preview_move(self, dx: int, dy: int):
        """apply incremental movement during live dragging"""
        #dx and dy are incremental deltas since last drag event
        if dx == 0 and dy == 0:
            return

        with self._app_state.batch():   #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)
                self._app_state.offset_model_position(model, dx, dy)

    def freeze_final_positions(self):
        """record final positions at the end of a drag gesture"""
        self._final_positions = {       #record final positions for selected widgets at drag end
            model_id: self._app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }

    def execute(self):
        """apply the snapshotted final widget positions to AppState"""
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
