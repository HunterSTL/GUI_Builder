import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from events import EventRouter
from utility import Direction, Edge
from utility.Constants import CTRL_KEY_MASK, DRAG_THRESHOLD, NUDGE_SMALL, NUDGE_BIG

from AppState import AppState


@dataclass
class _MouseGesture:
    """Stores the state of an active mouse gesture."""
    press_coordinates: tuple[int, int]
    press_widget_id: str | None
    applied_delta: tuple[int, int]
    is_additive: bool
    is_dragging: bool


class CanvasController:
    """Translates canvas input into domain intent."""
    def __init__(
        self,
        canvas: tk.Canvas,
        event_router: EventRouter,
        app_state: AppState,
        resolve_canvas_item_id_to_widget_id: Callable[[int], str]
    ) -> None:
        self._canvas: tk.Canvas = canvas
        self._event_router: EventRouter = event_router
        self._app_state: AppState = app_state
        self._resolve_canvas_item_id_to_widget_id: Callable[[int], str] = resolve_canvas_item_id_to_widget_id

        self._active_mouse_gesture: _MouseGesture | None = None

        self._bind_events()

    def _handle_canvas_press(
        self,
        event: tk.Event
    ) -> None:
        """Record state for the mouse gesture interpretation."""
        canvas_x, canvas_y = self._pointer_in_canvas_coords(event)

        self._active_mouse_gesture = _MouseGesture(
            press_coordinates=(canvas_x, canvas_y),
            press_widget_id=self._widget_id_at(canvas_x, canvas_y),
            applied_delta=(0, 0),
            is_additive=bool(event.state & CTRL_KEY_MASK),
            is_dragging=False
        )

    def _handle_canvas_drag(
        self,
        event: tk.Event
    ) -> None:
        """Start the active mouse gesture when the drag threshold is first exceeded and update it on every drag event."""
        gesture = self._active_mouse_gesture
        if gesture is None:
            return

        canvas_x, canvas_y = self._pointer_in_canvas_coords(event)

        total_dx = canvas_x - gesture.press_coordinates[0]
        total_dy = canvas_y - gesture.press_coordinates[1]
        incremental_dx = total_dx - gesture.applied_delta[0]
        incremental_dy = total_dy - gesture.applied_delta[1]

        if not gesture.is_dragging:
            total_delta = abs(total_dx) + abs(total_dy)
            if total_delta < DRAG_THRESHOLD:
                return

            gesture.is_dragging = True
            gesture.applied_delta = 0, 0

            if gesture.press_widget_id is not None:
                if not self._app_state.selection_contains(gesture.press_widget_id):     #preserves the current selection when dragging an already selected widget
                    self._app_state.selection_handle_click(
                        widget_id=gesture.press_widget_id,
                        is_additive=gesture.is_additive
                    )
                self._event_router.emit("widget.drag.start")
            else:
                self._event_router.emit(
                    "selection.rectangle.start",
                    x1=gesture.press_coordinates[0],
                    y1=gesture.press_coordinates[1]
                )

        if gesture.press_widget_id is not None:
            self._event_router.emit(
                "widget.drag.update",
                dx=incremental_dx,
                dy=incremental_dy
            )
            gesture.applied_delta = total_dx, total_dy
        else:
            self._event_router.emit(
                "selection.rectangle.update",
                x1=gesture.press_coordinates[0],
                y1=gesture.press_coordinates[1],
                x2=canvas_x,
                y2=canvas_y
            )

    def _handle_canvas_release(
        self,
        event: tk.Event
    ) -> None:
        """Apply click selection if the drag threshold was not exceeded, otherwise end the active mouse gesture."""
        gesture = self._active_mouse_gesture
        if gesture is None:
            return

        try:
            if not gesture.is_dragging:
                if gesture.press_widget_id is not None:
                    self._app_state.selection_handle_click(
                        widget_id=gesture.press_widget_id,
                        is_additive=gesture.is_additive
                    )
                else:
                    self._app_state.selection_clear()
            else:
                if gesture.press_widget_id is not None:
                    self._event_router.emit("widget.drag.end")
                else:
                    canvas_x, canvas_y = self._pointer_in_canvas_coords(event)
                    self._select_enclosed_widgets(
                        x1=gesture.press_coordinates[0],
                        y1=gesture.press_coordinates[1],
                        x2=canvas_x,
                        y2=canvas_y,
                        is_additive=gesture.is_additive
                    )
                    self._event_router.emit("selection.rectangle.end")
        finally:
            self._active_mouse_gesture = None

    def _bind_events(
        self
    ) -> None:
        """Bind canvas input to the corresponding handlers and events."""
        #keep focus on canvas
        self._canvas.bind("<Enter>", lambda e: self._canvas.focus_set(), add="+")
        self._canvas.bind("<Button-1>", lambda e: self._canvas.focus_set(), add="+")

        #mouse events
        self._canvas.bind("<ButtonPress-1>", self._handle_canvas_press)
        self._canvas.bind("<B1-Motion>", self._handle_canvas_drag)
        self._canvas.bind("<ButtonRelease-1>", self._handle_canvas_release)
        self._canvas.bind("<Button-3>", lambda e: self._event_router.emit("menu.show", tk_event=e))

        #project events
        self._canvas.bind("<Control-n>", lambda e: self._event_router.emit("project.new"))
        self._canvas.bind("<Control-o>", lambda e: self._event_router.emit("project.open"))
        self._canvas.bind("<Control-s>", lambda e: self._event_router.emit("project.save"))
        self._canvas.bind("<Control-Shift-S>", lambda e: self._event_router.emit("project.save_as"))

        #app events
        self._canvas.bind("<Alt-F4>", lambda e: self._event_router.emit("app.exit"))

        #edit events
        self._canvas.bind("<Delete>", lambda e: self._event_router.emit("edit.delete"))
        self._canvas.bind("<Control-c>", lambda e: self._event_router.emit("edit.copy"))
        self._canvas.bind("<Control-v>", lambda e: self._event_router.emit("edit.paste"))
        self._canvas.bind("<Control-x>", lambda e: self._event_router.emit("edit.cut"))
        self._canvas.bind("<Control-z>", lambda e: self._event_router.emit("edit.undo"))
        self._canvas.bind("<Control-y>", lambda e: self._event_router.emit("edit.redo"))

        #widget events
        self._canvas.bind("<Left>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.LEFT, amount=NUDGE_SMALL))
        self._canvas.bind("<Right>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.RIGHT, amount=NUDGE_SMALL))
        self._canvas.bind("<Up>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.UP, amount=NUDGE_SMALL))
        self._canvas.bind("<Down>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.DOWN, amount=NUDGE_SMALL))
        self._canvas.bind("<Shift-Left>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.LEFT, amount=NUDGE_BIG))
        self._canvas.bind("<Shift-Right>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.RIGHT, amount=NUDGE_BIG))
        self._canvas.bind("<Shift-Up>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.UP, amount=NUDGE_BIG))
        self._canvas.bind("<Shift-Down>", lambda e: self._event_router.emit("widget.nudge", direction=Direction.DOWN, amount=NUDGE_BIG))
        self._canvas.bind("<Key-s>", lambda e: self._event_router.emit("widget.snap_to_grid"))
        self._canvas.bind("<Control-Left>", lambda e: self._event_router.emit("widget.align", edge=Edge.LEFT))
        self._canvas.bind("<Control-Right>", lambda e: self._event_router.emit("widget.align", edge=Edge.RIGHT))
        self._canvas.bind("<Control-Up>", lambda e: self._event_router.emit("widget.align", edge=Edge.TOP))
        self._canvas.bind("<Control-Down>", lambda e: self._event_router.emit("widget.align", edge=Edge.BOTTOM))
        self._canvas.bind("<Control-a>", lambda e: self._event_router.emit("widget.select_all"))

        #grid events
        self._canvas.bind("<Key-g>", lambda e: self._event_router.emit("grid.toggle"))
        self._canvas.bind("<Control-g>", lambda e: self._event_router.emit("grid.change_size"))
        self._canvas.bind("<Shift-G>", lambda e: self._event_router.emit("grid.change_color"))

        #debug events
        self._canvas.bind("<Control-Shift-T>", lambda e: self._event_router.emit("debug.toggle_call_tracing"))
        self._canvas.bind("<numbersign>", lambda e: self._event_router.emit("debug.print_widget_count"))
        self._canvas.bind("<F1>", lambda e: self._event_router.emit("debug.print_clipboard"))
        self._canvas.bind("<F2>", lambda e: self._event_router.emit("debug.print_command_stack"))
        self._canvas.bind("<F3>", lambda e: self._event_router.emit("debug.print_selection"))
        self._canvas.bind("<F4>", lambda e: self._event_router.emit("debug.print_bounding_boxes"))
        self._canvas.bind("<F5>", lambda e: self._event_router.emit("debug.print_id_counters"))

    def _pointer_in_canvas_coords(
        self,
        event: tk.Event
    ) -> tuple[int, int]:
        """Return the event position in canvas coordinates."""
        return int(self._canvas.canvasx(event.x)), int(self._canvas.canvasy(event.y))

    def _find_topmost_canvas_window_at(
        self,
        x: int,
        y: int
    ) -> int | None:
        """Return the topmost canvas window item at the given canvas coordinates."""
        canvas_item_ids = self._canvas.find_overlapping(x, y, x, y)
        for canvas_item_id in reversed(canvas_item_ids):    #last is top-most
            if self._canvas.type(canvas_item_id) == "window":
                return canvas_item_id
        return None

    def _widget_id_at(
        self,
        x: int,
        y: int
    ) -> str | None:
        """Return the widget ID of the widget located at the given canvas coordinates."""
        canvas_item_id = self._find_topmost_canvas_window_at(x, y)
        if canvas_item_id is None:
            return None
        return self._resolve_canvas_item_id_to_widget_id(canvas_item_id)

    def _select_enclosed_widgets(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        is_additive: bool
    ) -> None:
        """Apply additive or exclusive selection to the widgets enclosed by the given canvas coordinates."""
        #find all enclosed items and filter out anything that isn't a window (widget)
        enclosed_canvas_item_ids = [
            canvas_item_id for canvas_item_id in self._canvas.find_enclosed(x1, y1, x2, y2)
            if self._canvas.type(canvas_item_id) == "window"
        ]

        #convert canvas item IDs (int) to widget IDs (str)
        enclosed_widget_ids = [
            self._resolve_canvas_item_id_to_widget_id(canvas_item_id)
            for canvas_item_id in enclosed_canvas_item_ids
        ]

        self._app_state.apply_rectangle_selection(
            enclosed_widget_ids=enclosed_widget_ids,
            is_additive=is_additive
        )
