from collections.abc import Callable

from commands import AddWidget, AlignWidgets, CommandStack, DragWidgets, EditWidget, NudgeWidgets, SnapWidgetsToGrid
from model import BaseWidgetData, ButtonWidgetData, EntryWidgetData, LabelWidgetData
from utility import Direction, Edge, WidgetType, allowed_x_range, allowed_y_range, clamp, clamped_delta

from AppState import AppState


class WidgetActions:
    """Encapsulates widget movement, creation and attribute editing."""
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack,
        measure_preview_widget_callback: Callable[[WidgetType, str], tuple[int, int]]
    ) -> None:
        self._app_state: AppState = app_state
        self._command_stack: CommandStack = command_stack
        self._measure_preview_widget_callback: Callable[[WidgetType, str], tuple[int, int]] = measure_preview_widget_callback

        self._active_drag_command: DragWidgets | None = None
        self._active_drag_models: tuple[BaseWidgetData, ...] | None = None  #live reference to models used for bounding box lookup during live dragging

        self._active_edit_command: EditWidget | None = None
        self._active_edit_model: BaseWidgetData | None = None               #live reference to the model used for dimension recomputation on text changes


    def nudge(
        self,
        direction: Direction,
        amount: int
    ) -> None:
        """Nudge selected widgets by a fixed amount in the given direction."""
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        dx, dy = clamped_delta(     #keeps widgets within canvas bounds
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_model_group_bounding_box(selected_models),
            dx=direction.dx * amount,
            dy=direction.dy * amount
        )

        if dx == 0 and dy == 0:
            return

        self._command_stack.execute(
            NudgeWidgets(
                models=selected_models,
                dx=dx,
                dy=dy,
                app_state=self._app_state
            )
        )

    def start_drag(
        self
    ) -> None:
        """Start a drag gesture with the current selection."""
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        self._active_drag_models = selected_models  #used for bounding box lookup during live dragging
        self._active_drag_command = DragWidgets(
            models=selected_models,
            app_state=self._app_state
        )

    def apply_drag_delta(
        self,
        dx: int,
        dy: int
    ) -> None:
        """Apply a drag delta to the active drag gesture."""
        if self._active_drag_command is None or self._active_drag_models is None:
            return

        dx, dy = clamped_delta(     #keeps widgets within canvas bounds
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_model_group_bounding_box(self._active_drag_models),
            dx=dx,
            dy=dy
        )

        if dx == 0 and dy == 0:
            return

        self._active_drag_command.apply_drag_delta(dx, dy)

    def commit_drag(
        self
    ) -> None:
        """Commit the active drag gesture if it had an effect."""
        cmd = self._active_drag_command
        if not cmd:
            return

        try:
            cmd.record_final_positions()

            if cmd.has_effect():
                self._command_stack.execute(cmd)
        finally:
            self._active_drag_models = None
            self._active_drag_command = None

    def snap_to_grid(
        self
    ) -> None:
        """Snap selected widgets to their nearest valid grid positions."""
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        cmd = SnapWidgetsToGrid(
            models=selected_models,
            app_state=self._app_state
        )

        if not cmd.has_effect():
            return

        self._command_stack.execute(cmd)

    def align(
        self,
        edge: Edge
    ) -> None:
        """Align the given edge of selected widgets to the same edge of the last selected widget."""
        selected_models = self._app_state.get_selected_models()
        last_selected_model_id = self._app_state.get_last_selected_model_id()
        if not selected_models or last_selected_model_id is None:
            return

        cmd = AlignWidgets(
            models=selected_models,
            reference_model_id=last_selected_model_id,
            edge=edge,
            app_state=self._app_state
        )

        if not cmd.has_effect():
            return

        self._command_stack.execute(cmd)

    def add(
        self,
        widget_type: WidgetType,
        coordinates: tuple[int, int] | None,
        text: str | None
    ) -> None:
        """Add a widget to the project using the given type, coordinates and text."""
        if widget_type not in (WidgetType.LABEL, WidgetType.ENTRY, WidgetType.BUTTON):
            raise ValueError(f"WidgetActions - widget creation failed: unsupported type \"{widget_type}\"")

        if coordinates is None:
            raise ValueError("WidgetActions - widget creation failed: missing coordinates")

        if widget_type in (WidgetType.LABEL, WidgetType.BUTTON) and text is None:
            raise ValueError("WidgetActions - widget creation failed: missing text")

        measurement_text = text if text is not None else ""
        width, height = self._measure_preview_widget_callback(widget_type, measurement_text)

        min_x, max_x = allowed_x_range(
            canvas_width=self._app_state.project.width,
            widget_width=width,
            anchor="sw"
        )
        min_y, max_y = allowed_y_range(
            canvas_height=self._app_state.project.height,
            widget_height=height,
            anchor="sw"
        )
        x = clamp(coordinates[0], min_x, max_x)
        y = clamp(coordinates[1], min_y, max_y)

        model_id = self._app_state.project.id_counters.generate_id(widget_type)

        if widget_type == WidgetType.LABEL:
            model = LabelWidgetData(
                id=model_id,
                x=x,
                y=y,
                bg=self._app_state.project.theme["label"]["bg"],
                fg=self._app_state.project.theme["label"]["fg"],
                width=width,
                height=height,
                text=text
            )
        elif widget_type == WidgetType.ENTRY:
            model = EntryWidgetData(
                id=model_id,
                x=x,
                y=y,
                bg=self._app_state.project.theme["entry"]["bg"],
                fg=self._app_state.project.theme["entry"]["fg"],
                width=width,
                height=height
            )
        else:   #WidgetType.BUTTON; other types were rejected above
            model = ButtonWidgetData(
                id=model_id,
                x=x,
                y=y,
                bg=self._app_state.project.theme["button"]["bg"],
                fg=self._app_state.project.theme["button"]["fg"],
                width=width,
                height=height,
                text=text
            )

        cmd = AddWidget(
            model=model,
            app_state=self._app_state
        )

        self._command_stack.execute(cmd)

    def start_edit(
        self
    ) -> None:
        """Start an attribute edit gesture for a single selected widget."""
        if self._active_edit_command is not None:
            return

        selected_models = self._app_state.get_selected_models()
        if len(selected_models) != 1:
            return

        self._active_edit_model = selected_models[0]    #used for dimension recomputation on text changes
        self._active_edit_command = EditWidget(
            model=selected_models[0],
            app_state=self._app_state
        )

    def apply_attribute_change(
        self,
        attribute: str,
        value: str | int
    ) -> None:
        """
        Apply an attribute change to the active edit gesture while keeping the widget valid.

        Text changes may update widget dimensions.
        Dimension and anchor changes may update widget position.
        """
        if self._active_edit_command is None or self._active_edit_model is None:
            return

        if attribute == "text":     #text updates require measurement to update model dimensions
            width, height = self._measure_preview_widget_callback(self._active_edit_model.type, value)

            min_x, max_x = allowed_x_range(
                canvas_width=self._app_state.project.width,
                widget_width=width,
                anchor=self._active_edit_model.anchor
            )
            min_y, max_y = allowed_y_range(
                canvas_height=self._app_state.project.height,
                widget_height=height,
                anchor=self._active_edit_model.anchor
            )
            x = clamp(self._active_edit_model.x, min_x, max_x)
            y = clamp(self._active_edit_model.y, min_y, max_y)

            attribute_changes = {
                "text": value,
                "width": width,
                "height": height,
                "x": x,
                "y": y
            }
        elif attribute == "width":  #width updates require recomputation of allowed x range
            min_x, max_x = allowed_x_range(
                canvas_width=self._app_state.project.width,
                widget_width=value,
                anchor=self._active_edit_model.anchor
            )
            x = clamp(self._active_edit_model.x, min_x, max_x)

            attribute_changes = {
                "width": value,
                "x": x
            }
        elif attribute == "height": #height updates require recomputation of allowed y range
            min_y, max_y = allowed_y_range(
                canvas_height=self._app_state.project.height,
                widget_height=value,
                anchor=self._active_edit_model.anchor
            )
            y = clamp(self._active_edit_model.y, min_y, max_y)

            attribute_changes = {
                "height": value,
                "y": y
            }
        elif attribute == "anchor": #anchor updates require recomputation of allowed x and y range
            min_x, max_x = allowed_x_range(
                canvas_width=self._app_state.project.width,
                widget_width=self._active_edit_model.width,
                anchor=value
            )
            min_y, max_y = allowed_y_range(
                canvas_height=self._app_state.project.height,
                widget_height=self._active_edit_model.height,
                anchor=value
            )
            x = clamp(self._active_edit_model.x, min_x, max_x)
            y = clamp(self._active_edit_model.y, min_y, max_y)

            attribute_changes = {
                "anchor": value,
                "x": x,
                "y": y
            }
        else:
            attribute_changes = {
                attribute: value
            }

        self._active_edit_command.apply_attribute_changes(attribute_changes)

    def commit_edit(
        self
    ) -> None:
        """Commit the active attribute edit gesture if it had an effect."""
        cmd = self._active_edit_command
        if not cmd:
            return

        try:
            cmd.record_final_snapshot()

            if cmd.has_effect():
                self._command_stack.execute(cmd)
        finally:
            self._active_edit_model = None
            self._active_edit_command = None
