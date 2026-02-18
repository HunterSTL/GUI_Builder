from .BaseCommand import Command
from _managers import WidgetManager

class MoveWidgets(Command):
    def __init__(
        self,
        model_ids: frozenset,
        dx: int,
        dy: int,
        widget_manager: WidgetManager
    ):
        """initialize a MoveWidgets command with deltas and affected model IDs"""
        self._model_ids = model_ids
        self._dx = dx
        self._dy = dy
        self._widget_manager = widget_manager
        self._original_positions = {}   #model_id -> (x, y)

    def execute(self):
        """apply movement deltas to all referenced widgets using AppState batching"""
        with self._widget_manager.app_state.batch():    #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                #record original position
                model = self._widget_manager.get_model_from_model_id(model_id)
                self._original_positions[model_id] = (model.x, model.y)

                #move the widget
                self._widget_manager.app_state.move_widget_by(model, self._dx, self._dy)

    def undo(self):
        """undo the widget movement by restoring original positions using AppState batching"""
        with self._widget_manager.app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                #move the widget to the original position
                model = self._widget_manager.get_model_from_model_id(model_id)
                self._widget_manager.app_state.move_widget_to(model, x, y)