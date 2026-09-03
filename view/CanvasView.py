import tkinter as tk

from utility.AppTheme import BOUNDARY_COLOR


class CanvasView:
    """Owns the canvas and synchronizes the grid."""
    def __init__(
        self,
        parent: tk.Canvas,
        width: int,
        height: int,
        background_color: str
    ) -> None:
        self._width: int = width
        self._height: int = height

        self.canvas: tk.Canvas = tk.Canvas(
            parent,
            width=self._width,
            height=self._height,
            bg=background_color,
            highlightthickness=0,
            takefocus=1
        )

        self.canvas.create_rectangle(
            1, 1, self._width - 1, self._height - 1,
            outline=BOUNDARY_COLOR,
            width=1,
            dash=(2, 2)
        )

    def sync_grid(
        self,
        size: int,
        color: str,
        visible: bool
    ) -> None:
        """Synchronize the grid with the given configuration."""
        self.canvas.delete("grid")

        if not visible:
            return

        for x in range(0, self._width, size):
            self.canvas.create_line(
                x, 0, x, self._height,
                fill=color,
                tags="grid"
            )

        for y in range(0, self._height, size):
            self.canvas.create_line(
                0, y, self._width, y,
                fill=color,
                tags="grid"
            )
