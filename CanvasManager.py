import tkinter as tk

class CanvasManager:
    def __init__(self, parent: tk.Frame, width: int, height: int, bg_color: str, grid_size: int, grid_color: str, nudge_small: int, nudge_big: int):
        self.parent  = parent
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.grid_size = grid_size
        self.grid_color = grid_color
        self.nudge_small = nudge_small
        self.nudge_big = nudge_big
        self.canvas = None
        self.grid_lines = []
        self.show_grid = False

    def create_canvas(self):
        self.canvas = tk.Canvas(self.parent, width=self.width, height=self.height, bg=self.bg_color, highlightthickness=0)
        return self.canvas

    def pack_canvas(self):
        self.canvas.pack(side="left")

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        if self.show_grid:
            self.draw_grid()
        else:
            self.clear_grid()

    def draw_grid(self):
        for x in range(0, self.width, self.grid_size):
            line = self.canvas.create_line(x, 0, x, self.height, fill=self.grid_color)
            self.grid_lines.append(line)
        for y in range(0, self.height, self.grid_size):
            line = self.canvas.create_line(0, y, self.width, y, fill=self.grid_color)
            self.grid_lines.append(line)

    def clear_grid(self):
        for line in self.grid_lines:
            self.canvas.delete(line)
        self.grid_lines.clear()

    def bind_events(self, callbacks):
        #set focus on canvas when user clicks anywhere on canvas
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set())
        #bind context menu to right click
        self.canvas.bind("<Button-3>", callbacks["show_menu"])

        #bind rectangle selection events
        selection_callbacks = callbacks["selection"]
        self.canvas.bind("<ButtonPress-1>", selection_callbacks["press"])
        self.canvas.bind("<B1-Motion>", selection_callbacks["drag"])
        self.canvas.bind("<ButtonRelease-1>", selection_callbacks["release"])

        #delete selected widgets
        self.canvas.bind("<Delete>", lambda e: callbacks["delete"])

        #binds events to move selected widgets
        self.canvas.bind("<Left>", lambda e: callbacks["move"](-self.nudge_small, 0))
        self.canvas.bind("<Right>", lambda e: callbacks["move"](self.nudge_small, 0))
        self.canvas.bind("<Up>", lambda e: callbacks["move"](0, -self.nudge_small))
        self.canvas.bind("<Down>", lambda e: callbacks["move"](0, self.nudge_small))
        self.canvas.bind("<Shift-Left>", lambda e: callbacks["move"](-self.nudge_big, 0))
        self.canvas.bind("<Shift-Right>", lambda e: callbacks["move"](self.nudge_big, 0))
        self.canvas.bind("<Shift-Up>", lambda e: callbacks["move"](0, -self.nudge_big))
        self.canvas.bind("<Shift-Down>", lambda e: callbacks["move"](0, self.nudge_big))

        #align selected widgets
        self.canvas.bind("<Control-Left>", lambda e: callbacks["align"]("left"))
        self.canvas.bind("<Control-Right>", lambda e: callbacks["align"]("right"))
        self.canvas.bind("<Control-Up>", lambda e: callbacks["align"]("top"))
        self.canvas.bind("<Control-Down>", lambda e: callbacks["align"]("bottom"))

        #toggle grid
        self.canvas.bind("<Key-g>", lambda e: self.toggle_grid())

        #snap selected widgets to grid
        self.canvas.bind("<Key-s>", lambda e: callbacks["snap"](self.grid_size))