import tkinter as tk
from utility import BoundingBox

class SelectionView:
    """
    Tk-only view that draws selection outlines and the selection rectangle (UI element) during a rectangle selection (gesture)
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        canvas: tk.Canvas,
        selection_color: str,
        last_selected_color: str,
        selection_width: int,
        selection_dash: tuple[int, int],
        selection_padding: int
    ):
        """store canvas and appearance settings"""
        self.canvas = canvas
        self.selection_color = selection_color
        self.last_selected_color = last_selected_color
        self.selection_width = selection_width
        self.selection_dash = selection_dash
        self.selection_padding = selection_padding

        self._selection_rectangle_id: int | None = None
        self._selection_outlines: dict[str, int] = {}   #{model.id: rectangle_id}

    #Rendering API------------------------------------------------------------------------------------------------------
    def update_outline_for(self, model_id: str, bounding_box: BoundingBox, is_last_selected: bool):
        """create or update the selection outline for a model ID using the given bounding box"""
        x1, y1 = bounding_box.left - self.selection_padding, bounding_box.top - self.selection_padding      #top-left corner of selection outline
        x2, y2 = bounding_box.right + self.selection_padding, bounding_box.bottom + self.selection_padding  #bottom-right corner of selection outline

        outline_color = self.last_selected_color if is_last_selected else self.selection_color
        rectangle_id = self._selection_outlines.get(model_id)

        if rectangle_id is None:
            rectangle_id = self._create_outline_for(model_id)

        self._update_outline(rectangle_id, x1, y1, x2, y2, outline_color)

    def delete_outline_for(self, model_id: str):
        """delete the selection outline for the given model ID"""
        if model_id not in self._selection_outlines:
            return

        rectangle_id = self._selection_outlines.pop(model_id)
        self.canvas.delete(rectangle_id)

    def clear_all_outlines(self):
        self.canvas.delete("selection_outline")
        self._selection_outlines.clear()

    def draw_selection_rectangle(self, x1: int, y1: int):
        """begin drawing the selection rectangle (UI-element) used for the rectangle selection (gesture)"""
        if self._selection_rectangle_id is None:
            self._selection_rectangle_id = self.canvas.create_rectangle(
                x1, y1, x1, y1,
                outline=self.selection_color,
                width=self.selection_width,
                dash=self.selection_dash,
                fill=""
            )
        else:
            self.canvas.coords(
                self._selection_rectangle_id,
                x1,
                y1,
                x1,
                y1
            )

        #ensure outline is on top
        self.canvas.tag_raise(self._selection_rectangle_id)

    def update_selection_rectangle(self, x1: int, y1: int, x2: int, y2: int):
        """update the selection rectangle while dragging"""
        if self._selection_rectangle_id is not None:
            self.canvas.coords(self._selection_rectangle_id, x1, y1, x2, y2)
            self.canvas.tag_raise(self._selection_rectangle_id)

    def clear_selection_rectangle(self):
        """remove the selection rectangle"""
        if self._selection_rectangle_id is not None:
            self.canvas.delete(self._selection_rectangle_id)
            self._selection_rectangle_id = None

    #Internals----------------------------------------------------------------------------------------------------------
    def _create_outline_for(self, model_id: str) -> int:
        rectangle_id = self.canvas.create_rectangle(
            0, 0, 0, 0,
            tags="selection_outline"
        )
        self._selection_outlines[model_id] = rectangle_id
        return rectangle_id

    def _update_outline(self, rectangle_id: int, x1: int, y1: int, x2: int, y2: int, outline_color: str):
        self.canvas.coords(rectangle_id, x1, y1, x2, y2)
        self.canvas.itemconfig(
            rectangle_id,
            outline=outline_color,
            width=self.selection_width,
            dash=self.selection_dash,
            fill="",
            tags="selection_outline"
        )
