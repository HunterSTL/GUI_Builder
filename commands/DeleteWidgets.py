from model import BaseWidgetData
from commands import Command
from AppState import AppState

class DeleteWidgets(Command):
    def __init__(
        self,
        model_ids: frozenset,
        app_state: AppState
    ):
        """store affected model IDs and keep a reference of AppState (model mutator)"""
        self._model_ids = list(model_ids)   #freeze iteration order for deterministic undo/redo behaviour
        self._app_state = app_state

        #store model data
        self._snapshot = [
            self._app_state.get_model_from_model_id(model_id).to_dict(include_id=True)
            for model_id in self._model_ids
        ]

    def execute(self):
        """remove widgets from AppState"""
        with self._app_state.batch():
            for model_id in self._model_ids:
                model = self._app_state.get_model_from_model_id(model_id)

                #delete the model from the ProjectDocument via AppState
                self._app_state.remove_widget(model)

    def undo(self):
        """add models back to AppState from the stored snapshot (model data)"""
        with self._app_state.batch():
            for model_data in self._snapshot:
                model = BaseWidgetData.from_dict(model_data)

                #add the model to the ProjectDocument via AppState
                self._app_state.add_widget(model)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[DeleteWidgets]"
        s += f"\n\tmodel IDs:\t\t\t{self._model_ids}"
        s += f"\n\tmodel data:"
        for model_data in self._snapshot:
            s += f"\n\t\t{model_data}"
        return s