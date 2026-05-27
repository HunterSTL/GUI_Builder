from commands import Command
from utility import Edge
from AppState import AppState

class AlignWidgets(Command):
    def __init__(
        self,
        model_ids: frozenset,
        last_selected_model_id: str,
        edge: Edge,
        app_state: AppState
    ):
        """store affected model IDs, snapshot original widget positions and compute and snapshot final widget positions"""
        self._model_ids = list(model_ids)   #freeze iteration order for deterministic undo/redo behaviour
        self._last_selected_model_id = last_selected_model_id
        self._edge = edge
        self._app_state = app_state

        #determine the bbox of the reference model (last selected)
        self._reference_model_bbox = self._app_state.get_model_bounding_box_from_model_id(last_selected_model_id)

        #snapshot original positions
        self._original_positions = {
            model_id: self._app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }

        #compute and snapshot final positions
        self._final_positions = {}
        for model_id in self._model_ids:
            if not model_id == self._last_selected_model_id:
                model_bbox = self._app_state.get_model_bounding_box_from_model_id(model_id)

                #calculate necessary movement delta
                if self._edge == Edge.LEFT:
                    dx, dy = self._reference_model_bbox.left - model_bbox.left, 0
                elif self._edge == Edge.RIGHT:
                    dx, dy = self._reference_model_bbox.right - model_bbox.right, 0
                elif self._edge == Edge.TOP:
                    dx, dy = 0, self._reference_model_bbox.top - model_bbox.top
                elif self._edge == Edge.BOTTOM:
                    dx, dy = 0, self._reference_model_bbox.bottom - model_bbox.bottom
                else:
                    dx, dy = 0, 0
            else:
                dx, dy = 0, 0

            #snapshot final positions
            original_x, original_y = self._original_positions[model_id]
            self._final_positions[model_id] = (original_x + dx, original_y + dy)

    def has_effect(self):
        """return True if executing this command would cause the model to change"""
        return any(
            self._original_positions[model_id] != self._final_positions[model_id]
            for model_id in self._model_ids
        )

    def execute(self):
        """apply the snapshotted widget positions after alignment to AppState"""
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
        s = "[AlignWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\treference model ID:\t{self._last_selected_model_id}"
        s += f"\n\tedge:\t\t\t{self._edge}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s
