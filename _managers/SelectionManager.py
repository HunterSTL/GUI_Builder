import tkinter as tk
from typing import Dict, Optional, Set
from _dataclasses import RectangleSelectionState, WidgetDragState

class SelectionManager:
    def __init__(
            self,
            canvas: tk.Canvas,
            ctrl_key: str,
            selection_width: int,
            selection_dash: tuple[int],
            selection_padding: int,
            selection_color: str,
            last_selected_color: str,
            drag_threshold: int,
            callbacks: dict
        ):
        self.canvas = canvas
        self.ctrl_key = ctrl_key
        self.selection_width = selection_width
        self.selection_dash = selection_dash
        self.selection_padding = selection_padding
        self.selection_color = selection_color
        self.last_selected_color = last_selected_color
        self.drag_threshold = drag_threshold
        self.callbacks = callbacks

        self._selected: Set[int] = set()                                    #selected widget IDs (window items)
        self._rects: Dict[int, int] = {}                                    #widget_id -> rectangle_id
        self._last_selected = None

        self._mode = None                                                   #mode (selection or drag)

        self._rectangle_selection_state = RectangleSelectionState()         #rectangle selection state

        self._widget_drag_state = WidgetDragState()                         #widget drag state

    #clears the entire selection
    def clear(self):
        for widget_id in list(self._selected):
            self._remove_highlight(widget_id)
        self._selected.clear()
        self._last_selected = None

    #selects only the widget with the given widget_id
    def select_only(self, widget_id: Optional[int]):
        if widget_id is None:
            self.clear()
            return
        for other in list(self._selected):
            if other != widget_id:
                self._remove_highlight(other)
        self._selected = {widget_id}
        self._last_selected = widget_id

        self.callbacks["attributes_panel"]()                                #selection changed → check if attributes panel should be shown

    #toggles the widget with the given widget_id
    def toggle(self, widget_id: Optional[int]):
        if widget_id is None:
            return
        if widget_id in self._selected:
            self._remove_highlight(widget_id)
            self._selected.remove(widget_id)
        else:
            self._selected.add(widget_id)
            self._last_selected = widget_id

        self.callbacks["attributes_panel"]()                                #selection changed → check if attributes panel should be shown

    #selects the widget with the given widget_id (toggle or select_only based on CTRL-key) then refreshes outlines
    def select_widget(self, widget_id: int, event):
        if bool(event.state & self.ctrl_key):
            self.toggle(widget_id)
        else:
            if widget_id not in self.selected_ids():
                self.select_only(widget_id)

        self.refresh_all()                                                  #refresh outlines

    #selects all widgets
    def select_all(self):
        self.clear()                                                        #clear existing selection

        items = self.canvas.find_all()                                      #select all items with type "window" (=widget)
        for item in items:
            if self.canvas.type(item) == "window":
                self.toggle(item)

        self.refresh_all()                                                  #refresh outlines

    #returns a frozenset (so the collection can't be mutated) of all selected widget_ids
    def selected_ids(self) -> frozenset[int]:
        return frozenset(self._selected)

    #returns the widget_id of the last selected widget
    def last_selected_id(self):
        return self._last_selected

    #refreshes the outline for the widget with the given widget_id
    def refresh(self, widget_id: int):
        self._ensure_highlight(widget_id)

    #refreshes the ouline of all widgets
    def refresh_all(self):
        for widget_id in self._selected:
            self._ensure_highlight(widget_id)

    #records mouse position at drag start and notifies the designer of the drag start
    def start_widget_drag(self):
        wds = self._widget_drag_state
        wds.start_coords = self._pointer_in_canvas_coords()
        wds.last_total_dx = 0
        wds.last_total_dy = 0
        wds.is_dragging = False

        self.callbacks["widget"]["start_drag"]()                            #notify Designer that drag gesture starts (initializes MoveWidgetsTo command to store original widget positions)

    #computes drag delta and applies if threshold is exceeded
    def handle_widget_drag(self, move_callback):
        wds = self._widget_drag_state

        if not wds:
            return

        canvas_x, canvas_y = self._pointer_in_canvas_coords()

        total_dx = canvas_x - wds.start_coords[0]                           #total delta (since drag start)
        total_dy = canvas_y - wds.start_coords[1]

        incremental_dx = total_dx - wds.last_total_dx                       #incremental delta (since last drag event)
        incremental_dy = total_dy - wds.last_total_dy

        wds.last_total_dx = total_dx                                        #update last total delta (how much of the total_dx/dy has already been applied)
        wds.last_total_dy = total_dy

        if total_dx == 0 and total_dy == 0:
            return

        if not wds.is_dragging:
            if abs(total_dx) + abs(total_dy) < self.drag_threshold:
                return

            wds.is_dragging = True                                          #threshold is exceeded → set _dragging_widgets to True
            wds.last_total_dx = 0
            wds.last_total_dy = 0

        move_callback(incremental_dx, incremental_dy)
        return

    #resets widget drag state
    def end_widget_drag(self):
        wds = self._widget_drag_state
        wds.start_coords = None
        wds.is_dragging = False

        self.callbacks["widget"]["end_drag"]()                              #notify Designer that drag gesture ends (executes the MoveWidgetsTo command)

    #records start coordinates an whether ctrl is held (additive selection)
    def start_rectangle_selection(self, x, y, event):
        rss = self._rectangle_selection_state
        rss.start_coords = (x, y)
        rss.is_additive = bool(event.state & self.ctrl_key)

        if rss.selection_rectangle_id is None:                              #create/update rectangle outline
            rss.selection_rectangle_id = self.canvas.create_rectangle(
                x, y, x, y,
                outline=self.selection_color, width=self.selection_width, dash=self.selection_dash, fill=""
            )
        else:
            self.canvas.coords(rss.selection_rectangle_id, x, y, x, y)

        self.canvas.tag_raise(rss.selection_rectangle_id)                   #ensure outline is on top

    #updates the selection rectangle to span from RectangleSelectionState.start_coords to the current mouse position
    def update_selection_rectangle(self):
        rss = self._rectangle_selection_state

        if not rss.start_coords:
            return

        rss.is_dragging = True

        x0, y0 = rss.start_coords                                           #get rectangle coords (start coords + current pointer)
        x1, y1 = self._pointer_in_canvas_coords()

        #update rectangle
        self.canvas.coords(rss.selection_rectangle_id, x0, y0, x1, y1)
        self.canvas.tag_raise(rss.selection_rectangle_id)

    #check for widget at click position
    #if widget was clicked → sets mode to "drag" → starts widget drag
    #if canvas was clicked → sets mode to "selection" → starts rectangle selection
    def handle_canvas_press(self, event):
        canvas_x, canvas_y = self._pointer_in_canvas_coords()               #get canvas coords

        clicked_widget = self._find_topmost_window_at(canvas_x, canvas_y)   #check for widget at canvas coords

        if clicked_widget:                                                  #widget clicked → set mode to "drag" → start widget drag
            self.select_widget(clicked_widget, event)                       #select the clicked widget (toggle or select_only based on CTRL-key)
            self._mode = "drag"
            self.start_widget_drag()                                        #record start coords for widget drag and notify designer of drag start
        else:                                                               #no widget clicked → set mode to "selection" → start rectangle selection
            self._mode = "selection"
            self.start_rectangle_selection(canvas_x, canvas_y, event)       #record start coords for rectangle selection and create/update rectangle outline

    #if mode is "drag": computes drag delta and applies if threshold is exceeded
    #if mode is "selection": resizes the selection rectangle based on mouse movement
    def handle_canvas_drag(self):
        if self._mode == "drag":                                            #move selected widgets
            self.handle_widget_drag(self.callbacks["widget"]["move"])
        elif self._mode == "selection":                                     #update selection rectangle
            self.update_selection_rectangle()

    #if mode is "drag": resets the drag state
    #if mode is "selection": selects all widgets that are fully enclosed in the selection rectangle
    def handle_canvas_release(self):
        if self._mode == "drag":
            self.end_widget_drag()
        elif self._mode == "selection":
            rss = self._rectangle_selection_state

            try:
                if not rss.start_coords:
                    return

                start_x, start_y = rss.start_coords                         #get rectangle coords (start coords + current pointer)
                canvas_x, canvas_y = self._pointer_in_canvas_coords()

                rss.start_coords = None                                     #reset start coords

                x0n, x1n = sorted((start_x, canvas_x))                      #normalize corners
                y0n, y1n = sorted((start_y, canvas_y))

                if not rss.is_dragging:                                     #when dragging is false → treat as normal click
                    widget_id = self._find_topmost_window_at(canvas_x, canvas_y)
                    if widget_id is None:
                        self.clear()
                    else:
                        if rss.is_additive:
                            self.toggle(widget_id)
                        else:
                            self.select_only(widget_id)
                    self.callbacks["attributes_panel"]()                    #selection changed → check if attributes panel should be shown
                else:                                                       #when dragging is true → select all items fully enclosed by rectangle selection
                    enclosed_widgets = self.canvas.find_enclosed(x0n, y0n, x1n, y1n)
                    #filter out everything that's not a window item
                    enclosed_windows = [i for i in enclosed_widgets if self.canvas.type(i) == "window"]

                    if rss.is_additive:
                        for widget_id in enclosed_windows:
                            if widget_id not in self.selected_ids():
                                self.toggle(widget_id)                      #only toggle widgets that are not yet selected
                    else:
                        self.clear()
                        for widget_id in enclosed_windows:
                            self.toggle(widget_id)
                    self.callbacks["attributes_panel"]()                    #selection changed → check if attributes panel should be shown
            finally:
                self.refresh_all()                                          #refresh outlines

                if rss.selection_rectangle_id:                              #remove selection rectangle
                    self.canvas.delete(rss.selection_rectangle_id)
                    rss.selection_rectangle_id = None

                rss.is_dragging = False
                rss.is_additive = False
        self._mode = None

    def is_dragging(self):
        return self._widget_drag_state.is_dragging

    #returns pointer in canvas coordinates
    def _pointer_in_canvas_coords(self):
        pointer_x = self.canvas.winfo_pointerx()                            #screen coordinates
        pointer_y = self.canvas.winfo_pointery()
        window_x = pointer_x - self.canvas.winfo_rootx()                    #window coordinates
        window_y = pointer_y - self.canvas.winfo_rooty()
        return int(self.canvas.canvasx(window_x)), int(self.canvas.canvasy(window_y))

    #find clicked widget
    def _find_topmost_window_at(self, x: int, y: int):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):                                        #last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None

    def _ensure_highlight(self, widget_id: int):
        if widget_id not in self._selected:                                 #only draw outline if item is selected:
            self._remove_highlight(widget_id)
            return

        bbox = self.canvas.bbox(widget_id)
        if not bbox:
            return

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

    def _remove_highlight(self, widget_id: int):
        rect_id = self._rects.pop(widget_id, None)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.delete(rect_id)