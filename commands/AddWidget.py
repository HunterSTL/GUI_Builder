from model import BaseWidgetData
from commands import Command
from AppState import AppState

class AddWidget(Command):
    def __init__(
        self,
        model: BaseWidgetData,
        app_state: AppState
    ):
        self._model = model
        self._app_state = app_state

    def execute(self):
        """add model to AppState"""
        self._app_state.add_model(self._model)

    def undo(self):
        """remove the previously added model from AppState"""
        self._app_state.remove_model(self._model)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[AddWidget]"
        s += f"\n\tmodel data:\t\t{self._model.to_dict(include_id=True)}"
        return s
