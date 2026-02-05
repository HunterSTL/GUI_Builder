import tkinter as tk
from typing import Dict, Optional, Set

class SelectionManager:
    def __init__(
            self,
            canvas: tk.Canvas,
            ctrl_key: str,
            selection_width: int,
            selection_dash: tuple[int],
            selection_padding: int,
            selection_color: str,
            last_selected_color: str
        ):
        self.canvas = canvas
        self.ctrl_key = ctrl_key
        self.selection_width = selection_width
        self.selection_dash = selection_dash
        self.selection_padding = selection_padding
        self.selection_color = selection_color
        self.last_selected_color = last_selected_color

        self._selected: Set[int] = set()          #selected widget IDs (window items)
        self._rects: Dict[int, int] = {}          #widget_id -> rectangle_id
        self._last_selected = None

        #rectangle selection state
        self._rectangle_selection_id:  Optional[int] = None
        self._rectangle_selection_start: Optional[tuple[int, int]] = None
        self._rectangle_selection_dragging: bool = False
        self._rectangle_selection_additive: bool = False

        #widget drag state
        self._widget_drag_start = None
        self._widget_drag_end = None
        self._dragging_widgets = False

    def clear(self):
        for widget_id in list(self._selected):
            self._remove_highlight(widget_id)
        self._selected.clear()
        self._last_selected = None

    def select_only(self, widget_id: Optional[int]):
        if widget_id is None:
            self.clear()
            return
        for other in list(self._selected):
            if other != widget_id:
                self._remove_highlight(other)
        self._selected = {widget_id}
        self._last_selected = widget_id

    def toggle(self, widget_id: Optional[int]):
        if widget_id is None:
            return
        if widget_id in self._selected:
            self._remove_highlight(widget_id)
            self._selected.remove(widget_id)
        else:
            self._selected.add(widget_id)
            self._last_selected = widget_id

    def select_all(self):
        #clear existing selection
        self.clear()

        #select all items with type "window" (=widget)
        items = self.canvas.find_all()
        for item in items:
            if self.canvas.type(item) == "window":
                self.toggle(item)

        #refresh outline
        self.refresh_all()

    def selected_ids(self) -> frozenset[int]:
        return frozenset(self._selected)    #frozenset so external code can't mutate the collection

    def last_selected_id(self):
        return self._last_selected

    def refresh(self, widget_id: int):
        self._ensure_highlight(widget_id)

    def refresh_all(self):
        for widget_id in self._selected:
            self._ensure_highlight(widget_id)

    #create selection rectangle
    def handle_canvas_press(self, event):
        #record start coordinates and whether ctrl is held
        self._rectangle_selection_start = (event.x, event.y)
        self._rectangle_selection_dragging = False
        self._rectangle_selection_additive = bool(event.state & self.ctrl_key)

        #create or update rectangle outline
        if self._rectangle_selection_id is None:
            self._rectangle_selection_id = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline=self.selection_color, width=self.selection_width, dash=self.selection_dash, fill=""
            )
        else:
            self.canvas.coords(self._rectangle_selection_id, event.x, event.y, event.x, event.y)

        #make sure outline is on top
        self.canvas.tag_raise(self._rectangle_selection_id)

    #resize selection rectangle based on mouse movement
    def handle_canvas_drag(self, event):
        if not self._rectangle_selection_start:
            return
        self._rectangle_selection_dragging = True
        x0, y0 = self._rectangle_selection_start
        x1, y1 = event.x, event.y

        #update rectangle
        self.canvas.coords(self._rectangle_selection_id, x0, y0, x1, y1)
        self.canvas.tag_raise(self._rectangle_selection_id)

    #select all widgets that are fully enclosed in the selection rectangle
    def handle_canvas_release(self, event, sync_callback):
        try:
            if not self._rectangle_selection_start:
                return

            x0, y0 = self._rectangle_selection_start
            x1, y1 = event.x, event.y
            self._rectangle_selection_start = None

            #normalize corners
            x0n, x1n = sorted((x0, x1))
            y0n, y1n = sorted((y0, y1))

            #when dragging is false → treat as normal click
            if not self._rectangle_selection_dragging:
                widget_id = self._find_topmost_window_at(event.x, event.y)
                if widget_id is None:
                    self.clear()
                else:
                    if self._rectangle_selection_additive:
                        self.toggle(widget_id)
                    else:
                        self.select_only(widget_id)
                if sync_callback:
                    sync_callback()
            #when dragging is true → select all items fully enclosed by rectangle selection
            else:
                enclosed_widgets = self.canvas.find_enclosed(x0n, y0n, x1n, y1n)
                #filter out everything that's not a window item
                enclosed_windows = [i for i in enclosed_widgets if self.canvas.type(i) == "window"]

                if self._rectangle_selection_additive:
                    for widget_id in enclosed_windows:
                        if widget_id not in self.selected_ids():
                            self.toggle(widget_id)    #only toggle widgets that are not yet selected
                else:
                    self.clear()
                    for widget_id in enclosed_windows:
                        self.toggle(widget_id)

                if sync_callback:
                    sync_callback()
        finally:
            #refresh outlines
            self.refresh_all()

            #remove rectangle selection
            if self._rectangle_selection_id:
                self.canvas.delete(self._rectangle_selection_id)
                self._rectangle_selection_id = None

            self._rectangle_selection_dragging = False
            self._rectangle_selection_additive = False

    #select widget
    def handle_widget_click(self, event, widget_id: int):
        if bool(event.state & self.ctrl_key):
            self.toggle(widget_id)
        else:
            if widget_id not in self.selected_ids():
                self.select_only(widget_id)

        self.refresh_all()
        return "break"  #prevent canvas from clearing selection

    def start_widget_drag(self, event):
        #use canvas coordinates instead of screen coordinates (possible fix for wrong widget drag behaviour)
        self._widget_drag_start = (self.canvas.canvasx(event.x_root), self.canvas.canvasy(event.y_root))
        #self._widget_drag_start = (event.x_root, event.y_root)
        self._widget_drag_end = self._widget_drag_start
        self._dragging_widgets = False

    def handle_widget_drag(self, event, move_callback):
        if not self._widget_drag_start:
            return "break"

        dx, dy = event.x_root - self._widget_drag_end[0], event.y_root - self._widget_drag_end[1]

        if not self._dragging_widgets:
            self._dragging_widgets = True

        if callable(move_callback):
            move_callback(dx, dy)

        self._widget_drag_end = (event.x_root, event.y_root)
        return "break"

    def end_widget_drag(self):
        self._widget_drag_start = None
        self._widget_drag_end = None
        self._dragging_widgets = False
        return "break"

    def is_dragging(self):
        return self._dragging_widgets

    #find clicked widget
    def _find_topmost_window_at(self, x: int, y: int):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):  #last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None

    def _ensure_highlight(self, widget_id: int):
        #only draw outline if item is selected:
        if widget_id not in self._selected:
            self._remove_highlight(widget_id)
            return

        bbox = self.canvas.bbox(widget_id)
        if not bbox:
            return  #item is outside view

        x1, y1, x2, y2 = bbox
        x1 -= self.selection_padding
        y1 -= self.selection_padding
        x2 += self.selection_padding
        y2 += self.selection_padding

        outline_color = self.last_selected_color if self._last_selected == widget_id else self.selection_color
        rect_id = self._rects.get(widget_id)

        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.coords(rect_id, x1, y1, x2, y2)
            self.canvas.itemconfig(rect_id, outline=outline_color)
        else:
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=outline_color,
                width=self.selection_width,
                dash=self.selection_dash,
                fill="",
            )
            self._rects[widget_id] = rect_id
        self.canvas.tag_raise(rect_id)
        self.canvas.update_idletasks()

    def _remove_highlight(self, widget_id: int):
        rect_id = self._rects.pop(widget_id, None)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.delete(rect_id)