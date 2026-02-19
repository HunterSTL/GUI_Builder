import tkinter as tk
from _dataclasses import ProjectDocument

class CanvasView:
    """tk-only view: creates the inner canvas and renders the grid"""
    def __init__(
        self,
        parent: tk.Canvas,
        project_document: ProjectDocument
    ):
        """initialize the canvas view and construct the drawing canvas"""
        self.parent = parent
        self.project_document = project_document

        self.grid_lines: list[int] = []
        self.canvas = tk.Canvas(
            self.parent,
            width=self.project_document.width,
            height=self.project_document.height,
            bg=self.project_document.theme["background"]["color"],
            highlightthickness=0,
            takefocus=1
        )

    def refresh_grid(self):
        """redraw or remove the grid display based on visibility state"""
        if self.project_document.grid.visible:
            self._clear_grid()
            self._draw_grid()
        else:
            self._clear_grid()

    def _draw_grid(self):
        """draw the grid lines on the canvas"""
        width = self.project_document.width
        height = self.project_document.height
        grid_size = self.project_document.grid.size
        grid_color = self.project_document.grid.color

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