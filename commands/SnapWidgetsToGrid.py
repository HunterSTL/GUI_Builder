from commands import Command
from utility import allowed_x_range, allowed_y_range, nearest_in_bounds_grid_step
from AppState import AppState

class SnapWidgetsToGrid(Command):
    def __init__(
        self,
        model_ids: frozenset,
        app_state: AppState
    ):
        """store affected model IDs, snapshot original widget positions and compute and snapshot final widget positions"""
        self._model_ids = list(model_ids)   #freeze iteration order for deterministic undo/redo behaviour
        self._app_state = app_state

        #snapshot original positions
        self._original_positions = {
            model_id: self._app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }

        #compute and snapshot final positions
        self._final_positions = {}
        for model_id in self._model_ids:
            model = self._app_state.get_model_from_model_id(model_id)

            #compute allowed x and y range for the model
            min_x, max_x = allowed_x_range(self._app_state.project.width, model.width, model.anchor)
            min_y, max_y = allowed_y_range(self._app_state.project.height, model.height, model.anchor)

            #find nearest grid step that is still inside the allowed range
            new_x = nearest_in_bounds_grid_step(model.x, self._app_state.project.grid.size, min_x, max_x)
            new_y = nearest_in_bounds_grid_step(model.y, self._app_state.project.grid.size, min_y, max_y)

            #snapshot final positions
            self._final_positions[model_id] = (new_x, new_y)

    def has_effect(self):
        """return True if executing this command would cause the model to change"""
        return any(
            self._original_positions[model_id] != self._final_positions[model_id]
            for model_id in self._model_ids
        )

    def execute(self):
        """apply the snapshotted widget positions after grid alignment to AppState"""
        with self._app_state.batch():
            for model_id, (x, y) in self._final_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)

                #move the widget to the final position
                self._app_state.move_widget_to(model, x, y)

    def undo(self):
        """restore original widget positions from the snapshot"""
        with self._app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                model = self._app_state.get_model_from_model_id(model_id)

                #move the widget to the original position
                self._app_state.move_widget_to(model, x, y)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[SnapWidgetsToGrid]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s