from _managers import CanvasView

class CanvasController:
    """wires user interactions from the CanvasView into app intents via callbacks"""
    def __init__(
        self,
        view: CanvasView,
        nudge_small: int,
        nudge_big: int,
        callbacks: dict
    ):
        """initialize the canvas controller and construct the drawing canvas"""
        self.view = view
        self.nudge_small = nudge_small
        self.nudge_big = nudge_big
        self.callbacks = callbacks

    def bind_events(self):
        """bind key, mouse, selection, project, widget, grid, and debug events to the canvas"""
        canvas = self.view.canvas

        #keeps focus on canvas
        canvas.bind("<Enter>", lambda e: canvas.focus_set(), add="+")
        canvas.bind("<Button-1>", lambda e: canvas.focus_set(), add="+")

        #context menu (right click)
        canvas.bind("<Button-3>", self.callbacks["show_menu"])

        #selection events
        selection_callbacks = self.callbacks["selection"]
        canvas.bind("<ButtonPress-1>", selection_callbacks["press"])
        canvas.bind("<B1-Motion>", selection_callbacks["drag"])
        canvas.bind("<ButtonRelease-1>", selection_callbacks["release"])
        canvas.bind("<Control-a>", lambda e: selection_callbacks["select_all"]())

        #project events
        project_callbacks = self.callbacks["project"]
        canvas.bind("<Control-n>", lambda e: project_callbacks["new"]())
        canvas.bind("<Control-o>", lambda e: project_callbacks["open"]())
        canvas.bind("<Control-s>", lambda e: project_callbacks["save"]())
        canvas.bind("<Control-Shift-S>", lambda e: project_callbacks["save_as"]())
        canvas.bind("<Control-e>", lambda e: project_callbacks["export_json"]())
        canvas.bind("<Alt-F4>", lambda e: project_callbacks["exit_app"]())

        #edit events
        edit_callbacks = self.callbacks["edit"]
        canvas.bind("<Control-x>", lambda e: edit_callbacks["cut"]())
        canvas.bind("<Control-c>", lambda e: edit_callbacks["copy"]())
        canvas.bind("<Control-v>", lambda e: edit_callbacks["paste"]())
        canvas.bind("<Control-z>", lambda e: edit_callbacks["undo"]())
        canvas.bind("<Control-y>", lambda e: edit_callbacks["redo"]())

        #widget events
        widget_callbacks = self.callbacks["widget"]
        canvas.bind("<Left>", lambda e: widget_callbacks["move"](-self.nudge_small, 0))
        canvas.bind("<Right>", lambda e: widget_callbacks["move"](self.nudge_small, 0))
        canvas.bind("<Up>", lambda e: widget_callbacks["move"](0, -self.nudge_small))
        canvas.bind("<Down>", lambda e: widget_callbacks["move"](0, self.nudge_small))
        canvas.bind("<Shift-Left>", lambda e: widget_callbacks["move"](-self.nudge_big, 0))
        canvas.bind("<Shift-Right>", lambda e: widget_callbacks["move"](self.nudge_big, 0))
        canvas.bind("<Shift-Up>", lambda e: widget_callbacks["move"](0, -self.nudge_big))
        canvas.bind("<Shift-Down>", lambda e: widget_callbacks["move"](0, self.nudge_big))
        canvas.bind("<Key-s>", lambda e: widget_callbacks["snap_to_grid"]())
        canvas.bind("<Delete>", lambda e: widget_callbacks["delete"]())
        canvas.bind("<Control-Left>", lambda e: widget_callbacks["align_left"]())
        canvas.bind("<Control-Right>", lambda e: widget_callbacks["align_right"]())
        canvas.bind("<Control-Up>", lambda e: widget_callbacks["align_top"]())
        canvas.bind("<Control-Down>", lambda e: widget_callbacks["align_bottom"]())

        #grid events
        grid_callbacks = self.callbacks["grid"]
        canvas.bind("<Key-g>", lambda e: grid_callbacks["toggle"]())
        canvas.bind("<Control-g>", lambda e: grid_callbacks["change_size"]())
        canvas.bind("<Shift-G>", lambda e: grid_callbacks["change_color"]())

        #debug events
        canvas.bind("<Control-Shift-T>", lambda e: self.callbacks["toggle_call_tracing"]())
        canvas.bind("<Control-d>", lambda e: self.callbacks["set_dirty"]())
        canvas.bind("<Control-Shift-D>", lambda e: self.callbacks["set_clean"]())