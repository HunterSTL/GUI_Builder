import tkinter as tk
from Theme import NUDGE_SMALL, NUDGE_BIG

class CanvasManager:
    def __init__(self, parent: tk.Tk, width: int, height: int, bg_color: str, grid_size: int, grid_color: str):
        self.parent  = parent
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.grid_size = grid_size
        self.grid_color = grid_color
        self.canvas = None
        self.grid_lines = []
        self.show_grid = False

    def create_canvas(self):
        self.canvas = tk.Canvas(self.parent, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        return self.canvas

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

    def bind_events(self, context_menu_callback, selection_callbacks, move_callback, delete_callback):
        #bind context menu to right click
        self.canvas.bind("<Button-3>", context_menu_callback)

        #bind rectangle selection events
        self.canvas.bind("<ButtonPress-1>", selection_callbacks["press"])
        self.canvas.bind("<B1-Motion>", selection_callbacks["drag"])
        self.canvas.bind("<ButtonRelease-1>", selection_callbacks["release"])

        #binds events to move selected widgets
        self.canvas.focus_set()
        self.parent.bind("<Left>", lambda e: move_callback(-NUDGE_SMALL, 0))
        self.parent.bind("<Right>", lambda e: move_callback(NUDGE_SMALL, 0))
        self.parent.bind("<Up>", lambda e: move_callback(0, -NUDGE_SMALL))
        self.parent.bind("<Down>", lambda e: move_callback(0, NUDGE_SMALL))
        self.parent.bind("<Shift-Left>", lambda e: move_callback(-NUDGE_BIG, 0))
        self.parent.bind("<Shift-Right>", lambda e: move_callback(NUDGE_BIG, 0))
        self.parent.bind("<Shift-Up>", lambda e: move_callback(0, -NUDGE_BIG))
        self.parent.bind("<Shift-Down>", lambda e: move_callback(0, NUDGE_BIG))

        #delete selected widgets
        self.canvas.bind("<Delete>", lambda e: delete_callback())