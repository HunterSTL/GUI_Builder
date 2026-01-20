import tkinter as tk
from tkinter import simpledialog, messagebox
from DataModels import *
from ProjectDocument import ProjectDocument

class WidgetManager:
    def __init__(
            self,
            top: tk.Toplevel,
            canvas: tk.Canvas,
            project_document: ProjectDocument,
            selection_manager,
            attributes_panel_callback,
            group_clamped_delta_callback,
            clamped_delta_callback,
            set_dirty_callback,
            panel_update=None
        ):
        self.top = top
        self.canvas = canvas
        self.project_document = project_document
        self.selection_manager = selection_manager
        self.attributes_panel_callback = attributes_panel_callback
        self.group_clamped_delta_callback = group_clamped_delta_callback
        self.clamped_delta_callback = clamped_delta_callback
        self.set_dirty_callback = set_dirty_callback
        self.panel_update = panel_update
        self.widget_map = {}

    #create widget and model based on type
    def add_widget(self, widget_type: str, x: int, y: int):
        if widget_type == "label":
            text = simpledialog.askstring("Label text", "Enter label text:", parent=self.top)
            if text is None:
                return
            bg = self.project_document.theme["label"]["bg"]
            fg = self.project_document.theme["label"]["fg"]
            widget = tk.Label(
                self.canvas,
                text=text,
                bg=bg,
                fg=fg
            )
            model = LabelWidgetData(x=x, y=y, bg=bg, fg=fg, text=text)
        elif widget_type == "entry":
            bg = self.project_document.theme["entry"]["bg"]
            fg = self.project_document.theme["entry"]["fg"]
            widget = tk.Entry(
                self.canvas,
                bg=bg,
                fg=fg
            )
            model = EntryWidgetData(x=x, y=y, bg=bg, fg=fg)
        elif widget_type == "button":
            text = simpledialog.askstring("Button text", "Enter button text:", parent=self.top)
            if text is None:
                return
            bg = self.project_document.theme["button"]["bg"]
            fg = self.project_document.theme["button"]["fg"]
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

        #calculate clamped x and y to prevent the widget from being created (partially) outside the canvas
        widget.update_idletasks()
        required_width, required_height = widget.winfo_reqwidth(), widget.winfo_reqheight()
        min_x, max_x = self._allowed_x_range(required_width, model.anchor)
        min_y, max_y = self._allowed_y_range(required_height, model.anchor)
        clamped_x = self._clamp(x, min_x, max_x)
        clamped_y = self._clamp(y, min_y, max_y)

        #insert widget into canvas
        window_id = self.canvas.create_window(clamped_x, clamped_y, window=widget, anchor=model.anchor)

        #populate model width and height after creating window and updating widget, otherwise both values are 1
        widget.update()
        model.width, model.height = widget.winfo_width(), widget.winfo_height()
        model.x, model.y = clamped_x, clamped_y

        #store both the data model and the tkinter widget in the widget map with the window_id as the key
        self.widget_map[window_id] = {"model": model, "widget": widget}
        #also append the new model to the project_document
        self.project_document.widget_models.append(model)

        #bind events
        self._bind_widget_events(widget, window_id)

        #set focus back to canvas
        self.canvas.focus_set()

        #set app state to dirty
        self.set_dirty_callback()
        return window_id

    #create widget from model
    def add_widget_from_model(self, model):
        model_type = getattr(model, "type", "").lower()
        if model_type == "label":
            widget = tk.Label(self.canvas, text=model.text, bg=model.bg, fg=model.fg)
        elif model_type == "entry":
            widget = tk.Entry(self.canvas, bg=model.bg, fg=model.fg)
        elif model_type == "button":
            widget = tk.Button(self.canvas, text=model.text, bg=model.bg, fg=model.fg)
        else:
            return None

        #insert widget into canvas
        window_id = self.canvas.create_window(model.x, model.y, window=widget, anchor=model.anchor)

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

    #snap selected widgets to grid
    def snap_to_grid(self):
        grid_size = self.project_document.grid.size
        for item_id in self.selection_manager.selected_ids():
            model = self.widget_map.get(item_id)["model"]
            new_x, new_y = round(model.x / grid_size) * grid_size, round(model.y / grid_size) * grid_size
            dx, dy = new_x - model.x, new_y - model.y
            self.canvas.move(item_id, dx, dy)           #move widget in canvas
            model.x, model.y = new_x, new_y             #update model data
            self.selection_manager.refresh(item_id)     #update highlight

        #set app state to dirty
        self.set_dirty_callback()

    #align selected widgets based on last selected widget
    def align(self, direction: str):
        def _bbox(_item_id):
            bbox = self.canvas.bbox(_item_id)
            x1, y1, x2, y2 = bbox
            return {
                "left": x1,
                "top": y1,
                "right": x2,
                "bottom": y2
            }

        selected_widgets = self.selection_manager.selected_ids()
        last_selected_widget = self.selection_manager.last_selected_id()
        if last_selected_widget is None:
            return

        reference_model_bbox = _bbox(last_selected_widget)

        for item_id in selected_widgets:
            if not item_id == last_selected_widget:
                model = self.widget_map.get(item_id)["model"]
                model_bbox = _bbox(item_id)
                if direction == "left":
                    dx, dy = reference_model_bbox["left"] - model_bbox["left"], 0
                elif direction == "right":
                    dx, dy = reference_model_bbox["right"] - model_bbox["right"], 0
                elif direction == "top":
                    dx, dy = 0, reference_model_bbox["top"] - model_bbox["top"]
                elif direction == "bottom":
                    dx, dy = 0, reference_model_bbox["bottom"] - model_bbox["bottom"]
                else:
                    dx, dy = 0, 0

                #clamp to canvas bounds
                if callable(self.clamped_delta_callback):
                    dx, dy = self.clamped_delta_callback(item_id, dx, dy)

                #move widget and update model
                self.canvas.move(item_id, dx, dy)
                model.x += dx
                model.y += dy
                self.selection_manager.refresh(item_id) #update highlight

        #set app state to dirty
        self.set_dirty_callback()

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
            self.canvas.delete(item_id)                             #delete widget from canvas
            model = self.widget_map.get(item_id)["model"]
            try:
                self.project_document.widget_models.remove(model)   #delete model from project_document
            except ValueError:
                pass    #model not in project_document
            self.widget_map.pop(item_id, None)                      #delete model from widget map

        #clear selection
        self.selection_manager.clear()

        #hide attributes panel
        self.attributes_panel_callback()

        #set focus back to canvas
        self.canvas.focus_set()

        #set app state to dirty
        self.set_dirty_callback()

    #apply an attribute change from the AttributesPanel to the widget
    def update_widget_attribute(self, item_id, attribute, value):
        model = self.widget_map.get(item_id)["model"]
        widget = self.widget_map.get(item_id)["widget"]
        if not widget:
            return

        if attribute in ("x", "y"):
            if attribute == "x":
                x, y = value, model.y
            elif attribute == "y":
                x, y = model.x, value
            else:
                return
            self.canvas.coords(item_id, x, y)
            self.selection_manager.refresh(item_id) #update selection outline
        elif attribute in ("width", "height"):
            self.canvas.itemconfig(item_id, **{attribute: value})
            widget.update()
            model.width, model.height = widget.winfo_width(), widget.winfo_height()
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
            self.selection_manager.refresh(item_id)
        else:
            return

    def _bind_widget_events(self, widget, window_id):
        def _on_click(e, i=window_id):
            #start drag
            self.selection_manager.start_widget_drag(e)

            #handle widget click (toggle or select_only based on CTRL-Key)
            result = self.selection_manager.handle_widget_click(e, i)

            #show attributes panel
            self.attributes_panel_callback()
            return result

        widget.bind("<Button-1>", _on_click)

        #move widgets based on mouse movement
        widget.bind("<B1-Motion>", lambda e: self.selection_manager.handle_widget_drag(e, self.widget_map, self.group_clamped_delta_callback, self.panel_update))

        #reset drag state
        widget.bind("<ButtonRelease-1>", lambda e: self.selection_manager.end_widget_drag())

        #keep outlines in sync when widget resizes
        widget.bind("<Configure>", lambda e, i=window_id: self.selection_manager and self.selection_manager.refresh(i))

    def _allowed_x_range(self, width, anchor):
        canvas_width = int(self.canvas.winfo_width())
        if anchor in ["sw", "w", "nw"]:
            return 0, canvas_width - width
        elif anchor in ["ne", "e", "se"]:
            return width, canvas_width
        elif anchor in ["n", "s", "center"]:
            return width // 2, canvas_width - (width // 2)

    def _allowed_y_range(self, height, anchor):
        canvas_height = int(self.canvas.winfo_height())
        if anchor in ["sw", "s", "se"]:
            return height, canvas_height
        elif anchor in ["nw", "n", "ne"]:
            return 0, canvas_height - height
        elif anchor in ["w", "e", "center"]:
            return height // 2, canvas_height - (height // 2)

    @staticmethod
    def _clamp(value, minimum, maximum):
        return max(minimum, min(maximum, value))