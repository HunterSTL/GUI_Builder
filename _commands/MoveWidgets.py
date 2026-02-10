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
            self._original_positions[widget_id] = self._widget_manager.get_model_coordinates_from_widget_id(widget_id)

            #move the canvas item
            self._widget_manager.move(widget_id, self._dx, self._dy)

    def undo(self):
        for widget_id, (x, y) in self._original_positions.items():
            #move the canvas item to the original position
            self._widget_manager.move_to(widget_id, x, y)