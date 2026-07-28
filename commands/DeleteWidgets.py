from collections.abc import Iterable
from model import BaseWidgetData
from .BaseCommand import Command
from AppState import AppState

class DeleteWidgets(Command):
    def __init__(
        self,
        models: Iterable[BaseWidgetData],
        app_state: AppState
    ):
        """store affected model IDs and snapshot model data required to restore deleted widgets during undo"""
        self._app_state = app_state

        #store affected model IDs
        models = tuple(models)                              #freezes iteration order for deterministic undo and redo behaviour
        self._model_ids = [model.id for model in models]    #storing IDs and retrieving models protects against stale models

        #store model data
        self._snapshot = [
            model.to_dict(include_id=True)
            for model in models
        ]

    def execute(self):
        """remove widgets from AppState"""
        with self._app_state.batch():
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)

                #delete the model from the ProjectDocument via AppState
                self._app_state.remove_model(model)

    def undo(self):
        """restore previously deleted widgets from the snapshotted model data"""
        with self._app_state.batch():
            for model_data in self._snapshot:
                model = BaseWidgetData.from_dict(model_data)

                #add the model to the ProjectDocument via AppState
                self._app_state.add_model(model)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[DeleteWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tmodel data:"
        for model_data in self._snapshot:
            s += f"\n\t\t{model_data}"
        return s
