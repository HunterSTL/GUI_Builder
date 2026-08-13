from collections.abc import Callable

from commands import AddWidget, AlignWidgets, CommandStack, DragWidgets, EditWidget, NudgeWidgets, SnapWidgetsToGrid
from model import BaseWidget, ButtonWidget, EntryWidget, LabelWidget
from utility import Direction, Edge, WidgetType, allowed_x_range, allowed_y_range, clamp, clamped_delta

from AppState import AppState


class WidgetActions:
    """Encapsulates widget movement, creation and attribute editing."""
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack,
        measure_preview_tk_widget_callback: Callable[[WidgetType, str], tuple[int, int]]
    ) -> None:
        self._app_state: AppState = app_state
        self._command_stack: CommandStack = command_stack
        self._measure_preview_tk_widget_callback: Callable[[WidgetType, str], tuple[int, int]] = measure_preview_tk_widget_callback

        self._active_drag_command: DragWidgets | None = None
        self._active_drag_widgets: tuple[BaseWidget, ...] | None = None     #live reference to widgets used for bounding box lookup during live dragging

        self._active_edit_command: EditWidget | None = None
        self._active_edit_widget: BaseWidget | None = None                  #live reference to the widget used for dimension recomputation on text changes


    def nudge(
        self,
        direction: Direction,
        amount: int
    ) -> None:
        """Nudge selected widgets by a fixed amount in the given direction."""
        selected_widgets = self._app_state.get_selected_widgets()
        if not selected_widgets:
            return

        dx, dy = clamped_delta(     #keeps widgets within canvas bounds
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_widget_group_bounding_box(selected_widgets),
            dx=direction.dx * amount,
            dy=direction.dy * amount
        )

        if dx == 0 and dy == 0:
            return

        self._command_stack.execute(
            NudgeWidgets(
                widgets=selected_widgets,
                dx=dx,
                dy=dy,
                app_state=self._app_state
            )
        )

    def start_drag(
        self
    ) -> None:
        """Start a drag gesture with the current selection."""
        selected_widgets = self._app_state.get_selected_widgets()
        if not selected_widgets:
            return

        self._active_drag_widgets = selected_widgets    #used for bounding box lookup during live dragging
        self._active_drag_command = DragWidgets(
            widgets=selected_widgets,
            app_state=self._app_state
        )

    def update_drag(
        self,
        dx: int,
        dy: int
    ) -> None:
        """Apply a drag delta to the active drag gesture."""
        if self._active_drag_command is None or self._active_drag_widgets is None:
            return

        dx, dy = clamped_delta(     #keeps widgets within canvas bounds
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_widget_group_bounding_box(self._active_drag_widgets),
            dx=dx,
            dy=dy
        )

        if dx == 0 and dy == 0:
            return

        self._active_drag_command.apply_drag_delta(dx, dy)

    def end_drag(
        self
    ) -> None:
        """End the active drag gesture and execute it if it had an effect."""
        cmd = self._active_drag_command
        if not cmd:
            return

        try:
            cmd.record_final_positions()

            if cmd.has_effect():
                self._command_stack.execute(cmd)
        finally:
            self._active_drag_widgets = None
            self._active_drag_command = None

    def snap_to_grid(
        self
    ) -> None:
        """Snap selected widgets to their nearest valid grid positions."""
        selected_widgets = self._app_state.get_selected_widgets()
        if not selected_widgets:
            return

        cmd = SnapWidgetsToGrid(
            widgets=selected_widgets,
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
        selected_widgets = self._app_state.get_selected_widgets()
        last_selected_widget_id = self._app_state.get_last_selected_widget_id()
        if not selected_widgets or last_selected_widget_id is None:
            return

        cmd = AlignWidgets(
            widgets=selected_widgets,
            reference_widget_id=last_selected_widget_id,
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
        width, height = self._measure_preview_tk_widget_callback(widget_type, measurement_text)

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

        widget_id = self._app_state.project.id_counters.generate_id(widget_type)

        if widget_type == WidgetType.LABEL:
            widget = LabelWidget(
                id=widget_id,
                x=x,
                y=y,
                bg=self._app_state.project.theme["label"]["bg"],
                fg=self._app_state.project.theme["label"]["fg"],
                width=width,
                height=height,
                text=text
            )
        elif widget_type == WidgetType.ENTRY:
            widget = EntryWidget(
                id=widget_id,
                x=x,
                y=y,
                bg=self._app_state.project.theme["entry"]["bg"],
                fg=self._app_state.project.theme["entry"]["fg"],
                width=width,
                height=height
            )
        else:   #WidgetType.BUTTON; other types were rejected above
            widget = ButtonWidget(
                id=widget_id,
                x=x,
                y=y,
                bg=self._app_state.project.theme["button"]["bg"],
                fg=self._app_state.project.theme["button"]["fg"],
                width=width,
                height=height,
                text=text
            )

        cmd = AddWidget(
            widget=widget,
            app_state=self._app_state
        )

        self._command_stack.execute(cmd)

    def start_edit(
        self
    ) -> None:
        """Start an attribute edit gesture for a single selected widget."""
        if self._active_edit_command is not None:
            return

        selected_widgets = self._app_state.get_selected_widgets()
        if len(selected_widgets) != 1:
            return

        self._active_edit_widget = selected_widgets[0]  #used for dimension recomputation on text changes
        self._active_edit_command = EditWidget(
            widget=selected_widgets[0],
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
        if self._active_edit_command is None or self._active_edit_widget is None:
            return

        if attribute == "text":     #text updates require measurement to update widget dimensions
            width, height = self._measure_preview_tk_widget_callback(self._active_edit_widget.type, value)

            min_x, max_x = allowed_x_range(
                canvas_width=self._app_state.project.width,
                widget_width=width,
                anchor=self._active_edit_widget.anchor
            )
            min_y, max_y = allowed_y_range(
                canvas_height=self._app_state.project.height,
                widget_height=height,
                anchor=self._active_edit_widget.anchor
            )
            x = clamp(self._active_edit_widget.x, min_x, max_x)
            y = clamp(self._active_edit_widget.y, min_y, max_y)

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
                anchor=self._active_edit_widget.anchor
            )
            x = clamp(self._active_edit_widget.x, min_x, max_x)

            attribute_changes = {
                "width": value,
                "x": x
            }
        elif attribute == "height": #height updates require recomputation of allowed y range
            min_y, max_y = allowed_y_range(
                canvas_height=self._app_state.project.height,
                widget_height=value,
                anchor=self._active_edit_widget.anchor
            )
            y = clamp(self._active_edit_widget.y, min_y, max_y)

            attribute_changes = {
                "height": value,
                "y": y
            }
        elif attribute == "anchor": #anchor updates require recomputation of allowed x and y range
            min_x, max_x = allowed_x_range(
                canvas_width=self._app_state.project.width,
                widget_width=self._active_edit_widget.width,
                anchor=value
            )
            min_y, max_y = allowed_y_range(
                canvas_height=self._app_state.project.height,
                widget_height=self._active_edit_widget.height,
                anchor=value
            )
            x = clamp(self._active_edit_widget.x, min_x, max_x)
            y = clamp(self._active_edit_widget.y, min_y, max_y)

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
            self._active_edit_widget = None
            self._active_edit_command = None
