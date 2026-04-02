from .BaseCommand import Command
from controller import WidgetController

class MoveWidgets(Command):
    def __init__(
        self,
        model_ids: frozenset,
        dx: int,
        dy: int,
        widget_controller: WidgetController
    ):
        """initialize a MoveWidgets command with deltas and affected model IDs"""
        self.widget_controller = widget_controller

        self._model_ids = model_ids
        self._dx = dx
        self._dy = dy
        self._original_positions = {}   #model_id -> (x, y)

    def execute(self):
        """apply movement deltas to all referenced widgets using AppState batching"""
        with self.widget_controller.app_state.batch():  #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                #record original position
                model = self.widget_controller.app_state.get_model_from_model_id(model_id)
                self._original_positions[model_id] = (model.x, model.y)

                #move the widget
                self.widget_controller.app_state.move_widget_by(model, self._dx, self._dy)

    def undo(self):
        """undo the widget movement by restoring original positions using AppState batching"""
        with self.widget_controller.app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                #move the widget to the original position
                model = self.widget_controller.app_state.get_model_from_model_id(model_id)
                self.widget_controller.app_state.move_widget_to(model, x, y)