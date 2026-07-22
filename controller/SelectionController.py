import tkinter as tk
from model import WidgetDragState, RectangleSelectionState, BaseWidgetData
from view import SelectionView
from events import EventRouter
from AppState import AppState

class SelectionController:
    """
    Implements click selection, additive selection, rectangle selection,
    drag gestures, hit-testing and model based selection outline rendering.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        canvas: tk.Canvas,
        app_state: AppState,
        selection_view: SelectionView,
        ctrl_key: str,
        drag_threshold: int,
        resolve_widget_to_model,
        event_router: EventRouter
    ):
        """initialize selection/drag states and mappings"""
        self.canvas = canvas
        self.app_state = app_state
        self.selection_view = selection_view

        self.ctrl_key = ctrl_key
        self.drag_threshold = drag_threshold

        self.resolve_widget_to_model = resolve_widget_to_model  #resolves widget ID → model ID

        self.event_router = event_router

        #"selection", "drag" or None
        self._mode = None

        #is_dragging flag, drag start coordinates, last total delta
        self._widget_drag_state = WidgetDragState()

        #is_dragging and is_additive flags, drag start coordinates
        self._rectangle_selection_state = RectangleSelectionState()

    #Rendering API------------------------------------------------------------------------------------------------------
    def update_outline_for(self, model: BaseWidgetData):
        """create or update the selection outline for the given model based on selection state"""
        self.selection_view.update_outline_for(
            model_id=model.id,  #used to map selection outline rectangles to models
            bounding_box=self.app_state.get_model_bounding_box(model),
            is_last_selected=model.id == self.app_state.get_last_selected_model_id()
        )

    #Event handling-----------------------------------------------------------------------------------------------------
    def handle_canvas_press(self, event):
        """handle mouse press, deciding between selection or dragging mode"""
        canvas_x, canvas_y = self.pointer_in_canvas_coords(event)

        #check for model at canvas coords
        model_id = self.model_id_at(canvas_x, canvas_y)

        if model_id:
            #widget clicked → set mode to "drag" → start widget drag
            self._mode = "drag"

            #check if ctrl-key is pressed
            is_additive = bool(event.state & self.ctrl_key)

            #select the clicked widget (toggle or select_only based on CTRL-key)
            self.app_state.selection_handle_click(model_id, is_additive)

            #record start coords for widget drag and notify designer of drag start
            self.start_widget_drag(event)
        else:
            #no widget clicked → set mode to "selection" → start rectangle selection
            self._mode = "selection"

            #record start coords for rectangle selection and create/update rectangle outline
            self.start_rectangle_selection(event)

    def handle_canvas_drag(self, event):
        """handle drag by delegating to drag or selection logic"""
        if self._mode == "drag":
            #move selected widgets
            self.handle_widget_drag(event)
        elif self._mode == "selection":
            #update selection rectangle
            self.update_rectangle_selection(event)

    def handle_canvas_release(self, event):
        """finalize drag or rectangle selection and reset mode to None"""
        if self._mode == "drag":
            self.end_widget_drag()
        elif self._mode == "selection":
            self.end_rectangle_selection(event)

        self._mode = None

    #Domain logic-------------------------------------------------------------------------------------------------------
    def start_widget_drag(self, event):
        """begin a widget drag by recording drag start position and notifying the Designer (to store original widget positions)"""
        wds = self._widget_drag_state

        wds.drag_start_coords = self.pointer_in_canvas_coords(event)
        wds.last_total_dx = 0
        wds.last_total_dy = 0
        wds.is_dragging = False

        try:
            self.canvas.grab_set()
        except Exception:
            pass

        #notify Designer that drag gesture starts (initializes MoveWidgetsTo command to store original widget positions)
        self.event_router.emit("widget.drag.start")

    def handle_widget_drag(self, event):
        """handle widget drag movement, applying deltas after threshold"""
        wds = self._widget_drag_state
        if not wds.drag_start_coords:
            return

        canvas_x, canvas_y = self.pointer_in_canvas_coords(event)

        #total delta (since drag start)
        total_dx = canvas_x - wds.drag_start_coords[0]
        total_dy = canvas_y - wds.drag_start_coords[1]

        #incremental delta (since last drag event)
        incremental_dx = total_dx - wds.last_total_dx
        incremental_dy = total_dy - wds.last_total_dy

        #update last total delta (how much of the total_dx/dy has already been applied)
        wds.last_total_dx = total_dx
        wds.last_total_dy = total_dy

        if total_dx == 0 and total_dy == 0:
            return

        if not wds.is_dragging:
            #apply threshold
            if abs(total_dx) + abs(total_dy) < self.drag_threshold:
                return

            #threshold is exceeded → set is_dragging to True
            wds.is_dragging = True
            wds.last_total_dx = 0
            wds.last_total_dy = 0

        self.event_router.emit("widget.drag.apply_delta", dx=incremental_dx, dy=incremental_dy)

    def end_widget_drag(self):
        """end a widget drag by resetting widget drag state and notifying the Designer (to execute the MoveWidgetsTo command)"""
        wds = self._widget_drag_state

        wds.drag_start_coords = None
        wds.is_dragging = False

        try:
            self.canvas.grab_release()
        except Exception:
            pass

        #notify Designer that drag gesture ends (executes the MoveWidgetsTo command)
        self.event_router.emit("widget.drag.commit")

    def start_rectangle_selection(self, event):
        """begin a rectangle selection gesture"""
        rss = self._rectangle_selection_state

        canvas_x, canvas_y = self.pointer_in_canvas_coords(event)
        is_additive = bool(event.state & self.ctrl_key)

        #update rectangle selection state
        rss.is_dragging = False
        rss.is_additive = is_additive
        rss.drag_start_coords = (canvas_x, canvas_y)

        #let view render the selection rectangle
        self.selection_view.draw_selection_rectangle(canvas_x, canvas_y)

    def update_rectangle_selection(self, event):
        """update the selection rectangle (UI element) while dragging"""
        rss = self._rectangle_selection_state
        if not rss.drag_start_coords:
            return

        #set is_dragging flag
        rss.is_dragging = True

        #get rectangle coords (start coords + current pointer)
        x0, y0 = rss.drag_start_coords
        x1, y1 = self.pointer_in_canvas_coords(event)

        #let view update the selection rectangle
        self.selection_view.update_selection_rectangle(x0, y0, x1, y1)

    def end_rectangle_selection(self, event):
        """end a rectangle selection gesture"""
        rss = self._rectangle_selection_state
        if not rss.drag_start_coords:
            return

        #get rectangle coords (start coords + current pointer) and normalize corners
        x0, y0 = rss.drag_start_coords
        x1, y1 = self.pointer_in_canvas_coords(event)
        x0n, x1n = sorted((x0, x1))
        y0n, y1n = sorted((y0, y1))

        #find all enclosed widgets and filter out anything that isn't a window (widget)
        enclosed_widget_ids = [
            widget_id for widget_id in self.canvas.find_enclosed(x0n, y0n, x1n, y1n)
            if self.canvas.type(widget_id) == "window"
        ]

        #convert canvas item IDs (int) to model IDs (str)
        enclosed_model_ids = [
            self.resolve_widget_to_model(widget_id)
            for widget_id in enclosed_widget_ids
        ]

        #update selection
        if not rss.is_dragging:
            #not dragging → behave like a click
            model_id = self.model_id_at(x1, y1)
            if model_id is None:
                self.app_state.selection_clear()
            else:
                self.app_state.selection_handle_click(model_id, rss.is_additive)
        else:
            #dragging → apply rectangle selection
            self.app_state.apply_rectangle_selection(enclosed_model_ids, rss.is_additive)

            #reset rectangle selection state
            rss.drag_start_coords = None
            rss.is_dragging = False
            rss.is_additive = False

        #remove selection rectangle
        self.selection_view.clear_selection_rectangle()

    #Helpers------------------------------------------------------------------------------------------------------------
    def pointer_in_canvas_coords(self, event) -> tuple[int, int]:
        """convert tk event coordinates to canvas coordinates"""
        return int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))

    def find_topmost_window_at(self, x: int, y: int) -> int | None:
        """return the topmost widget at the given coordinates"""
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):    #last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None

    def model_id_at(self, x: int, y: int) -> str | None:
        """return the model ID of the widget located at the given canvas coordinates"""
        widget_id = self.find_topmost_window_at(x, y)
        if widget_id is None:
            return None
        return self.resolve_widget_to_model(widget_id)
