import tkinter as tk
from tkinter import simpledialog
from typing import Dict, Optional
from selection import SelectionManager
from models import (GUIWindow, BaseWidgetData, LabelWidgetData, EntryWidgetData, ButtonWidgetData)

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

        self._wire_context_menu()
        self._wire_canvas_events()

    #context menu
    def _wire_context_menu(self):
        self.menu = tk.Menu(self.top, tearoff=0)
        self.menu.add_command(label="Add Label", command=self.add_label)
        self.menu.add_command(label="Add Entry", command=self.add_entry)
        self.menu.add_command(label="Add Button", command=self.add_button)

    def _show_menu(self, event):
        self.click_x, self.click_y = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #canvas events
    def _wire_canvas_events(self):
        self.canvas.bind("<Button-3>", self._show_menu)                             #right-click
        self.canvas.bind("<Button-1>", self._on_canvas_left_click)                  #clear selection
        self.canvas.bind("<Control-Button-1>", self._on_canvas_ctrl_left_click)     #no-op

        #binds to move selected widgets
        self.canvas.focus_set()
        small_step, big_step = 1, 10
        self.top.bind_all("<Left>", lambda e: self._move_selection(-small_step, 0))
        self.top.bind_all("<Right>", lambda e: self._move_selection(small_step, 0))
        self.top.bind_all("<Up>", lambda e: self._move_selection(0, -small_step))
        self.top.bind_all("<Down>", lambda e: self._move_selection(0, small_step))
        self.top.bind_all("<Shift-Left>", lambda e: self._move_selection(-big_step, 0))
        self.top.bind_all("<Shift-Right>", lambda e: self._move_selection(big_step, 0))
        self.top.bind_all("<Shift-Up>", lambda e: self._move_selection(0, -big_step))
        self.top.bind_all("<Shift-Down>", lambda e: self._move_selection(0, big_step))

    def _on_canvas_left_click(self, event):
        item_id = self._find_topmost_window_at(event.x, event.y)
        if item_id is None and self.selection:
            self.selection.clear()
            self._sync_selected_widgets()

    def _on_canvas_ctrl_left_click(self, event):
        #keep existing selection; Ctrl+click empty canvas is a no-op
        pass

    #adders
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

    def add_entry(self):
        widget = tk.Entry(
            self.canvas,
            bg=self.colors["entry"]["bg"],
            fg=self.colors["entry"]["fg"]
        )
        self._create_window_for_widget(widget, EntryWidgetData())

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

    #plumbing
    def _create_window_for_widget(self, widget: tk.Widget, model: BaseWidgetData):
        x = self.click_x if self.click_x is not None else 20
        y = self.click_y if self.click_y is not None else 40

        model.x, model.y = x, y
        model.create_id()
        self.gui_window.add_widget(model)

        window_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)
        self.widget_map[window_id] = model

        #selection bindings for the widget itself
        widget.bind("<Button-1>", lambda e, i=window_id: self._on_widget_left_click(e, i))
        widget.bind("<Control-Button-1>", lambda e, i=window_id: self._on_widget_ctrl_left_click(e, i))
        widget.bind("<Configure>", lambda e, i=window_id: self.selection and self.selection.refresh(i))

    def _on_widget_left_click(self, event, item_id: int):
        if self.selection:
            self.selection.select_only(item_id)
            self._sync_selected_widgets()
        return "break"  #prevent canvas from clearing selection

    def _on_widget_ctrl_left_click(self, event, item_id: int):
        if self.selection:
            self.selection.toggle(item_id)
            self._sync_selected_widgets()
        return "break"

    def _move_selection(self, dx, dy):
        if not self.selection:
            return
        for item_id in self.selection.selected_ids():
            #move widget in canvas
            self.canvas.move(item_id, dx, dy)

            #update model data
            widget = self.widget_map[item_id]
            if widget:
                widget.x += dx
                widget.y += dy

            #update highlight
            self.selection.refresh(item_id)

    def _sync_selected_widgets(self):
        self.gui_window.selected_widgets = [
            self.widget_map[i] for i in self.selection.selected_ids() if i in self.widget_map
        ]

    #helpers
    def _find_topmost_window_at(self, x: int, y: int) -> Optional[int]:
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):  # last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None