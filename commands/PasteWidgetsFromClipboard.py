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
        """snapshot the current clipboard data"""
        self._clipboard = copy.deepcopy(clipboard)
        self._app_state = app_state

        self._executed = False
        self._pasted_ids = []   #populated on first execute(), reused on redo

    def execute(self):
        """create new widget models from the snapshotted clipboard data and add them to AppState"""
        with self._app_state.batch():
            for i, model_data in enumerate(self._clipboard):
                model = BaseWidgetData.from_dict(model_data)

                #only create an ID during the first execution (subsequent redos then reuse the same ID)
                if not self._executed:
                    #create model ID
                    model_id = model.create_id(self._app_state.project.id_counters)
                    self._pasted_ids.append(model_id)
                else:
                    model.id = self._pasted_ids[i]

                #add the model to the ProjectDocument via AppState
                self._app_state.add_model(model)
        self._executed = True

    def undo(self):
        """remove all widget models created from the snapshot"""
        with self._app_state.batch():
            for i, model_data in enumerate(self._clipboard):
                #get the model from AppState using the ID created during execute()
                model = self._app_state.get_model_from_model_id(self._pasted_ids[i])

                #remove the model from the ProjectDocument via AppState
                self._app_state.remove_model(model)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[PasteWidgetsFromClipboard]"
        for model_data in self._clipboard:
            s += f"\n\t{model_data}"
        return s
