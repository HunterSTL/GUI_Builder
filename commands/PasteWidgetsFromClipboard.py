import copy
from model import BaseWidgetData
from commands import Command
from AppState import AppState

class PasteWidgetsFromClipboard(Command):
    def __init__(
        self,
        clipboard: list[dict],
        app_state: AppState
    ):
        """store the current clipboard and keep a reference of AppState (model mutator)"""
        self._clipboard = copy.deepcopy(clipboard)
        self._app_state = app_state

    def execute(self):
        """create new widget models from serialized clipboard model_data and add them to the ProjectDocument via AppState"""
        with self._app_state.batch():
            for model_data in self._clipboard:
                model = BaseWidgetData.from_dict(model_data)

                #only create an ID during the first execution (subsequent redos then reuse the same ID)
                if "id" not in model_data:
                    #create model ID
                    model_id = model.create_id(self._app_state.project.id_counters)

                    #add ID to model_data
                    model_data["id"] = model_id

                #add the model to the ProjectDocument via AppState
                self._app_state.add_widget(model)

    def undo(self):
        """remove all widget models created during execute() from the ProjectDocument via AppState"""
        with self._app_state.batch():
            for model_data in self._clipboard:
                #get model from AppState using the ID created during execute()
                model = self._app_state.get_model_from_model_id(model_data.get("id"))

                #remove the model from the ProjectDocument via AppState
                self._app_state.remove_widget(model)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[PasteWidgetsFromClipboard]"
        for model_data in self._clipboard:
            s += f"\n\t{model_data}"
        return s