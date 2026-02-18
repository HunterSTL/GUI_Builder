import tkinter as tk
from typing import Dict
from _dataclasses import RectangleSelectionState, WidgetDragState
from CallTracer import call_tracer

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
        callbacks: dict,
        resolve_model_to_widget,
        resolve_widget_to_model
    ):
        """initialize selection manager, drag states, outline tracking, and callbacks"""
        self.canvas = canvas
        self.ctrl_key = ctrl_key
        self.selection_width = selection_width
        self.selection_dash = selection_dash
        self.selection_padding = selection_padding
        self.selection_color = selection_color
        self.last_selected_color = last_selected_color
        self.drag_threshold = drag_threshold
        self.callbacks = callbacks

        self._resolve_model_to_widget = resolve_model_to_widget             #label1 → 1
        self._resolve_widget_to_model = resolve_widget_to_model             #1 → label1

        self._selected_models: set[str] = set()                             #selected model IDs
        self._last_selected_model = None

        self._rects: Dict[str, int] = {}                                    #model -> rectangle_id
        self._in_canvas_drag = False

        self._mode = None                                                   #mode (selection or drag)

        self._rectangle_selection_state = RectangleSelectionState()         #rectangle selection state

        self._widget_drag_state = WidgetDragState()                         #widget drag state

    def clear(self):
        """clear the entire selection and remove all outlines"""
        for model_id in list(self._selected_models):
            self._remove_highlight(model_id)
        self._selected_models.clear()
        self._last_selected_model = None

        self.callbacks["attributes_panel"]()                                #selection changed → check if attributes panel should be shown

    def select_only(self, model_id: str):
        """select only the given model_id"""
        if model_id is None:
            self.clear()
            return
        for other in list(self._selected_models):
            if other != model_id:
                self._remove_highlight(other)
        self._selected_models = {model_id}
        self._last_selected_model = model_id

        self.callbacks["attributes_panel"]()                                #selection changed → check if attributes panel should be shown

    def toggle(self, model_id: str):
        """toggle selection state of a given model_id"""
        if model_id is None:
            return
        if model_id in self._selected_models:
            self._remove_highlight(model_id)
            self._selected_models.remove(model_id)
        else:
            self._selected_models.add(model_id)
            self._last_selected_model = model_id
    
        self.callbacks["attributes_panel"]()                                #selection changed → check if attributes panel should be shown

    def select_widget(self, model_id: str, event):
        """select a widget, respecting CTRL for additive selection"""
        if bool(event.state & self.ctrl_key):
            self.toggle(model_id)
        else:
            if model_id not in self.selected_model_ids():
                self.select_only(model_id)

        self.refresh_all()                                                  #refresh outlines

    def select_all(self):
        """select all widgets in the canvas"""
        self.clear()                                                        #clear existing selection

        widgets = self.canvas.find_all()                                    #select all items with type "window" (=widget)
        for widget_id in widgets:
            if self.canvas.type(widget_id) == "window":
                model_id = self._resolve_widget_to_model(widget_id)
                self.toggle(model_id)

        self.refresh_all()                                                  #refresh outlines

    def selected_model_ids(self) -> frozenset[str]:
        """return a frozenset of selected model IDs"""
        return frozenset(self._selected_models)

    def last_selected_model_id(self):
        """return the model ID of the last selected widget"""
        return self._last_selected_model

    def refresh(self, model_id: str):
        """refresh the outline for a single widget"""
        self.canvas.after_idle(lambda:self._ensure_highlight(model_id))

    def refresh_all(self):
        """refresh outlines of all selected widgets"""
        for model_id in self._selected_models:
            self._ensure_highlight(model_id)

    def start_widget_drag(self, event):
        """record drag start position and notify Designer"""
        wds = self._widget_drag_state
        wds.start_coords = self._pointer_in_canvas_coords(event)
        wds.last_total_dx = 0
        wds.last_total_dy = 0
        wds.is_dragging = False

        try:
            self.canvas.grab_set()
        except Exception:
            pass

        self.callbacks["widget"]["start_drag"]()                            #notify Designer that drag gesture starts (initializes MoveWidgetsTo command to store original widget positions)

    def handle_widget_drag(self, event, move_callback):
        """handle widget drag movement, applying deltas after threshold"""
        wds = self._widget_drag_state

        if not wds:
            return

        canvas_x, canvas_y = self._pointer_in_canvas_coords(event)
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

        #defer movement to idle time to prevent re-entry
        self.canvas.after_idle(lambda: move_callback(incremental_dx, incremental_dy))

    def end_widget_drag(self):
        """reset widget drag state and notify Designer"""
        wds = self._widget_drag_state
        wds.start_coords = None
        wds.is_dragging = False

        try:
            self.canvas.grab_release()
        except Exception:
            pass

        self.callbacks["widget"]["end_drag"]()                              #notify Designer that drag gesture ends (executes the MoveWidgetsTo command)

    def start_rectangle_selection(self, event):
        """begin a rectangle selection gesture"""
        rss = self._rectangle_selection_state
        canvas_x, canvas_y = self._pointer_in_canvas_coords(event)
        rss.start_coords = (canvas_x, canvas_y)
        rss.is_additive = bool(event.state & self.ctrl_key)

        if rss.selection_rectangle_id is None:                              #create/update rectangle outline
            rss.selection_rectangle_id = self.canvas.create_rectangle(
                canvas_x, canvas_y, canvas_x, canvas_y,
                outline=self.selection_color, width=self.selection_width, dash=self.selection_dash, fill=""
            )
        else:
            self.canvas.coords(rss.selection_rectangle_id, canvas_x, canvas_y, canvas_x, canvas_y)

        self.canvas.tag_raise(rss.selection_rectangle_id)                   #ensure outline is on top

    def update_selection_rectangle(self, event):
        """update the rectangle selection outline while dragging"""
        rss = self._rectangle_selection_state

        if not rss.start_coords:
            return

        rss.is_dragging = True

        x0, y0 = rss.start_coords                                           #get rectangle coords (start coords + current pointer)
        x1, y1 = self._pointer_in_canvas_coords(event)

        #update rectangle
        self.canvas.coords(rss.selection_rectangle_id, x0, y0, x1, y1)
        self.canvas.tag_raise(rss.selection_rectangle_id)

    def handle_canvas_press(self, event):
        """handle mouse press, deciding between selection or dragging mode"""
        canvas_x, canvas_y = self._pointer_in_canvas_coords(event)
        model_id = self.model_at_click_location(canvas_x, canvas_y)         #check for model at canvas coords

        if model_id:                                                        #widget clicked → set mode to "drag" → start widget drag
            self.select_widget(model_id, event)                             #select the clicked widget (toggle or select_only based on CTRL-key)
            self._mode = "drag"
            self.start_widget_drag(event)                                   #record start coords for widget drag and notify designer of drag start
        else:                                                               #no widget clicked → set mode to "selection" → start rectangle selection
            self._mode = "selection"
            self.start_rectangle_selection(event)                           #record start coords for rectangle selection and create/update rectangle outline

    def handle_canvas_drag(self, event):
        """handle drag and delegate to drag or selection logic"""
        if getattr(self, "_in_canvas_drag", False):
            call_tracer.log_event("REENTRY")
            return

        self._in_canvas_drag = True
        try:
            if self._mode == "drag":                                        #move selected widgets
                self.handle_widget_drag(event, self.callbacks["widget"]["move"])
            elif self._mode == "selection":                                 #update selection rectangle
                self.update_selection_rectangle(event)
        finally:
            self._in_canvas_drag = False

    def handle_canvas_release(self, event):
        """finalize drag or rectangle selection"""
        if self._mode == "drag":
            self.end_widget_drag()
        elif self._mode == "selection":
            rss = self._rectangle_selection_state

            try:
                if not rss.start_coords:
                    return

                start_x, start_y = rss.start_coords                         #get rectangle coords (start coords + current pointer)
                canvas_x, canvas_y = self._pointer_in_canvas_coords(event)

                rss.start_coords = None                                     #reset start coords

                x0n, x1n = sorted((start_x, canvas_x))                      #normalize corners
                y0n, y1n = sorted((start_y, canvas_y))

                if not rss.is_dragging:                                     #when dragging is false → treat as normal click
                    model_id = self.model_at_click_location(canvas_x, canvas_y)
                    if model_id is None:
                        self.clear()
                    else:
                        if rss.is_additive:
                            self.toggle(model_id)
                        else:
                            self.select_only(model_id)
                else:                                                       #when dragging is true → select all items fully enclosed by rectangle selection
                    enclosed_widgets = self.canvas.find_enclosed(x0n, y0n, x1n, y1n)
                    #filter out everything that's not a window item
                    enclosed_windows = [i for i in enclosed_widgets if self.canvas.type(i) == "window"]

                    if rss.is_additive:
                        for widget_id in enclosed_windows:
                            model_id = self._resolve_widget_to_model(widget_id)
                            if model_id not in self.selected_model_ids():
                                self.toggle(model_id)                      #only toggle widgets that are not yet selected
                    else:
                        self.clear()
                        for widget_id in enclosed_windows:
                            model_id = self._resolve_widget_to_model(widget_id)
                            self.toggle(model_id)
            finally:
                self.refresh_all()                                          #refresh outlines

                if rss.selection_rectangle_id:                              #remove selection rectangle
                    self.canvas.delete(rss.selection_rectangle_id)
                    rss.selection_rectangle_id = None

                rss.is_dragging = False
                rss.is_additive = False
        self._mode = None

    def is_dragging(self):
        """return True if a widget drag gesture is active"""
        return self._widget_drag_state.is_dragging

    def model_at_click_location(self, x: int, y: int):
        """return model_id at the given canvas coordinates"""
        widget_id = self._find_topmost_window_at(x, y)
        return self._resolve_widget_to_model(widget_id)

    def _pointer_in_canvas_coords(self, event):
        """convert event coordinates to canvas coordinates"""
        return int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))

    def _find_topmost_window_at(self, x: int, y: int):
        """return the topmost widget window at the given position"""
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):                                        #last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None

    def _ensure_highlight(self, model_id: str):
        """ensure outline rectangle exists and matches widget position"""
        if model_id not in self._selected_models:                           #only draw outline if item is selected:
            self._remove_highlight(model_id)
            return

        widget_id = self._resolve_model_to_widget(model_id)
        bbox = self.canvas.bbox(widget_id)
        if not bbox:
            self._remove_highlight(model_id)
            return

        x1, y1, x2, y2 = bbox
        x1 -= self.selection_padding
        y1 -= self.selection_padding
        x2 += self.selection_padding
        y2 += self.selection_padding

        outline_color = self.last_selected_color if self._last_selected_model == model_id else self.selection_color
        rect_id = self._rects.get(model_id)

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
            self._rects[model_id] = rect_id
        self.canvas.tag_raise(rect_id)

    def _remove_highlight(self, model_id: str):
        """remove highlight rectangle for a model_id"""
        rect_id = self._rects.pop(model_id, None)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.delete(rect_id)