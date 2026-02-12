import tkinter as tk
from AppState import AppState

class WidgetManager:
    def __init__(
            self,
            top: tk.Toplevel,
            canvas: tk.Canvas,
            app_state: AppState,
            selection_manager
        ):
        self.top = top
        self.canvas = canvas
        self.app_state = app_state
        self.selection_manager = selection_manager
        self.widget_map = {}

    #create new widget
    def add_widget(self, model, widget, x: int, y: int):
        #prevent widget from taking focus (redirect focus back to canvas)
        widget.bind("<FocusIn>", lambda e: self.canvas.focus_set())

        #insert widget into canvas
        widget_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor, tags="widget")

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

        #prevent widget from taking focus (redirect focus back to canvas)
        widget.bind("<FocusIn>", lambda e: self.canvas.focus_set())

        #insert widget into canvas
        widget_id = self.canvas.create_window(model.x, model.y, window=widget, anchor=model.anchor, tags="widget")

        #populate model width and height after creating window and updating widget, otherwise both values are 1
        widget.update()
        self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
        self.app_state.set_widget_attribute(model, "height", widget.winfo_height())

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
        self.app_state.move_widget_by(model, dx, dy)
        self.selection_manager.refresh(widget_id)

    #move canvas item to (x, y), update model and refresh outline
    def move_to(self, widget_id: int, x: int, y: int):
        self.canvas.coords(widget_id, x, y)
        model = self.get_model_from_widget_id(widget_id)
        self.app_state.move_widget_to(model, x, y)
        self.selection_manager.refresh(widget_id)

    #delete widget (canvas item), remove from widget_map and set focus back to canvas
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

        #validate attribute name
        attribute =attribute.strip().lower()
        allowed_attributes = {"x", "y", "width", "height", "text", "bg", "fg", "anchor"}
        if attribute not in allowed_attributes:
            return

        if attribute in ("x", "y"):
            if attribute == "x":
                x, y = value, model.y
            else:
                x, y = model.x, value
            self.canvas.coords(widget_id, x, y)
            self.app_state.set_widget_attribute(model, "x", x)
            self.app_state.set_widget_attribute(model, "y", y)
        elif attribute in ("width", "height"):
            self.canvas.itemconfig(widget_id, **{attribute: value})
            widget.update()
            self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
            self.app_state.set_widget_attribute(model, "height", widget.winfo_height())
        elif attribute == "text":
            widget.config(text=value)
            widget.update()
            self.app_state.set_widget_attribute(model, "text", value)
            self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
            self.app_state.set_widget_attribute(model, "height", widget.winfo_height())
        elif attribute in ("bg", "fg"):
            widget.config(**{attribute: value})
            self.app_state.set_widget_attribute(model, attribute, value)
        elif attribute == "anchor":
            try:
                self.canvas.itemconfig(widget_id, anchor=value)
            except Exception:
                widget.config(anchor=value)
            self.app_state.set_widget_attribute(model, "anchor", value)

        self.selection_manager.refresh(widget_id)

    def _bind_widget_events(self, widget, widget_id: int):
        def forward_to_canvas(event, sequence):
            canvas_x = event.x_root - self.canvas.winfo_rootx()
            canvas_y = event.y_root - self.canvas.winfo_rooty()

            self.canvas.event_generate(
                sequence,
                x=canvas_x,
                y=canvas_y,
                state=event.state
            )
            return "break"

        #keep outlines in sync when widget resizes
        widget.bind(
            "<Configure>", lambda e, i=widget_id: (
                self.selection_manager
                and not self.selection_manager.is_dragging()
                and self.selection_manager.refresh(i)
            )
        )

        #forward all mouse events from the widget to the canvas
        widget.bind("<ButtonPress-1>", lambda event: forward_to_canvas(event, "<ButtonPress-1>"))
        #widget.bind("<B1-Motion>", lambda event: forward_to_canvas(event, "<B1-Motion>"))
        widget.bind("<ButtonRelease-1>", lambda event: forward_to_canvas(event, "<ButtonRelease-1>"))