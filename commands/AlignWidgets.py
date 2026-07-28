from collections.abc import Iterable
from model import BaseWidgetData
from .BaseCommand import Command
from utility import Edge
from AppState import AppState

class AlignWidgets(Command):
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        reference_model_id: str,
        edge: Edge,
        app_state: AppState
    ):
        """store affected model IDs, snapshot original widget positions and compute and snapshot final widget positions"""
        self._reference_model_id = reference_model_id
        self._edge = edge
        self._app_state = app_state

        #store affected model IDs
        models = tuple(models)                              #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids = [model.id for model in models]    #storing IDs and retrieving models protects against stale models

        #determine the bounding box of the reference model
        reference_model = self._app_state.get_model_from_model_id(reference_model_id)
        self._reference_model_bbox = self._app_state.get_model_bounding_box(reference_model)

        #snapshot original positions
        self._original_positions = {
            model.id: (model.x, model.y)
            for model in models
        }

        #compute and snapshot final positions
        self._final_positions = {}
        for model in models:
            if model.id != self._reference_model_id:
                model_bbox = self._app_state.get_model_bounding_box(model)

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
            original_x, original_y = self._original_positions[model.id]
            self._final_positions[model.id] = (original_x + dx, original_y + dy)

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
        s += f"\n\treference model ID:\t{self._reference_model_id}"
        s += f"\n\tedge:\t\t\t\t{self._edge}"
        s += f"\n\toriginal positions:\t{self._original_positions}"
        s += f"\n\tfinal positions:\t{self._final_positions}"
        return s
