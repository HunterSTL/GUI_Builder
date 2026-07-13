from collections.abc import Callable
from model import BaseWidgetData, LabelWidgetData, EntryWidgetData, ButtonWidgetData
from commands import CommandStack, MoveWidgets, MoveWidgetsTo, SnapWidgetsToGrid, AlignWidgets, AddWidget
from utility import Direction, Edge, WidgetType, clamped_delta, allowed_x_range, allowed_y_range, clamp
from AppState import AppState

class WidgetActions:
    """
    Encapsulates the editor's widget semantics: nudge, drag (start, apply delta, commit), snap to grid and align.

    This class uses AppState for model access and mutation and a CommandStack for undo and redo support.
    """
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack,
        measure_preview_widget_callback: Callable[[BaseWidgetData], tuple[int, int]]
    ):
        self._app_state = app_state
        self._command_stack = command_stack
        self._measure_preview_widget_callback = measure_preview_widget_callback

        self._active_drag_command: MoveWidgetsTo | None = None              #MoveWidgetsTo command used for live dragging
        self._active_drag_models: tuple[BaseWidgetData, ...] | None = None  #models used for bounding box lookup during live dragging

    def nudge(self, direction: Direction, amount: int):
        """nudge selected widgets in the given direction by a fixed amount"""
        #query selection
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        #convert to movement delta
        dx, dy = direction.dx * amount, direction.dy * amount

        #compute clamped delta of all selected widgets so they can't be moved outside the canvas
        dx, dy = clamped_delta(
            self._app_state.project.width,
            self._app_state.project.height,
            self._app_state.get_model_group_bounding_box(selected_models),
            dx, dy
        )

        #detect no-op
        if dx == 0 and dy == 0:
            return

        #move widgets by the delta
        self._command_stack.execute(
            MoveWidgets(
                models=selected_models,
                dx=dx,
                dy=dy,
                app_state=self._app_state
            )
        )

    def start_drag(self):
        """initialize drag state to snapshot original widget positions"""
        #query selection
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        #store models used for bounding box lookup during live dragging
        self._active_drag_models = selected_models

        #create the MoveWidgetsTo command to record original widget positions
        self._active_drag_command = MoveWidgetsTo(
            models=selected_models,
            app_state=self._app_state
        )

    def apply_drag_delta(self, dx: int, dy: int):
        """apply a clamped drag delta to the selected widgets"""
        if self._active_drag_command is None or self._active_drag_models is None:
            return

        #compute clamped delta of all selected widgets so they can't be moved outside the canvas
        dx, dy = clamped_delta(
            self._app_state.project.width,
            self._app_state.project.height,
            self._app_state.get_model_group_bounding_box(self._active_drag_models),
            dx, dy
        )

        #detect no-op
        if dx == 0 and dy == 0:
            return

        #apply the clamped drag delta to the live model
        self._active_drag_command.apply_drag_delta(dx, dy)

    def commit_drag(self):
        """commit the current drag gesture"""
        cmd = self._active_drag_command
        if not cmd:
            return

        if cmd and cmd.has_effect():
            #record final widget positions
            cmd.record_final_positions()

            #execute the actual command
            self._command_stack.execute(cmd)

        #reset active_drag_models and active_widget_drag_command
        self._active_drag_models = None
        self._active_drag_command = None

    def snap_to_grid(self):
        """snap selected widgets to the nearest in bound grid positions"""
        #query selection
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        #create the SnapWidgetsToGrid command
        cmd = SnapWidgetsToGrid(
            models=selected_models,
            app_state=self._app_state
        )

        #detect no-op
        if not cmd.has_effect():
            return

        #snap widgets to grid
        self._command_stack.execute(cmd)

    def align(self, edge: Edge):
        """align the given edge of selected widgets to the corresponding edge of the last selected widget"""
        #query selection
        selected_models = self._app_state.get_selected_models()
        last_selected_model_id = self._app_state.get_last_selected_model_id()
        if not selected_models or last_selected_model_id is None:
            return

        #create the AlignWidgets command
        cmd = AlignWidgets(
            models=selected_models,
            reference_model_id=last_selected_model_id,
            edge=edge,
            app_state=self._app_state
        )

        #detect no-op
        if not cmd.has_effect():
            return

        #align widgets
        self._command_stack.execute(cmd)

    def add(self, widget_type: WidgetType, coordinates: tuple[int, int] | None, text: str | None):
        """add a new widget to the project"""
        if coordinates is None:
            raise ValueError("WidgetActions - widget creation failed: missing coordinates")

        if widget_type == WidgetType.LABEL:
            if text is None:
                raise ValueError("WidgetActions - widget creation failed: missing required label text")

            model = LabelWidgetData(
                x=coordinates[0],
                y=coordinates[1],
                bg=self._app_state.project.theme["label"]["bg"],
                fg=self._app_state.project.theme["label"]["fg"],
                text=text
            )
        elif widget_type == WidgetType.ENTRY:
            model = EntryWidgetData(
                x=coordinates[0],
                y=coordinates[1],
                bg=self._app_state.project.theme["entry"]["bg"],
                fg=self._app_state.project.theme["entry"]["fg"]
            )
        elif widget_type == WidgetType.BUTTON:
            if text is None:
                raise ValueError("WidgetActions - widget creation failed: missing required button text")

            model = ButtonWidgetData(
                x=coordinates[0],
                y=coordinates[1],
                bg=self._app_state.project.theme["button"]["bg"],
                fg=self._app_state.project.theme["button"]["fg"],
                text=text
            )
        else:
            raise ValueError(f"WidgetActions - widget creation failed: unsupported type \"{widget_type}\"")

        model.create_id(self._app_state.project.id_counters)
        model.width, model.height = self._measure_preview_widget_callback(model)

        #calculate clamped x and y to prevent the widget from being created (partially) outside the canvas
        min_x, max_x = allowed_x_range(self._app_state.project.width, model.width, model.anchor)
        min_y, max_y = allowed_y_range(self._app_state.project.height, model.height, model.anchor)
        model.x = clamp(model.x, min_x, max_x)
        model.y = clamp(model.y, min_y, max_y)

        cmd = AddWidget(
            model=model,
            app_state=self._app_state
        )

        self._command_stack.execute(cmd)
