import tkinter as tk

class CanvasView:
    """
    Tk-only view that owns the inner drawing canvas
    and provides the grid rendering API
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        parent: tk.Canvas,
        canvas_width: int,
        canvas_height: int,
        background_color: str
    ):
        """initialize the canvas view and construct the drawing canvas"""
        self.parent = parent
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.grid_lines: list[int] = []
        self.canvas = tk.Canvas(
            self.parent,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=background_color,
            highlightthickness=0,
            takefocus=1
        )

    #Rendering API------------------------------------------------------------------------------------------------------
    def render_grid(self, grid_size: int, grid_color: str, grid_visible: bool):
        """redraw or remove the grid display based on visibility state"""
        if grid_visible:
            self._clear_grid()
            self._draw_grid(grid_size, grid_color)
        else:
            self._clear_grid()

    #Internals----------------------------------------------------------------------------------------------------------
    def _draw_grid(self, grid_size: int, grid_color: str):
        """draw the grid lines on the canvas"""
        width, height = self.canvas_width, self.canvas_height

        for x in range(0, width, grid_size):
            line = self.canvas.create_line(x, 0, x, height, fill=grid_color)
            self.grid_lines.append(line)

        for y in range(0, height, grid_size):
            line = self.canvas.create_line(0, y, width, y, fill=grid_color)
            self.grid_lines.append(line)

    def _clear_grid(self):
        """remove all existing grid lines"""
        for line in self.grid_lines:
            self.canvas.delete(line)
        self.grid_lines.clear()