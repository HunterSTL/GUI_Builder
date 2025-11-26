import tkinter as tk
from tkinter import simpledialog, messagebox
from DataModels import *

class WidgetManager:
    def __init__(self, top, canvas, theme, selection_manager, sync_callback, clamped_delta):
        self.top = top
        self.canvas = canvas
        self.theme = theme
        self.selection_manager = selection_manager
        self.sync_callback = sync_callback
        self.clamped_delta = clamped_delta
        self.widget_map = {}

    def add_widget(self, widget_type: str, x: int, y: int):
        #create widget and model based on type
        if widget_type == "label":
            text = simpledialog.askstring("Label Text", "Enter label text:", parent=self.top)
            if text is None:
                return
            widget = tk.Label(
                self.canvas,
                text=text,
                bg=self.theme["label"]["bg"],
                fg=self.theme["label"]["fg"]
            )
            model = LabelWidgetData(text=text)
        elif widget_type == "entry":
            widget = tk.Entry(
                self.canvas,
                bg=self.theme["entry"]["bg"],
                fg=self.theme["entry"]["fg"]
            )
            model = EntryWidgetData()
        elif widget_type == "button":
            text = simpledialog.askstring("Button Text", "Enter button text:", parent=self.top)
            if text is None:
                return
            widget = tk.Button(
                self.canvas,
                text=text,
                bg=self.theme["button"]["bg"],
                fg=self.theme["button"]["fg"]
            )
            model = ButtonWidgetData(text=text)
        else:
            return

        model.create_id()
        model.x, model.y = x, y

        #insert widget into canvas
        window_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)
        self.widget_map[window_id] = model

        #bind events
        self._bind_widget_events(widget, window_id)

        #set focus back to canvas
        self.canvas.focus_set()
        return window_id

    def _bind_widget_events(self, widget, window_id):
        def _on_click(e, i=window_id):
            #start drag
            self.selection_manager.start_widget_drag(e)
            #handle widget click (toggle or select_only based on CTRL-Key)
            result = self.selection_manager.handle_widget_click(e, i)
            self.sync_callback()
            return result

        widget.bind("<Button-1>", _on_click)

        #move widgets based on mouse movement
        widget.bind("<B1-Motion>", lambda e: self.selection_manager.handle_widget_drag(e, self.widget_map, self.clamped_delta))

        #reset drag state
        widget.bind("<ButtonRelease-1>", lambda e: self.selection_manager.end_widget_drag())

        #keep outlines in sync when widget resizes
        widget.bind("<Configure>", lambda e, i=window_id: self.selection_manager and self.selection_manager.refresh(i))

    #snap selected widgets to grid
    def snap_to_grid(self, grid_size: int):
        for item_id in self.selection_manager.selected_ids():
            model = self.widget_map.get(item_id)
            new_x, new_y = round(model.x / grid_size) * grid_size, round(model.y / grid_size) * grid_size
            dx, dy = new_x - model.x, new_y - model.y

            #move widget in canvas
            self.canvas.move(item_id, dx, dy)

            #update model data
            model.x, model.y = new_x, new_y

            #update highlight
            self.selection_manager.refresh(item_id)
        self.sync_callback()

    def delete_selected_widgets(self):
        count_selected_widgets = len(self.selection_manager.selected_ids())
        if count_selected_widgets == 0:
            return
        elif count_selected_widgets == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count_selected_widgets)} selected widgets?"

        if not messagebox.askyesno("Delete", messagebox_text):
            return

        for item_id in [i for i in self.selection_manager.selected_ids() if self.canvas.type(i) == "window"]:
            #delete widget
            self.canvas.delete(item_id)
            #delete model
            self.widget_map.pop(item_id, None)
            #clear selection
        self.selection_manager.clear()
        self.sync_callback()