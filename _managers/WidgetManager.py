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
        """initialize the widget manager and its widget/model mappings"""
        self.top = top
        self.canvas = canvas
        self.app_state = app_state
        self.selection_manager = selection_manager
        self.widget_map = {}
        self.model_id_to_widget_id: dict[str, int] = {}
        self.widget_id_to_model_id: dict[int, str] = {}

    def render_full(self):
        """fully rebuild all widgets from the project models"""
        #clear all canvas items except grid lines
        for widget_id in list(self.widget_map.keys()):
            self.canvas.delete(widget_id)
        self.widget_map.clear()

        #rebuild widgets from models
        for model in self.app_state.project.widget_models:
            self._render_widget(model)

    def render_soft(self, model):
        """update an existing widget’s position, attributes, and outline"""
        #get the widget_id of this model
        widget_id = self.get_widget_id_from_model_id(model.id)

        if widget_id is None:
            #widget does not exist yet → render it fully
            self._render_widget(model)
            return

        #update widget position
        self.canvas.coords(widget_id, model.x, model.y)

        #update widget attributes (text, color)
        widget = self.widget_map[widget_id]["widget"]
        widget.config(text=getattr(model, "text", widget.cget("text")), bg=model.bg, fg=model.fg)

        #update size if width/height in model
        if model.width and model.height:
            self.canvas.itemconfig(widget_id, width=model.width, height=model.height)

        #refresh outline
        self.selection_manager.refresh(model.id)

    def _render_widget(self, model):
        """create and insert a Tk widget for a model"""
        #create the correct Tk widget
        if model.type == "Label":
            widget = tk.Label(self.canvas, text=model.text, bg=model.bg, fg=model.fg)
        elif model.type == "Entry":
            widget = tk.Entry(self.canvas, bg=model.bg, fg=model.fg)
        elif model.type == "Button":
            widget = tk.Button(self.canvas, text=model.text, bg=model.bg, fg=model.fg)
        else:
            return None

        #insert widget into canvas
        widget_id = self.canvas.create_window(
            model.x, model.y,
            window=widget,
            anchor=model.anchor,
            tags="widget"
        )

        #insert widget into widget_map
        self.widget_map[widget_id] = {"model": model, "widget": widget}

        #store widget and model id in mapping
        self.widget_id_to_model_id[widget_id] = model.id
        self.model_id_to_widget_id[model.id] = widget_id

        #bind widget events (forward to canvas, configure handling)
        self._bind_widget_events(widget, model.id)

        return widget_id

    def add_widget(self, model, widget, x: int, y: int):
        """create a new widget instance and add it to the canvas"""
        #prevent widget from taking focus (redirect focus back to canvas)
        widget.bind("<FocusIn>", lambda e: self.canvas.focus_set())

        #insert widget into canvas
        widget_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor, tags="widget")

        #store both the data model and the tkinter widget in the widget map with the widget_id as the key
        self.widget_map[widget_id] = {"model": model, "widget": widget}

        #store widget and model id in mapping
        self.widget_id_to_model_id[widget_id] = model.id
        self.model_id_to_widget_id[model.id] = widget_id

        #bind events
        self._bind_widget_events(widget, model.id)

        #set focus back to canvas
        self.canvas.focus_set()

    def add_widget_from_model(self, model):
        """create a widget from a model, compute width/height, and register mappings"""
        if model.type == "Label":
            widget = tk.Label(self.canvas, text=model.text, bg=model.bg, fg=model.fg)
        elif model.type == "Entry":
            widget = tk.Entry(self.canvas, bg=model.bg, fg=model.fg)
        elif model.type == "Button":
            widget = tk.Button(self.canvas, text=model.text, bg=model.bg, fg=model.fg)
        else:
            return None

        #prevent widget from taking focus (redirect focus back to canvas)
        widget.bind("<FocusIn>", lambda e: self.canvas.focus_set())

        #insert widget into canvas
        widget_id = self.canvas.create_window(model.x, model.y, window=widget, anchor=model.anchor, tags="widget")

        #batch app state changes so _on_changed_state gets called only once (instead of per change)
        with self.app_state.batch():
            #populate model width and height after creating window and updating widget, otherwise both values are 1
            widget.update()
            self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
            self.app_state.set_widget_attribute(model, "height", widget.winfo_height())

        #store both the data model and the tkinter widget in the widget map with the widget_id as the key
        self.widget_map[widget_id] = {"model": model, "widget": widget}

        #store widget and model id in mapping
        self.widget_id_to_model_id[widget_id] = model.id
        self.model_id_to_widget_id[model.id] = widget_id

        #bind events
        self._bind_widget_events(widget, model.id)

        #set focus back to canvas
        self.canvas.focus_set()
        return widget_id

    def get_model_from_model_id(self, model_id: str):
        """return the model associated with a given model_id"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        return self.widget_map.get(widget_id)["model"]

    def get_model_id_from_widget_id(self, widget_id: int):
        """return the model_id mapped to a widget_id"""
        return self.widget_id_to_model_id.get(widget_id)

    def get_widget_id_from_model_id(self, model_id: str):
        """return the widget_id mapped to a model_id"""
        return self.model_id_to_widget_id.get(model_id)

    def get_model_coordinates_from_model_id(self, model_id: str):
        """return the x,y coordinates of the model"""
        model = self.get_model_from_model_id(model_id)
        return model.x, model.y

    def get_bbox_from_model_id(self, model_id: str):
        """return the bounding box of the widget"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        bbox = self.canvas.bbox(widget_id)

        if not bbox:
            return None

        x1, y1, x2, y2 = bbox
        return {
            "left": x1,
            "top": y1,
            "right": x2,
            "bottom": y2
        }

    def delete(self, model_id: str):
        """delete a widget and remove from all mappings"""
        #remove widget_id from model id <> widget id mapping
        widget_id = self.model_id_to_widget_id.pop(model_id, None)
        if widget_id:
            self.widget_id_to_model_id.pop(widget_id, None)

        self.widget_map.pop(widget_id, None)    #delete widget_id from widget_map
        self.canvas.delete(widget_id)           #delete canvas item
        self.canvas.focus_set()                 #set focus back to canvas

    def update_widget_attribute(self, model_id: str, attribute: str, value):
        """apply an attribute change from the AttributesPanel to a widget and propagate through AppState"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        widget = self.widget_map.get(widget_id)["widget"]
        if not widget:
            return

        #validate attribute name
        attribute = attribute.strip().lower()
        allowed_attributes = {"x", "y", "width", "height", "text", "bg", "fg", "anchor"}
        if attribute not in allowed_attributes:
            return

        model = self.get_model_from_model_id(model_id)

        if attribute in ("x", "y"):
            if attribute == "x":
                x, y = value, model.y
            else:
                x, y = model.x, value

            #batch app state changes so _on_changed_state gets called only once (instead of per change)
            with self.app_state.batch():
                self.app_state.set_widget_attribute(model, "x", x)
                self.app_state.set_widget_attribute(model, "y", y)
        elif attribute in ("width", "height"):
            with self.app_state.batch():
                self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
                self.app_state.set_widget_attribute(model, "height", widget.winfo_height())
        elif attribute == "text":
            with self.app_state.batch():
                self.app_state.set_widget_attribute(model, "text", value)
                self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
                self.app_state.set_widget_attribute(model, "height", widget.winfo_height())
        elif attribute in ("bg", "fg"):
            self.app_state.set_widget_attribute(model, attribute, value)
        elif attribute == "anchor":
            self.app_state.set_widget_attribute(model, "anchor", value)

        self.selection_manager.refresh(model_id)

    def _bind_widget_events(self, widget, model_id: str):
        """bind widget mouse/configure events and forward to canvas where needed"""
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
            "<Configure>", lambda e, m_id=model_id: (
                self.selection_manager
                and not self.selection_manager.is_dragging()
                and self.selection_manager.refresh(m_id)
            )
        )

        #forward all mouse events from the widget to the canvas
        widget.bind("<ButtonPress-1>", lambda event: forward_to_canvas(event, "<ButtonPress-1>"))
        #widget.bind("<B1-Motion>", lambda event: forward_to_canvas(event, "<B1-Motion>"))
        widget.bind("<ButtonRelease-1>", lambda event: forward_to_canvas(event, "<ButtonRelease-1>"))