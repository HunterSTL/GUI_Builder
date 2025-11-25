import tkinter as tk
from Theme import *
from typing import Dict, Optional, Set

class SelectionManager:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self._selected: Set[int] = set()          #selected canvas item IDs (window items)
        self._rects: Dict[int, int] = {}          #window_id -> rectangle_id
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
        for item_id in list(self._selected):
            self._remove_highlight(item_id)
        self._selected.clear()

    def select_only(self, item_id: Optional[int]):
        if item_id is None:
            self.clear()
            return
        for other in list(self._selected):
            if other != item_id:
                self._remove_highlight(other)
        self._selected = {item_id}
        self._last_selected = item_id

    def toggle(self, item_id: Optional[int]):
        if item_id is None:
            return
        if item_id in self._selected:
            self._remove_highlight(item_id)
            self._selected.remove(item_id)
        else:
            self._selected.add(item_id)
            self._last_selected = item_id

    def selected_ids(self) -> frozenset[int]:
        return frozenset(self._selected)    #frozenset so external code can't mutate the collection

    def refresh(self, item_id: int):
        self._ensure_highlight(item_id)

    def refresh_all(self):
        for item_id in self._selected:
            self._ensure_highlight(item_id)

    #create selection rectangle
    def handle_canvas_press(self, event):
        #record start coordinates and whether ctrl is held
        self._rectangle_selection_start = (event.x, event.y)
        self._rectangle_selection_dragging = False
        self._rectangle_selection_additive = bool(event.state & 0x0004)     #0x0004 = ctrl key

        #create rectangle outline
        if self._rectangle_selection_id is None:
            self._rectangle_selection_id = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline=SELECTION_COLOR, width=SELECTION_WIDTH, dash=SELECTION_DASH, fill=""
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
                item_id = self._find_topmost_window_at(event.x, event.y)
                if item_id is None:
                    self.clear()
                else:
                    if self._rectangle_selection_additive:
                        self.toggle(item_id)
                    else:
                        self.select_only(item_id)
                if sync_callback:
                    sync_callback()
            #when dragging is true → select all items fully enclosed by rectangle selection
            else:
                enclosed_widgets = self.canvas.find_enclosed(x0n, y0n, x1n, y1n)
                #filter out everything that's not a window item
                enclosed_windows = [i for i in enclosed_widgets if self.canvas.type(i) == "window"]

                if self._rectangle_selection_additive:
                    for window_id in enclosed_windows:
                        if window_id not in self.selected_ids():
                            self.toggle(window_id)    #only toggle widgets that are not yet selected
                else:
                    self.clear()
                    for window_id in enclosed_windows:
                        self.toggle(window_id)

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
    def handle_widget_click(self, event, item_id: int):
        if bool(event.state & 0x0004):
            self.toggle(item_id)
        else:
            if item_id not in self.selected_ids():
                self.select_only(item_id)

        self.refresh_all()
        return "break"  #prevent canvas from clearing selection

    def start_widget_drag(self, event):
        self._widget_drag_start = (event.x_root, event.y_root)
        self._widget_drag_end = (event.x_root, event.y_root)
        self._dragging_widgets = False

    def handle_widget_drag(self, event, widget_map, clamped_delta):
        if not self._widget_drag_start:
            return "break"

        dx, dy = event.x_root - self._widget_drag_end[0], event.y_root - self._widget_drag_end[1]
        dx, dy = clamped_delta(dx, dy)

        #check drag threshold before moving widgets
        if not self._dragging_widgets:
            self._dragging_widgets = True

        #move selected widgets
        for item_id in self.selected_ids():
            self.canvas.move(item_id, dx, dy)
            model = widget_map.get(item_id)
            if model:
                model.x += dx
                model.y += dy

            self.refresh(item_id)

        self._widget_drag_end = (event.x_root, event.y_root)
        return "break"

    def end_widget_drag(self):
        self._widget_drag_start = None
        self._widget_drag_end = None
        self._dragging_widgets = False
        return "break"

    #find clicked widget
    def _find_topmost_window_at(self, x: int, y: int):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):  #last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None

    def _ensure_highlight(self, item_id: int):
        #only draw outline if item is selected:
        if item_id not in self._selected:
            self._remove_highlight(item_id)
            return

        bbox = self.canvas.bbox(item_id)
        if not bbox:
            return  #item is outside view

        x1, y1, x2, y2 = bbox
        x1 -= SELECTION_PADDING
        y1 -= SELECTION_PADDING
        x2 += SELECTION_PADDING
        y2 += SELECTION_PADDING

        outline_color = LAST_SELECTED_COLOR if self._last_selected == item_id else SELECTION_COLOR
        rect_id = self._rects.get(item_id)

        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.coords(rect_id, x1, y1, x2, y2)
            self.canvas.itemconfig(rect_id, outline=outline_color)
        else:
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=outline_color,
                width=SELECTION_WIDTH,
                dash=SELECTION_DASH,
                fill="",
            )
            self._rects[item_id] = rect_id
        self.canvas.tag_raise(rect_id)

    def _remove_highlight(self, item_id: int):
        rect_id = self._rects.pop(item_id, None)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.delete(rect_id)