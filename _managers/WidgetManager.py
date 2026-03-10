import tkinter as tk
from AppState import AppState

class WidgetManager:
    def __init__(
        self,
        top: tk.Tk | tk.Toplevel,
        canvas: tk.Canvas,
        app_state: AppState
    ):
        """initialize the widget manager and its widget/model mappings"""
        self.top = top
        self.canvas = canvas
        self.app_state = app_state
        self.widget_map = {}
        self.model_id_to_widget_id: dict[str, int] = {}
        self.widget_id_to_model_id: dict[int, str] = {}

    def _create_widget_from_model(self, model):
        """create a Tk widget based on the model.type"""
        if model.type == "Label":
            return tk.Label(self.canvas)
        elif model.type == "Entry":
            return tk.Entry(self.canvas)
        elif model.type == "Button":
            return tk.Button(self.canvas)
        return None

    def _insert_widget_into_canvas(self, widget, x, y, anchor):
        """create a canvas window for the widget and place it on model.x / model.y"""
        widget_id = self.canvas.create_window(
            x, y,
            window=widget,
            anchor=anchor,
            tags="widget"
        )
        return widget_id

    def _register_widget_mappings(self, model, widget, widget_id):
        """insert widget and model into widget map (keyed by widget_id) and register widget_id <> model_id mappings"""
        self.widget_map[widget_id] = {"model": model, "widget": widget}
        self.widget_id_to_model_id[widget_id] = model.id
        self.model_id_to_widget_id[model.id] = widget_id

    def _render_widget(self, model):
        """create a Tk widget from a model and register mappings"""
        #create the correct Tk widget
        widget = self._create_widget_from_model(model)

        #insert widget into canvas
        widget_id = self._insert_widget_into_canvas(widget, model.x, model.y, model.anchor)

        #insert widget into widget_map and register widget_id <> model_id mappings
        self._register_widget_mappings(model, widget, widget_id)

        #bind events
        self._bind_widget_events(widget)

        #apply attributes from model to the widget
        self.render_soft(model)

        #set focus back to canvas
        self.canvas.focus_set()

    def create_preview_widget(self, model):
        """create a temporary Tk widget to measure size & clamp coordinates"""
        #create the correct Tk widget
        widget = self._create_widget_from_model(model)

        #insert widget into canvas
        widget_id = self._insert_widget_into_canvas(widget, model.x, model.y, model.anchor)

        return widget, widget_id

    def render_full(self):
        """fully rebuild all widgets from the project models"""
        #clear all canvas items except grid lines
        for widget_id in list(self.widget_map.keys()):
            self.canvas.delete(widget_id)
        self.widget_map.clear()

        #clear mappings
        self.model_id_to_widget_id.clear()
        self.widget_id_to_model_id.clear()

        #rebuild widgets from models
        for model in self.app_state.project.widget_models:
            self._render_widget(model)

    def render_soft(self, model):
        """update an existing widget’s attributes to match the model"""
        #get the widget_id and widget of this model
        widget_id = self.get_widget_id_from_model_id(model.id)

        if widget_id is None:
            #widget does not exist yet → render it fully
            self._render_widget(model)
            return

        widget = self.widget_map[widget_id]["widget"]

        #update widget's position
        self.canvas.coords(widget_id, model.x, model.y)

        #update widget's colors
        widget.config(
            bg=model.bg,
            fg=model.fg
        )

        #update widget's text
        if model.type in ("Label", "Button"):
            widget.config(text=model.text)

        #update canvas owned attributes (anchor)
        self.canvas.itemconfig(
            widget_id,
            anchor=model.anchor,
            width=model.width,
            height=model.height
        )

    def get_model_from_model_id(self, model_id: str):
        """return the model associated with a given model_id"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        if widget_id is None:
            return None
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

        #changing text should resize the widget
        if attribute == "text":
            #apply new text to the actual widget so tk recomputes geometry
            widget.config(text=value)
            widget.update_idletasks()

            #fetch new dimensions
            new_width, new_height = widget.winfo_width(), widget.winfo_height()

            #update the model using batching (so only one notify happens)
            with self.app_state.batch():
                self.app_state.set_widget_attribute(model, "text", value)
                self.app_state.set_widget_attribute(model, "width", new_width)
                self.app_state.set_widget_attribute(model, "height", new_height)
        else:
            self.app_state.set_widget_attribute(model, attribute, value)

    def _bind_widget_events(self, widget):
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

        #forward all mouse events from the widget to the canvas
        widget.bind("<ButtonPress-1>", lambda event: forward_to_canvas(event, "<ButtonPress-1>"))
        widget.bind("<B1-Motion>", lambda event: forward_to_canvas(event, "<B1-Motion>"))
        widget.bind("<ButtonRelease-1>", lambda event: forward_to_canvas(event, "<ButtonRelease-1>"))