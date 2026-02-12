from .BaseCommand import Command
from _managers import WidgetManager

class MoveWidgets(Command):
    def __init__(self, widget_ids: frozenset, dx: int, dy: int, widget_manager: WidgetManager):
        self._widget_ids = widget_ids
        self._dx = dx
        self._dy = dy
        self._widget_manager = widget_manager
        self._original_positions = {}   #widget_id -> (x, y)

    def execute(self):
        for widget_id in self._widget_ids:
            #record original position
            model = self._widget_manager.get_model_from_widget_id(widget_id)
            self._original_positions[widget_id] = (model.x, model.y)

            #move the widget
            self._widget_manager.app_state.move_widget_by(model, self._dx, self._dy)

            #request visual update from designer (through callback)
            self._widget_manager.render_soft(model)

    def undo(self):
        for widget_id, (x, y) in self._original_positions.items():
            #move the widget to the original position
            model = self._widget_manager.get_model_from_widget_id(widget_id)
            self._widget_manager.app_state.move_widget_to(model, x, y)

            #request visual update from designer (through callback)
            self._widget_manager.render_soft(model)