from view import CanvasView
from events import EventRouter
from utility import Direction
from AppState import AppState

class CanvasController:
    """
    Routes all canvas input (keyboard, mouse, gestures) into
    Designer actions, selection logic and widget manipulation.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        app_state: AppState,
        canvas_view: CanvasView,
        nudge_small: int,
        nudge_big: int,
        event_router: EventRouter
    ):
        """store references and initial configuration"""
        self.canvas_view = canvas_view
        self.app_state = app_state
        self.nudge_small = nudge_small
        self.nudge_big = nudge_big
        self.event_router = event_router

    #Rendering API------------------------------------------------------------------------------------------------------
    def render_grid(self):
        """render or remove the grid based on grid visibility"""
        grid_config = self.app_state.project.grid
        self.canvas_view.render_grid(grid_config.size, grid_config.color, grid_config.visible)

    #Event handling-----------------------------------------------------------------------------------------------------
    def bind_events(self):
        """bind keyboard, mouse, selection, project, widget, grid, and debug events to the canvas"""
        canvas = self.canvas_view.canvas

        #keeps focus on canvas
        canvas.bind("<Enter>", lambda e: canvas.focus_set(), add="+")
        canvas.bind("<Button-1>", lambda e: canvas.focus_set(), add="+")

        #context menu (right click)
        canvas.bind("<Button-3>", lambda e: self.event_router.emit("menu.show", event=e))

        #selection events
        canvas.bind("<ButtonPress-1>", lambda e: self.event_router.emit("selection.handle_press", event=e))
        canvas.bind("<B1-Motion>", lambda e: self.event_router.emit("selection.handle_drag", event=e))
        canvas.bind("<ButtonRelease-1>", lambda e: self.event_router.emit("selection.handle_release", event=e))

        #project events
        canvas.bind("<Control-n>", lambda e: self.event_router.emit("project.new"))
        canvas.bind("<Control-o>", lambda e: self.event_router.emit("project.open"))
        canvas.bind("<Control-s>", lambda e: self.event_router.emit("project.save"))
        canvas.bind("<Control-Shift-S>", lambda e: self.event_router.emit("project.save_as"))

        #app events
        canvas.bind("<Alt-F4>", lambda e: self.event_router.emit("app.exit"))

        #edit events
        canvas.bind("<Control-x>", lambda e: self.event_router.emit("edit.cut"))
        canvas.bind("<Control-c>", lambda e: self.event_router.emit("edit.copy"))
        canvas.bind("<Control-v>", lambda e: self.event_router.emit("edit.paste"))
        canvas.bind("<Control-z>", lambda e: self.event_router.emit("edit.undo"))
        canvas.bind("<Control-y>", lambda e: self.event_router.emit("edit.redo"))

        #widget events
        canvas.bind("<Left>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.LEFT, amount=self.nudge_small))
        canvas.bind("<Right>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.RIGHT, amount=self.nudge_small))
        canvas.bind("<Up>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.UP, amount=self.nudge_small))
        canvas.bind("<Down>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.DOWN, amount=self.nudge_small))
        canvas.bind("<Shift-Left>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.LEFT, amount=self.nudge_big))
        canvas.bind("<Shift-Right>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.RIGHT, amount=self.nudge_big))
        canvas.bind("<Shift-Up>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.UP, amount=self.nudge_big))
        canvas.bind("<Shift-Down>", lambda e: self.event_router.emit("widget.nudge", direction=Direction.DOWN, amount=self.nudge_big))
        canvas.bind("<Key-s>", lambda e: self.event_router.emit("widget.snap_to_grid"))
        canvas.bind("<Delete>", lambda e: self.event_router.emit("widget.delete"))
        canvas.bind("<Control-Left>", lambda e: self.event_router.emit("widget.align.left"))
        canvas.bind("<Control-Right>", lambda e: self.event_router.emit("widget.align.right"))
        canvas.bind("<Control-Up>", lambda e: self.event_router.emit("widget.align.top"))
        canvas.bind("<Control-Down>", lambda e: self.event_router.emit("widget.align.bottom"))
        canvas.bind("<Control-a>", lambda e: self.event_router.emit("widget.select_all"))

        #grid events
        canvas.bind("<Key-g>", lambda e: self.event_router.emit("grid.toggle"))
        canvas.bind("<Control-g>", lambda e: self.event_router.emit("grid.change_size"))
        canvas.bind("<Shift-G>", lambda e: self.event_router.emit("grid.change_color"))

        #debug events
        canvas.bind("<Control-Shift-T>", lambda e: self.event_router.emit("debug.toggle_call_tracing"))
        canvas.bind("<Control-d>", lambda e: self.event_router.emit("debug.set_dirty"))
        canvas.bind("<Control-Shift-D>",lambda e: self.event_router.emit("debug.set_clean"))
        canvas.bind("<numbersign>", lambda e: self.event_router.emit("debug.print_widget_count"))
        canvas.bind("<F1>", lambda e: self.event_router.emit("debug.print_clipboard"))
        canvas.bind("<F2>", lambda e: self.event_router.emit("debug.print_command_stack"))
        canvas.bind("<F3>", lambda e: self.event_router.emit("debug.print_selection"))
        canvas.bind("<F4>", lambda e: self.event_router.emit("debug.print_bounding_boxes"))
        canvas.bind("<F5>", lambda e: self.event_router.emit("debug.print_id_counters"))
