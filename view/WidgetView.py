import tkinter as tk
from utility import WidgetType

class WidgetView:
    """
    Tk-only view that builds, renders, updates and destroys widget instances
    based on model data and maintains widget <> model mappings.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        canvas: tk.Canvas
    ):
        """store canvas reference and widget/model mappings"""
        self.canvas = canvas
        self.widget_map = {}                            #{widget ID: {"model": model, "widget": widget}}
        self.model_id_to_widget_id: dict[str, int] = {} #model ID → widget ID
        self.widget_id_to_model_id: dict[int, str] = {} #widget ID → model ID

    #Rendering API------------------------------------------------------------------------------------------------------
    def update_widget_for(self, model):
        """create or update the tk widget for the given model"""
        if model.x is None or model.y is None:
            raise ValueError(f"WidgetView - widget update failed: missing position for model \"{model.id}\"")

        widget_id = self.get_widget_id_from_model_id(model.id)

        if widget_id is None:
            """
            widget_id refers to the canvas window item ID returned by
            canvas.create_window(...), not the Tk widget instance itself.

            Tkinter represents an embedded widget using:
               1. a Tk widget instance (Label, Entry, Button...)
               2. a canvas window item that owns the widget's placement

            Both objects are required:
               widget    → appearance/configuration
               widget_id → canvas positioning and canvas item configuration
            """
            widget, widget_id = self._create_widget_for(model)
        else:
            entry = self.widget_map.get(widget_id)
            if not entry:
                raise ValueError(f"WidgetView - widget update failed: unknown widget ID \"{widget_id}\"")
            widget = entry["widget"]

        self._update_widget(widget, widget_id, model)

    def delete_widget_for(self, model_id: str):
        """delete the widget associated with the given model ID"""
        widget_id = self.get_widget_id_from_model_id(model_id)

        if widget_id not in self.widget_map:
            return

        widget_map_entry = self.widget_map.pop(widget_id)

        #delete the widget from canvas
        self.canvas.delete(widget_id)

        #delete the tk widget instance
        if widget_map_entry:
            widget = widget_map_entry["widget"]
            widget.destroy()

        #remove from mappings
        self.model_id_to_widget_id.pop(model_id, None)
        self.widget_id_to_model_id.pop(widget_id, None)

    def measure_preview_widget(self, widget_type: WidgetType, text: str):
        """create a temporary preview widget then measure and return its required size"""
        #create temporary widget
        widget = self._instantiate_widget(widget_type)

        if widget_type in (WidgetType.LABEL, WidgetType.BUTTON):
            widget.config(text=text)

        #measure required size
        widget.update_idletasks()
        widget_width = widget.winfo_reqwidth()
        widget_height = widget.winfo_reqheight()

        #delete temporary widget
        widget.destroy()

        return widget_width, widget_height

    #Internals----------------------------------------------------------------------------------------------------------
    def _create_widget_for(self, model):
        widget = self._instantiate_widget(model.type)
        widget_id = self._insert_widget_into_canvas(widget, model.x, model.y, model.anchor)
        self._register_widget_mappings(model, widget, widget_id)
        self._bind_widget_events(widget)
        return widget, widget_id

    def _update_widget(self, widget, widget_id, model):
        self.canvas.coords(widget_id, model.x, model.y)
        widget.config(
            bg=model.bg,
            fg=model.fg
        )

        if model.type in (WidgetType.LABEL, WidgetType.BUTTON):
            widget.config(text=model.text)

        self.canvas.itemconfig(
            widget_id,
            anchor=model.anchor,
            width=model.width,
            height=model.height
        )

    def _instantiate_widget(self, widget_type):
        """instantiate a tk widget instance based on the widget type"""
        if widget_type == WidgetType.LABEL:
            return tk.Label(self.canvas)
        elif widget_type == WidgetType.ENTRY:
            return tk.Entry(self.canvas)
        elif widget_type == WidgetType.BUTTON:
            return tk.Button(self.canvas)
        raise ValueError(f"WidgetView - widget creation failed: unsupported type \"{widget_type}\"")

    def _insert_widget_into_canvas(self, widget, x, y, anchor):
        """place widget on canvas and return resulting widget ID"""
        widget_id = self.canvas.create_window(
            x, y,
            window=widget,
            anchor=anchor,
            tags="widget"
        )
        return widget_id

    def _register_widget_mappings(self, model, widget, widget_id):
        """insert widget and model into widget map (keyed by widget ID) and register widget ID <> model ID mappings"""
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

    #Helpers------------------------------------------------------------------------------------------------------------
    def get_widget_id_from_model_id(self, model_id: str) -> int | None:
        """return the widget ID mapped to a model ID"""
        return self.model_id_to_widget_id.get(model_id)

    def get_widget_from_model_id(self, model_id: str) -> tk.Label | tk.Entry | tk.Button | None:
        """return the widget associated with a given model ID"""
        widget_id = self.get_widget_id_from_model_id(model_id)
        if widget_id is None:
            return None #widget not created yet (valid state)

        entry = self.widget_map.get(widget_id)
        if not entry:
            raise ValueError(f"WidgetView - widget lookup failed: unknown widget ID \"{widget_id}\"")
        return entry["widget"]

    def get_model_id_from_widget_id(self, widget_id: int) -> str | None:
        """return the model ID mapped to a widget ID"""
        return self.widget_id_to_model_id.get(widget_id)
