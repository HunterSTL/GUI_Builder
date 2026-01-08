import tkinter as tk
from tkinter import simpledialog, messagebox
from DataModels import *

class WidgetManager:
    def __init__(self, top, canvas, theme, selection_manager, sync_callback, clamped_delta, panel_update=None):
        self.top = top
        self.canvas = canvas
        self.theme = theme
        self.selection_manager = selection_manager
        self.sync_callback = sync_callback
        self.clamped_delta = clamped_delta
        self.panel_update = panel_update
        self.widget_map = {}

    def add_widget(self, widget_type: str, x: int, y: int):
        #create widget and model based on type
        if widget_type == "label":
            text = simpledialog.askstring("Label Text", "Enter label text:", parent=self.top)
            if text is None:
                return
            bg = self.theme["label"]["bg"]
            fg = self.theme["label"]["fg"]
            widget = tk.Label(
                self.canvas,
                text=text,
                bg=bg,
                fg=fg
            )
            model = LabelWidgetData(x=x, y=y, bg=bg, fg=fg, text=text)
        elif widget_type == "entry":
            bg = self.theme["entry"]["bg"]
            fg = self.theme["entry"]["fg"]
            widget = tk.Entry(
                self.canvas,
                bg=bg,
                fg=fg
            )
            model = EntryWidgetData(x=x, y=y, bg=bg, fg=fg)
        elif widget_type == "button":
            text = simpledialog.askstring("Button Text", "Enter button text:", parent=self.top)
            if text is None:
                return
            bg = self.theme["button"]["bg"]
            fg = self.theme["button"]["fg"]
            widget = tk.Button(
                self.canvas,
                text=text,
                bg=bg,
                fg=fg
            )
            model = ButtonWidgetData(x=x, y=y, bg=bg, fg=fg, text=text)
        else:
            return

        model.create_id()

        #insert widget into canvas
        window_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)

        #populate model width and height after creating window and updating widget, otherwise both values are 1
        widget.update()
        model.width, model.height = widget.winfo_width(), widget.winfo_height()

        #store both the data model and the tkinter widget in the widget map with the window_id as the key
        self.widget_map[window_id] = {"model": model, "widget": widget}

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
        widget.bind("<B1-Motion>", lambda e: self.selection_manager.handle_widget_drag(e, self.widget_map, self.clamped_delta, self.panel_update))

        #reset drag state
        widget.bind("<ButtonRelease-1>", lambda e: self.selection_manager.end_widget_drag())

        #keep outlines in sync when widget resizes
        widget.bind("<Configure>", lambda e, i=window_id: self.selection_manager and self.selection_manager.refresh(i))

    def snap_to_grid(self, grid_size: int):
        #snap selected widgets to grid
        for item_id in self.selection_manager.selected_ids():
            model = self.widget_map.get(item_id)["model"]
            new_x, new_y = round(model.x / grid_size) * grid_size, round(model.y / grid_size) * grid_size
            dx, dy = new_x - model.x, new_y - model.y
            self.canvas.move(item_id, dx, dy)           #move widget in canvas
            model.x, model.y = new_x, new_y             #update model data
            self.selection_manager.refresh(item_id)     #update highlight
        self.sync_callback()

    def align(self, direction: str):
        #align selected widgets based on last selected widget
        selected_widgets = self.selection_manager.selected_ids()
        last_selected_widget = self.selection_manager.last_selected_id()
        reference_model = self.widget_map.get(last_selected_widget)["model"]

        for item_id in selected_widgets:
            if not item_id == last_selected_widget:
                model = self.widget_map.get(item_id)["model"]
                if direction == "left":
                    dx = reference_model.x - model.x            #compute delta x
                    self.canvas.move(item_id, dx, 0)            #move widget in canvas
                    model.x += dx                               #update model data
                elif direction == "right":
                    dx = (reference_model.x + reference_model.width) - (model.x + model.width)
                    self.canvas.move(item_id, dx, 0)
                    model.x += dx
                elif direction == "top":
                    dy = (reference_model.y - reference_model.height) - (model.y - model.height)
                    self.canvas.move(item_id, 0, dy)
                    model.y += dy
                elif direction == "bottom":
                    dy = reference_model.y - model.y
                    self.canvas.move(item_id, 0, dy)
                    model.y += dy
                else:
                    return
                self.selection_manager.refresh(item_id) #update highlight
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

    def update_widget_attribute(self, item_id, attribute, value):
        #apply an attribute change from the AttributesPanel to the widget
        model = self.widget_map.get(item_id)["model"]
        widget = self.widget_map.get(item_id)["widget"]
        if not widget:
            return

        if attribute in ("x", "y"):
            x, y = model.x, model.y
            self.canvas.coords(item_id, x, y)
            self.canvas.update_idletasks()
            self.selection_manager.refresh(item_id) #update selection outline
        elif attribute in ("width", "height"):
            self.canvas.itemconfig(item_id, **{attribute: value})
            self.canvas.update_idletasks()
            self.selection_manager.refresh(item_id)
        elif attribute == "text":
            widget.config(text=value)
            widget.update()
            model.width, model.height = widget.winfo_width(), widget.winfo_height()
            self.selection_manager.refresh(item_id)
        elif attribute in ("bg", "fg"):
            widget.config(**{attribute: value})
            widget.update()
            model.width, model.height = widget.winfo_width(), widget.winfo_height()
            self.selection_manager.refresh(item_id)
        elif attribute == "anchor":
            try:
                self.canvas.itemconfig(item_id, anchor=value)
            except Exception:
                widget.config(anchor=value)
            self.canvas.update_idletasks()
            self.selection_manager.refresh(item_id)
        else:
            pass