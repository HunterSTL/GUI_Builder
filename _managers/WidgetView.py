import tkinter as tk

class WidgetView:
    """
    Tk-only view that builds, renders, updates and destroys widget instances
    based on model data and maintains widget <> model mappings.
    """
    def __init__(
        self,
        canvas: tk.Canvas
    ):
        """store canvas reference and widget/model mappings"""
        self.canvas = canvas
        self.widget_map = {}                            #{widget_id: {"model": model, "widget": widget}}
        self.model_id_to_widget_id: dict[str, int] = {} #model_id → widget_id
        self.widget_id_to_model_id: dict[int, str] = {} #widget_id → model_id

    #Internals----------------------------------------------------------------------------------------------------------
    def _create_widget_from_model(self, model):
        """create a tk widget based on the model.type"""
        if model.type == "Label":
            return tk.Label(self.canvas)
        elif model.type == "Entry":
            return tk.Entry(self.canvas)
        elif model.type == "Button":
            return tk.Button(self.canvas)
        return None

    def _insert_widget_into_canvas(self, widget, x, y, anchor):
        """place widget on canvas and return resulting widget_id"""
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

    def _bind_widget_events(self, widget):
        """forward widget events to the canvas"""
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

    def _render_widget(self, model):
        """create, map and render a tk widget for a given model and bind widget events"""
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

    #Rendering API------------------------------------------------------------------------------------------------------
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

        #update canvas owned attributes (anchor, dimensions)
        self.canvas.itemconfig(
            widget_id,
            anchor=model.anchor,
            width=model.width,
            height=model.height
        )

    def render_full(self, models):
        """fully rebuild all widgets from the project models"""
        #clear all canvas items except grid lines
        for widget_id, widget_map_entry in list(self.widget_map.items()):
            #delete the widget from canvas
            self.canvas.delete(widget_id)

            #delete the tk widget instance
            if widget_map_entry:
                widget = widget_map_entry["widget"]
                widget.destroy()

        #clear widget_map and model_id <> widget_id mappings
        self.widget_map.clear()
        self.model_id_to_widget_id.clear()
        self.widget_id_to_model_id.clear()

        #rebuild widgets from models
        for model in models:
            self._render_widget(model)

    def create_preview_widget(self, model):
        """create a temporary tk widget to measure size & clamp coordinates"""
        #create the correct Tk widget
        widget = self._create_widget_from_model(model)

        #insert widget into canvas
        widget_id = self._insert_widget_into_canvas(widget, model.x, model.y, model.anchor)

        return widget, widget_id

    def delete_widget(self, model_id: str):
        """delete a widget from the canvas and remove it from all mappings"""
        #delete widget_id from model_id <> widget_id mapping
        widget_id = self.model_id_to_widget_id.pop(model_id, None)

        if widget_id:
            #delete model_id from widget_id <> model_id mapping
            self.widget_id_to_model_id.pop(widget_id, None)

            #delete widget_id from widget_map
            widget_map_entry = self.widget_map.pop(widget_id, None)

            #delete the widget from canvas
            self.canvas.delete(widget_id)

            #delete the tk widget instance
            if widget_map_entry:
                widget = widget_map_entry["widget"]
                widget.destroy()

    #Helpers------------------------------------------------------------------------------------------------------------
    def get_widget_id_from_model_id(self, model_id: str):
        """return the widget_id mapped to a model_id"""
        return self.model_id_to_widget_id.get(model_id)

    def get_widget_from_model_id(self, model_id: str):
        """return the widget associated with a given model_id"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        if widget_id is None:
            return None
        return self.widget_map.get(widget_id)["widget"]

    def get_model_id_from_widget_id(self, widget_id: int):
        """return the model_id mapped to a widget_id"""
        return self.widget_id_to_model_id.get(widget_id)

    def get_bbox_from_model_id(self, model_id: str):
        """return the bounding box of the widget"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        if widget_id is None:
            return None

        bbox = self.canvas.bbox(widget_id)
        if bbox is None:
            return None

        x1, y1, x2, y2 = bbox
        return {
            "left": x1,
            "top": y1,
            "right": x2,
            "bottom": y2
        }