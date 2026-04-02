from .BaseCommand import Command
from controller import WidgetController

class MoveWidgetsTo(Command):
    def __init__(
        self,
        model_ids: frozenset,
        widget_controller: WidgetController
    ):
        """initialize MoveWidgetsTo and record original widget positions"""
        self.widget_controller = widget_controller

        self._model_ids = model_ids
        self._original_positions = {    #record original positions for selected widgets at drag start
            model_id: self.widget_controller.app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }
        self._final_positions = {}

    def has_effect(self):
        """return True if widget positions changed since initialization"""
        return any(
            self._original_positions[model_id] != self.widget_controller.app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        )

    def preview_move(self, dx: int, dy: int):
        """apply incremental movement during live dragging"""
        #dx and dy are incremental deltas since last drag event
        if dx == 0 and dy == 0:
            return

        with self.widget_controller.app_state.batch():    #batching so only one notify happens even if multiple widgets are moved
            for model_id in self._model_ids:
                model = self.widget_controller.app_state.get_model_from_model_id(model_id)
                self.widget_controller.app_state.move_widget_by(model, dx, dy)

    def freeze_final_positions(self):
        """record final positions at the end of a drag gesture"""
        self._final_positions = {       #record final positions for selected widgets at drag end
            model_id: self.widget_controller.app_state.get_model_coordinates_from_model_id(model_id)
            for model_id in self._model_ids
        }

    def execute(self):
        """apply the final stored positions to the widgets using AppState batching"""
        with self.widget_controller.app_state.batch():
            for model_id, (x, y) in self._final_positions.items():
                #move the widget to the final position
                model = self.widget_controller.app_state.get_model_from_model_id(model_id)
                self.widget_controller.app_state.move_widget_to(model, x, y)

    def undo(self):
        """restore original positions saved at drag start using AppState batching"""
        with self.widget_controller.app_state.batch():
            for model_id, (x, y) in self._original_positions.items():
                #move the widget to the original position
                model = self.widget_controller.app_state.get_model_from_model_id(model_id)
                self.widget_controller.app_state.move_widget_to(model, x, y)