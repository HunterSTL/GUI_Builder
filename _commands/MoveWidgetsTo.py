from .BaseCommand import Command
from _managers import WidgetManager

class MoveWidgetsTo(Command):
    def __init__(self, widget_ids: frozenset, widget_manager: WidgetManager):
        self._widget_ids = widget_ids
        self._widget_manager = widget_manager
        self._original_positions = {    #record original positions for selected widgets at drag start
            widget_id: self._widget_manager.get_model_coordinates_from_widget_id(widget_id)
            for widget_id in self._widget_ids
        }
        self._final_positions = {}

    def has_effect(self):
        return any(
            self._original_positions[widget_id] != self._widget_manager.get_model_coordinates_from_widget_id(widget_id)
            for widget_id in self._widget_ids
        )

    def preview_move(self, dx: int, dy: int):
        #dx and dy are incremental deltas since last drag event
        if dx == 0 and dy == 0:
            return

        for widget_id in self._widget_ids:
            self._widget_manager.move(widget_id, dx, dy)

    def freeze_final_positions(self):
        self._final_positions = {       #record final positions for selected widgets at drag end
            widget_id: self._widget_manager.get_model_coordinates_from_widget_id(widget_id)
            for widget_id in self._widget_ids
        }

    def execute(self):
        for widget_id, (x, y) in self._final_positions.items():
            self._widget_manager.move_to(widget_id, x, y)

    def undo(self):
        for widget_id, (x, y) in self._original_positions.items():
            self._widget_manager.move_to(widget_id, x, y)