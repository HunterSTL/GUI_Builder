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
        selection_dash: tuple[int],
        selection_padding: int
    ):
        """store canvas and appearance settings"""
        self.canvas = canvas
        self.selection_color = selection_color
        self.last_selected_color = last_selected_color
        self.selection_width = selection_width
        self.selection_dash = selection_dash
        self.selection_padding = selection_padding

        self._selection_rectangle_id = None     #stores the ID of the selection rectangle
        self._selection_outlines = {}           #maps model IDs to the ID of selection outline rectangles

    #Rendering API------------------------------------------------------------------------------------------------------
    def clear_selection_outlines(self):
        """delete all selection outlines and clear the dictionary mapping them to model IDs"""
        for rect_id in self.canvas.find_withtag("selection_outline"):
            self.canvas.delete(rect_id)
        self._selection_outlines.clear()

    def render_outline_for(self, model_id: str, bounding_box: BoundingBox, is_last_selected: bool):
        """render or update the selection outline for a model ID using the given bounding box"""
        #compute top-left corner of selection outline
        x1 = bounding_box.left - self.selection_padding
        y1 = bounding_box.top - self.selection_padding

        #compute bottom-right corner of selection outline
        x2 = bounding_box.right + self.selection_padding
        y2 = bounding_box.bottom + self.selection_padding

        #determine color
        outline_color = self.last_selected_color if is_last_selected else self.selection_color

        rectangle_id = self._selection_outlines.get(model_id)
        if rectangle_id and self.canvas.type(rectangle_id) == "rectangle":
            #update existing selection outline
            self.canvas.coords(rectangle_id, x1, y1, x2, y2)
            self.canvas.itemconfig(rectangle_id, outline=outline_color)
        else:
            #create new selection outline
            rectangle_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=outline_color,
                width=self.selection_width,
                dash=self.selection_dash,
                fill="",
                tags="selection_outline"
            )
            self._selection_outlines[model_id] = rectangle_id
        self.canvas.tag_raise(rectangle_id)

    def draw_selection_rectangle(self, x0: int, y0: int):
        """begin drawing the selection rectangle (UI-element) used for the rectangle selection (gesture)"""
        if self._selection_rectangle_id is None:
            self._selection_rectangle_id = self.canvas.create_rectangle(
                x0, y0, x0, y0,
                outline=self.selection_color,
                width=self.selection_width,
                dash=self.selection_dash,
                fill=""
            )
        else:
            self.canvas.coords(
                self._selection_rectangle_id,
                x0,
                y0,
                x0,
                y0
            )

        #ensure outline is on top
        self.canvas.tag_raise(self._selection_rectangle_id)

    def update_selection_rectangle(self, x0: int, y0: int, x1: int, y1: int):
        """update the selection rectangle while dragging"""
        if self._selection_rectangle_id is not None:
            self.canvas.coords(self._selection_rectangle_id, x0, y0, x1, y1)
            self.canvas.tag_raise(self._selection_rectangle_id)

    def clear_selection_rectangle(self):
        """remove the selection rectangle"""
        if self._selection_rectangle_id is not None:
            self.canvas.delete(self._selection_rectangle_id)
            self._selection_rectangle_id = None
