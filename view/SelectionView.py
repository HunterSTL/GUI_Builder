import tkinter as tk

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

        self._selection_rectangle_id = None     #stores the id of the selection rectangle
        self._selection_outlines = {}           #model_id -> outline rectangle_id

    #Rendering API------------------------------------------------------------------------------------------------------
    def clear_selection_outlines(self):
        """delete all canvas items with tag "selection_outline" and clear the selection_outlines dictionary"""
        for rect_id in self.canvas.find_withtag("selection_outline"):
            self.canvas.delete(rect_id)
        self._selection_outlines.clear()

    def render_outline_for(self, model_id: str, last_selected_model: str | None, resolve_model_to_widget):
        """create or update the selection outline for a single selected widget"""
        widget_id = resolve_model_to_widget(model_id)
        if widget_id is None:
            return

        bbox = self.canvas.bbox(widget_id)
        if not bbox:
            return

        x1, y1, x2, y2 = bbox
        x1 -= self.selection_padding
        y1 -= self.selection_padding
        x2 += self.selection_padding
        y2 += self.selection_padding

        if last_selected_model == model_id:
            outline_color = self.last_selected_color
        else:
            outline_color = self.selection_color

        rect_id = self._selection_outlines.get(model_id)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            #update existing selection outline
            self.canvas.coords(rect_id, x1, y1, x2, y2)
            self.canvas.itemconfig(rect_id, outline=outline_color)
        else:
            #create new selection outline
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=outline_color,
                width=self.selection_width,
                dash=self.selection_dash,
                fill="",
                tags="selection_outline"
            )
            self._selection_outlines[model_id] = rect_id
        self.canvas.tag_raise(rect_id)

    def render_all_outlines(self, selected_models: frozenset[str], last_selected_model: str | None, resolve_model_to_widget):
        """clear existing selection outlines and recreate for all selected widgets"""
        self.clear_selection_outlines()

        #recreate outlines for selected models
        for model_id in selected_models:
            self.render_outline_for(model_id, last_selected_model, resolve_model_to_widget)

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