from commands import CommandStack, MoveWidgets, MoveWidgetsTo, SnapWidgetsToGrid, AlignWidgets
from utility import Direction, Edge, clamped_delta
from AppState import AppState

class WidgetActions:
    """
    Encapsulates the editor's widget semantics: nudge, drag (start, preview, commit), snap to grid and align.

    This class uses AppState for model access and mutation, a CommandStack
    for undo and redo support and an injected callback to handle dirty state updates.
    """
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack,
        set_dirty_callback
    ):
        self.app_state = app_state
        self.command_stack = command_stack
        self.set_dirty_callback = set_dirty_callback

        self._active_drag_command: MoveWidgetsTo | None = None      #MoveWidgetsTo command used for drag preview
        self._active_drag_model_ids: frozenset[str] | None = None   #model IDs used for bounding box lookup during drag preview

    def nudge(self, direction: Direction, amount: int) -> frozenset[str]:
        """nudge selected widgets in the given direction by a fixed amount"""
        #query selection
        selected_models = self.app_state.selection_currently_selected()
        if not selected_models:
            return frozenset()

        #convert to movement delta
        dx, dy = direction.dx * amount, direction.dy * amount

        #compute clamped delta of all selected widgets so they can't be moved outside the canvas
        dx, dy = clamped_delta(
            self.app_state.project.width,
            self.app_state.project.height,
            self.app_state.get_model_bounding_box_from_model_ids(selected_models),
            dx, dy
        )

        #detect no-op
        if dx == 0 and dy == 0:
            return frozenset()

        #move widgets by the delta
        self.command_stack.execute(
            MoveWidgets(
                model_ids=selected_models,
                dx=dx,
                dy=dy,
                app_state=self.app_state
            )
        )

        #mark project as dirty
        self.set_dirty_callback()

        #return the frozenset of model IDs
        return frozenset(selected_models)   #allows the Designer to know whether to refresh the Attributes panel

    def start_drag(self):
        """initialize drag state to snapshot original widget positions"""
        #query selection
        selected_models = self.app_state.selection_currently_selected()
        if not selected_models:
            return

        #store model IDs used for bounding box lookup during drag preview
        self._active_drag_model_ids = frozenset(selected_models)

        #create the MoveWidgetsTo command to record original widget positions
        self._active_drag_command = MoveWidgetsTo(
            model_ids=selected_models,
            app_state=self.app_state
        )

    def preview_drag(self, dx: int, dy: int) -> frozenset[str]:
        """apply a clamped drag preview delta to the selected widgets"""
        if not self._active_drag_command or not self._active_drag_model_ids:
            return frozenset()

        #compute clamped delta of all selected widgets so they can't be moved outside the canvas
        dx, dy = clamped_delta(
            self.app_state.project.width,
            self.app_state.project.height,
            self.app_state.get_model_bounding_box_from_model_ids(self._active_drag_model_ids),
            dx, dy
        )

        #preview the clamped drag movement
        self._active_drag_command.preview_move(dx, dy)

        #return the frozenset of model IDs
        return self._active_drag_model_ids  #allows the Designer to know whether to refresh the Attributes panel

    def commit_drag(self):
        """commit the current drag gesture"""
        cmd = self._active_drag_command
        if not cmd:
            return

        if cmd and cmd.has_effect():
            #record final widget positions
            cmd.freeze_final_positions()

            #execute the actual command
            self.command_stack.execute(cmd)

            #mark project as dirty
            self.set_dirty_callback()

        #reset active_drag_model_ids and active_widget_drag_command
        self._active_drag_model_ids = None
        self._active_drag_command = None

    def snap_to_grid(self) -> frozenset[str]:
        """snap selected widgets to the nearest in bound grid positions"""
        #query selection
        selected_models = self.app_state.selection_currently_selected()
        if not selected_models:
            return frozenset()

        #create the SnapWidgetsToGrid command
        cmd = SnapWidgetsToGrid(
            model_ids=selected_models,
            app_state=self.app_state
        )

        #detect no-op
        if not cmd.has_effect():
            return frozenset()

        #snap widgets to grid
        self.command_stack.execute(cmd)

        #mark project as dirty
        self.set_dirty_callback()

        #return the frozenset of model IDs
        return frozenset(selected_models)   #allows the Designer to know whether to refresh the Attributes panel

    def align(self, edge: Edge):
        """align the given edge of selected widgets to the corresponding edge of the last selected widget"""
        #query selection
        selected_models = self.app_state.selection_currently_selected()
        last_selected_model = self.app_state.selection_last_selected()
        if not selected_models or not last_selected_model:
            return

        #create the AlignWidgets command
        cmd = AlignWidgets(
            model_ids=selected_models,
            last_selected_model_id=last_selected_model,
            edge=edge,
            app_state=self.app_state
        )

        #detect no-op
        if not cmd.has_effect():
            return

        #align widgets
        self.command_stack.execute(cmd)

        #mark project as dirty
        self.set_dirty_callback()