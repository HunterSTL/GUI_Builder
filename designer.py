import tkinter as tk
from tkinter import simpledialog
from typing import Dict, Optional
from selection import SelectionManager
from models import (GUIWindow, BaseWidgetData, LabelWidgetData, EntryWidgetData, ButtonWidgetData)
from theme import SELECTION_COLOR, SELECTION_WIDTH, SELECTION_DASH, NUDGE_SMALL, NUDGE_BIG

class Designer:
    def __init__(self, parent: tk.Tk, title: str, width: int, height: int, colors: dict):
        self.parent = parent
        self.colors = colors

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry(f"{width}x{height}")

        self.canvas = tk.Canvas(self.top, bg=self.colors["background"]["bg"])
        self.canvas.pack(fill="both", expand=True)

        self.gui_window = GUIWindow(title, width, height, self.colors["background"]["bg"])
        self.selection = SelectionManager(self.canvas)
        self.widget_map: Dict[int, BaseWidgetData] = {}

        #last right-click position for insertion
        self.click_x: Optional[int] = None
        self.click_y: Optional[int] = None

        #rectangle selection
        self._rectangle_selection_id:  Optional[int] = None
        self._rectangle_selection_start: Optional[tuple[int, int]] = None
        self._rectangle_selection_dragging: bool = False
        self._rectangle_selection_additive: bool = False

        #drag state
        self._drag_start_root: Optional[tuple[int, int]] = None
        self._drag_last_root: Optional[tuple[int, int]] = None
        self._dragging_widgets: bool = False
        self._drag_threshold: int = 3

        self._wire_context_menu()
        self._wire_canvas_events()

    #create context menu
    def _wire_context_menu(self):
        self.menu = tk.Menu(self.top, tearoff=0)
        self.menu.add_command(label="Add Label", command=self.add_label)
        self.menu.add_command(label="Add Entry", command=self.add_entry)
        self.menu.add_command(label="Add Button", command=self.add_button)

    #post context menu
    def _show_menu(self, event):
        self.click_x, self.click_y = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #bind events to functions
    def _wire_canvas_events(self):
        #context menu
        self.canvas.bind("<Button-3>", self._show_menu)

        #rectangle selection
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        #binds to move selected widgets
        self.canvas.focus_set()
        self.top.bind("<Left>", lambda e: self._move_selection(-NUDGE_SMALL, 0))
        self.top.bind("<Right>", lambda e: self._move_selection(NUDGE_SMALL, 0))
        self.top.bind("<Up>", lambda e: self._move_selection(0, -NUDGE_SMALL))
        self.top.bind("<Down>", lambda e: self._move_selection(0, NUDGE_SMALL))
        self.top.bind("<Shift-Left>", lambda e: self._move_selection(-NUDGE_BIG, 0))
        self.top.bind("<Shift-Right>", lambda e: self._move_selection(NUDGE_BIG, 0))
        self.top.bind("<Shift-Up>", lambda e: self._move_selection(0, -NUDGE_BIG))
        self.top.bind("<Shift-Down>", lambda e: self._move_selection(0, NUDGE_BIG))

    #create selection rectangle
    def _on_canvas_press(self, event):
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
    def _on_canvas_drag(self, event):
        if not self._rectangle_selection_start:
            return
        self._rectangle_selection_dragging = True
        x0, y0 = self._rectangle_selection_start
        x1, y1 = event.x, event.y

        #update rectangle
        if self._rectangle_selection_id is not None:
            self.canvas.coords(self._rectangle_selection_id, x0, y0, x1, y1)
            self.canvas.tag_raise(self._rectangle_selection_id)

    #select all widgets that are fully enclosed in the selection rectangle
    def _on_canvas_release(self, event):
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
                if item_id is None and self.selection:
                    self.selection.clear()
                    self._sync_selected_widgets()
                else:
                    if self.selection:
                        if self._rectangle_selection_additive:
                            self.selection.toggle(item_id)
                        else:
                            self.selection.select_only(item_id)
                        self._sync_selected_widgets()
            #when dragging is true → select all items fully enclosed by rectangle selection
            else:
                enclosed_widgets = self.canvas.find_enclosed(x0n, y0n, x1n, y1n)
                #filter out everything that's not a window item
                enclosed_windows = [i for i in enclosed_widgets if self.canvas.type(i) == "window"]

                if self.selection:
                    if self._rectangle_selection_additive:
                        for window_id in enclosed_windows:
                            if window_id not in self.selection.selected_ids():
                                self.selection.toggle(window_id)    #only toggle widgets that are not yet selected
                    else:
                        self.selection.clear()
                        for window_id in enclosed_windows:
                            self.selection.toggle(window_id)
        finally:
            #remove rectangle selection
            if self._rectangle_selection_id is not None:
                self.canvas.delete(self._rectangle_selection_id)
                self._rectangle_selection_id = None
            self._rectangle_selection_dragging = False
            self._rectangle_selection_additive = False

    #add new label
    def add_label(self):
        text = simpledialog.askstring("Label Text", "Enter label text:", parent=self.top)
        if text is None:
            return
        widget = tk.Label(
            self.canvas,
            text=text,
            bg=self.colors["label"]["bg"],
            fg=self.colors["label"]["fg"]
        )
        self._create_window_for_widget(widget, LabelWidgetData(text=text))

    #add new entry
    def add_entry(self):
        widget = tk.Entry(
            self.canvas,
            bg=self.colors["entry"]["bg"],
            fg=self.colors["entry"]["fg"]
        )
        self._create_window_for_widget(widget, EntryWidgetData())

    #add new button
    def add_button(self):
        text = simpledialog.askstring("Button Text", "Enter button text:", parent=self.top)
        if text is None:
            return
        widget = tk.Button(
            self.canvas,
            text=text,
            bg=self.colors["button"]["bg"],
            fg=self.colors["button"]["fg"]
        )
        self._create_window_for_widget(widget, ButtonWidgetData(text=text))

    #create window for widget
    def _create_window_for_widget(self, widget: tk.Widget, model: BaseWidgetData):
        x = self.click_x if self.click_x is not None else 20
        y = self.click_y if self.click_y is not None else 40

        model.x, model.y = x, y
        model.create_id()
        self.gui_window.add_widget(model)

        window_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)
        self.widget_map[window_id] = model

        #selection bindings for the widget itself
        widget.bind("<ButtonPress-1>", lambda e, i=window_id: self._on_widget_press(e, i))
        widget.bind("<B1-Motion>", lambda e, i=window_id: self._on_widget_drag(e, i))
        widget.bind("<ButtonRelease-1>", lambda e, i=window_id: self._on_widget_release(e, i))
        widget.bind("<Control-Button-1>", lambda e, i=window_id: self._on_widget_ctrl_left_click(e, i))
        widget.bind("<Configure>", lambda e, i=window_id: self.selection and self.selection.refresh(i))

    #select widget
    def _on_widget_press(self, event, item_id: int):
        if self.selection:
            if bool(event.state & 0x0004):
                self.selection.toggle(item_id)
                self._sync_selected_widgets()
            else:
                if item_id not in self.selection.selected_ids():
                    self.selection.select_only(item_id)
                    self._sync_selected_widgets()

        #record screen coordinates
        self._drag_start_root = (event.x_root, event.y_root)
        self._drag_last_root = (event.x_root, event.y_root)
        self._dragging_widgets = False
        return "break"  #prevent canvas from clearing selection

    #move widgets based on mouse movement
    def _on_widget_drag(self, event, item_id):
        if not self._drag_start_root:
            return "break"

        dx, dy = event.x_root - self._drag_last_root[0], event.y_root - self._drag_last_root[1]
        dx, dy = self._group_clamped_delta(dx, dy)

        if not self._dragging_widgets:
            total_dx = event.x_root - self._drag_start_root[0]
            total_dy = event.y_root - self._drag_start_root[1]
            if abs(total_dx) + abs(total_dy) < self._drag_threshold:
                return "break"
            self._dragging_widgets = True

        for item_id in self.selection.selected_ids():
            self.canvas.move(item_id, dx, dy)
            model = self.widget_map.get(item_id)
            if model:
                model.x += dx
                model.y += dy
            self.selection.refresh(item_id)

        self._drag_last_root = (event.x_root, event.y_root)
        return "break"

    #reset drag state after dragging
    def _on_widget_release(self, event, item_it: int):
        self._drag_start_root = None
        self._drag_last_root = None
        self._dragging_widgets = False
        return "break"

    #add widget to selection
    def _on_widget_ctrl_left_click(self, event, item_id: int):
        if self.selection:
            self.selection.toggle(item_id)
            self._sync_selected_widgets()
        return "break"

    #move selected widgets
    def _move_selection(self, dx, dy):
        if not self.selection:
            return
        dx, dy = self._group_clamped_delta(dx, dy)
        for item_id in self.selection.selected_ids():
            #move widget in canvas
            self.canvas.move(item_id, dx, dy)

            #update model data
            widget = self.widget_map.get(item_id)
            if widget:
                widget.x += dx
                widget.y += dy

            #update highlight
            self.selection.refresh(item_id)

    #compute clamped delta, so that widget cannot be moved outside the GUI window
    def _group_clamped_delta(self, dx: int, dy: int) -> tuple[int, int]:
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx_clamped, dy_clamped = dx, dy

        for item_id in self.selection.selected_ids():
            bbox = self.canvas.bbox(item_id)
            if not bbox:
                continue
            x0, y0, x1, y1 = bbox
            min_dx = -x0
            max_dx = canvas_width - x1
            min_dy = -y0
            max_dy = canvas_height - y1
            dx_clamped = max(min_dx, min(max_dx, dx_clamped))
            dy_clamped = max(min_dy, min(max_dy, dy_clamped))

        return dx_clamped, dy_clamped

    #update selected widgets in GUI window
    def _sync_selected_widgets(self):
        self.gui_window.selected_widgets = [
            self.widget_map[i] for i in self.selection.selected_ids() if i in self.widget_map
        ]

    #find clicked widget
    def _find_topmost_window_at(self, x: int, y: int) -> Optional[int]:
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):  #last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None