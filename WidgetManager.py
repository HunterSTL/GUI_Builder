import tkinter as tk
from ProjectDocument import ProjectDocument

class WidgetManager:
    def __init__(
            self,
            top: tk.Toplevel,
            canvas: tk.Canvas,
            project_document: ProjectDocument,
            selection_manager,
            callbacks: dict
        ):
        self.top = top
        self.canvas = canvas
        self.project_document = project_document
        self.selection_manager = selection_manager
        self.callbacks = callbacks
        self.widget_map = {}

    #create new widget
    def add_widget(self, model, widget, x: int, y: int):
        #insert widget into canvas
        widget_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)

        #store both the data model and the tkinter widget in the widget map with the widget_id as the key
        self.widget_map[widget_id] = {"model": model, "widget": widget}

        #bind events
        self._bind_widget_events(widget, widget_id)

        #set focus back to canvas
        self.canvas.focus_set()

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
        widget_id = self.canvas.create_window(model.x, model.y, window=widget, anchor=model.anchor)

        #populate model width and height after creating window and updating widget, otherwise both values are 1
        widget.update()
        model.width, model.height = widget.winfo_width(), widget.winfo_height()

        #store both the data model and the tkinter widget in the widget map with the widget_id as the key
        self.widget_map[widget_id] = {"model": model, "widget": widget}

        #bind events
        self._bind_widget_events(widget, widget_id)

        #set focus back to canvas
        self.canvas.focus_set()
        return widget_id

    #return model
    def get_model_from_widget_id(self, widget_id: int):
        return self.widget_map.get(widget_id)["model"]

    #return models x and y coordinates
    def get_model_coordinates_from_widget_id(self, widget_id: int):
        model = self.get_model_from_widget_id(widget_id)
        return model.x, model.y

    #return bounding box
    def get_bbox_from_widget_id(self, widget_id: int):
        bbox = self.canvas.bbox(widget_id)
        x1, y1, x2, y2 = bbox
        return {
            "left": x1,
            "top": y1,
            "right": x2,
            "bottom": y2
        }

    #move canvas item by delta, update model and refresh outline
    def move(self, widget_id: int, dx: int, dy: int):
        self.canvas.move(widget_id, dx, dy)
        model = self.get_model_from_widget_id(widget_id)
        model.x += dx; model.y += dy
        self.selection_manager.refresh(widget_id)

    #move canvas item to (x, y), update model and refresh outline
    def move_to(self, widget_id: int, x: int, y: int):
        self.canvas.coords(widget_id, x, y)
        model = self.get_model_from_widget_id(widget_id)
        model.x, model.y = x, y
        self.selection_manager.refresh(widget_id)

    #delete widget
    def delete(self, widget_id: int):
        self.canvas.delete(widget_id)           #delete canvas item
        self.widget_map.pop(widget_id, None)    #delete widget_id from widget_map
        self.canvas.focus_set()                 #set focus back to canvas

    #apply an attribute change from the AttributesPanel to the widget
    def update_widget_attribute(self, widget_id: int, attribute: str, value):
        model = self.get_model_from_widget_id(widget_id)
        widget = self.widget_map.get(widget_id)["widget"]
        if not widget:
            return

        if attribute in ("x", "y"):
            if attribute == "x":
                x, y = value, model.y
            elif attribute == "y":
                x, y = model.x, value
            else:
                return
            self.canvas.coords(widget_id, x, y)
            self.selection_manager.refresh(widget_id) #update selection outline
        elif attribute in ("width", "height"):
            self.canvas.itemconfig(widget_id, **{attribute: value})
            widget.update()
            model.width, model.height = widget.winfo_width(), widget.winfo_height()
            self.selection_manager.refresh(widget_id)
        elif attribute == "text":
            widget.config(text=value)
            widget.update()
            model.width, model.height = widget.winfo_width(), widget.winfo_height()
            self.selection_manager.refresh(widget_id)
        elif attribute in ("bg", "fg"):
            widget.config(**{attribute: value})
            widget.update()
            model.width, model.height = widget.winfo_width(), widget.winfo_height()
            self.selection_manager.refresh(widget_id)
        elif attribute == "anchor":
            try:
                self.canvas.itemconfig(widget_id, anchor=value)
            except Exception:
                widget.config(anchor=value)
            self.selection_manager.refresh(widget_id)
        else:
            return

    def _bind_widget_events(self, widget, widget_id: int):
        def _on_click(e, w_id=widget_id):
            #handle widget click (toggle or select_only based on CTRL-Key)
            result = self.selection_manager.handle_widget_click(e, w_id)

            #start drag
            self.selection_manager.start_widget_drag(e)

            #notify Designer that drag gesture starts
            self.callbacks["widget"]["begin_drag"]()

            #show attributes panel
            self.callbacks["attributes_panel"]()
            return result

        widget.bind("<Button-1>", _on_click)

        #move widgets based on mouse movement
        widget.bind("<B1-Motion>", lambda e: self.selection_manager.handle_widget_drag(e, self.callbacks["widget"]["move"]))

        #reset drag state
        widget.bind(
            "<ButtonRelease-1>",
            lambda e: (self.selection_manager.end_widget_drag(),    #reset drag state in SelectionManager
            self.callbacks["widget"]["end_drag"]())                 #notify Designer that drag gesture ends
        )

        #keep outlines in sync when widget resizes
        widget.bind(
            "<Configure>", lambda e, i=widget_id: (
                self.selection_manager
                and not self.selection_manager.is_dragging()
                and self.selection_manager.refresh(i)
            )
        )