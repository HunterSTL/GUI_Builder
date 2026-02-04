import tkinter as tk
from ProjectDocument import ProjectDocument

class CanvasManager:
    def __init__(
            self,
            parent: tk.Canvas,
            project_document: ProjectDocument,
            nudge_small: int,
            nudge_big: int,
            callbacks: dict
        ):
        self.parent = parent
        self.project_document = project_document
        self.nudge_small = nudge_small
        self.nudge_big = nudge_big
        self.callbacks = callbacks

        self.grid_lines = []
        self.canvas = tk.Canvas(
            self.parent,
            width=self.project_document.width,
            height=self.project_document.height,
            bg=self.project_document.theme["background"]["color"],
            highlightthickness=0,
            takefocus=1
        )

    def apply_grid_visibility(self):
        if self.project_document.grid.visible:
            self._draw_grid()
        else:
            self._clear_grid()

    def refresh_grid(self):
        if self.project_document.grid.visible:  #redraw grid if it's already shown
            self._clear_grid()
            self._draw_grid()

    def _draw_grid(self):
        for x in range(0, self.project_document.width, self.project_document.grid.size):
            line = self.canvas.create_line(x, 0, x, self.project_document.height, fill=self.project_document.grid.color)
            self.grid_lines.append(line)
        for y in range(0, self.project_document.height, self.project_document.grid.size):
            line = self.canvas.create_line(0, y, self.project_document.width, y, fill=self.project_document.grid.color)
            self.grid_lines.append(line)

    def _clear_grid(self):
        for line in self.grid_lines:
            self.canvas.delete(line)
        self.grid_lines.clear()

    def bind_events(self):
        #set focus on canvas when user clicks anywhere on canvas
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set(), add="+")
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set(), add="+")

        #bind context menu to right click
        self.canvas.bind("<Button-3>", self.callbacks["show_menu"])

        #bind selection events
        selection_callbacks = self.callbacks["selection"]
        self.canvas.bind("<ButtonPress-1>", selection_callbacks["press"])
        self.canvas.bind("<B1-Motion>", selection_callbacks["drag"])
        self.canvas.bind("<ButtonRelease-1>", selection_callbacks["release"])
        self.canvas.bind("<Control-a>", lambda e: selection_callbacks["select_all"]())

        #bind project events
        project_callbacks = self.callbacks["project"]
        self.canvas.bind("<Control-n>", lambda e: project_callbacks["new"]())
        self.canvas.bind("<Control-o>", lambda e: project_callbacks["open"]())
        self.canvas.bind("<Control-s>", lambda e: project_callbacks["save"]())
        self.canvas.bind("<Control-Shift-S>", lambda e: project_callbacks["save_as"]())
        self.canvas.bind("<Control-e>", lambda e: project_callbacks["export_json"]())
        self.canvas.bind("<Alt-F4>", lambda e: project_callbacks["exit_app"]())

        #bind edit events
        edit_callbacks = self.callbacks["edit"]
        self.canvas.bind("<Control-x>", lambda e: edit_callbacks["cut"]())
        self.canvas.bind("<Control-c>", lambda e: edit_callbacks["copy"]())
        self.canvas.bind("<Control-v>", lambda e: edit_callbacks["paste"]())
        self.canvas.bind("<Control-z>", lambda e: edit_callbacks["undo"]())
        self.canvas.bind("<Control-y>", lambda e: edit_callbacks["redo"]())

        #bind widget events
        widget_callbacks = self.callbacks["widget"]
        self.canvas.bind("<Left>", lambda e: widget_callbacks["move"](-self.nudge_small, 0))
        self.canvas.bind("<Right>", lambda e: widget_callbacks["move"](self.nudge_small, 0))
        self.canvas.bind("<Up>", lambda e: widget_callbacks["move"](0, -self.nudge_small))
        self.canvas.bind("<Down>", lambda e: widget_callbacks["move"](0, self.nudge_small))
        self.canvas.bind("<Shift-Left>", lambda e: widget_callbacks["move"](-self.nudge_big, 0))
        self.canvas.bind("<Shift-Right>", lambda e: widget_callbacks["move"](self.nudge_big, 0))
        self.canvas.bind("<Shift-Up>", lambda e: widget_callbacks["move"](0, -self.nudge_big))
        self.canvas.bind("<Shift-Down>", lambda e: widget_callbacks["move"](0, self.nudge_big))
        self.canvas.bind("<Key-s>", lambda e: widget_callbacks["snap_to_grid"]())
        self.canvas.bind("<Delete>", lambda e: widget_callbacks["delete"]())
        self.canvas.bind("<Control-Left>", lambda e: widget_callbacks["align_left"]())
        self.canvas.bind("<Control-Right>", lambda e: widget_callbacks["align_right"]())
        self.canvas.bind("<Control-Up>", lambda e: widget_callbacks["align_top"]())
        self.canvas.bind("<Control-Down>", lambda e: widget_callbacks["align_bottom"]())

        #bind grid events
        grid_callbacks = self.callbacks["grid"]
        self.canvas.bind("<Key-g>", lambda e: grid_callbacks["toggle"]())
        self.canvas.bind("<Control-g>", lambda e: grid_callbacks["change_size"]())
        self.canvas.bind("<Shift-G>", lambda e: grid_callbacks["change_color"]())

        #bind set dirty/clean
        self.canvas.bind("<Control-d>", lambda e: self.callbacks["set_dirty"]())
        self.canvas.bind("<Control-Shift-D>", lambda e: self.callbacks["set_clean"]())