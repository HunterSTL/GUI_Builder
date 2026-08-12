import tkinter as tk
from utility import WidgetType

class WidgetView:
    """
    Tk-only view that builds, renders, updates and destroys Tk widgets
    based on domain widgets and maintains mappings between Tk widgets and domain widgets.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        canvas: tk.Canvas
    ):
        self.canvas = canvas
        self.widget_map = {}                            #{canvas item ID: {"widget": widget, "tk_widget": tk_widget}}
        self.widget_id_to_canvas_item_id: dict[str, int] = {}
        self.canvas_item_id_to_widget_id: dict[int, str] = {}

    #Rendering API------------------------------------------------------------------------------------------------------
    def render_tk_widget_for(self, widget):
        """create or update the Tk widget for the given domain widget"""
        if widget.x is None or widget.y is None:
            raise ValueError(f"WidgetView - Tk widget rendering failed: missing position for widget \"{widget.id}\"")

        canvas_item_id = self.get_canvas_item_id_from_widget_id(widget.id)

        if canvas_item_id is None:
            tk_widget, canvas_item_id = self._create_tk_widget_for(widget)
        else:
            entry = self.widget_map.get(canvas_item_id)
            if not entry:
                raise ValueError(f"WidgetView - Tk widget rendering failed: unknown canvas item ID \"{canvas_item_id}\"")
            tk_widget = entry["tk_widget"]

        self._update_tk_widget(tk_widget, canvas_item_id, widget)

    def delete_tk_widget_for(self, widget_id: str):
        """delete the Tk widget associated with the given widget ID"""
        canvas_item_id = self.get_canvas_item_id_from_widget_id(widget_id)

        if canvas_item_id not in self.widget_map:
            return

        widget_map_entry = self.widget_map.pop(canvas_item_id)

        #delete the canvas window that hosts the Tk widget
        self.canvas.delete(canvas_item_id)

        #delete the Tk widget
        if widget_map_entry:
            tk_widget = widget_map_entry["tk_widget"]
            tk_widget.destroy()

        #remove from mappings
        self.widget_id_to_canvas_item_id.pop(widget_id, None)
        self.canvas_item_id_to_widget_id.pop(canvas_item_id, None)

    def measure_preview_tk_widget(self, widget_type: WidgetType, text: str):
        """create a temporary preview Tk widget then measure and return its required size"""
        #create temporary Tk widget
        tk_widget = self._instantiate_tk_widget(widget_type)

        if widget_type in (WidgetType.LABEL, WidgetType.BUTTON):
            tk_widget.config(text=text)

        #measure required size
        tk_widget.update_idletasks()
        widget_width = tk_widget.winfo_reqwidth()
        widget_height = tk_widget.winfo_reqheight()

        #delete temporary widget
        tk_widget.destroy()

        return widget_width, widget_height

    #Internals----------------------------------------------------------------------------------------------------------
    def _create_tk_widget_for(self, widget):
        tk_widget = self._instantiate_tk_widget(widget.type)
        canvas_item_id = self._insert_tk_widget_into_canvas(tk_widget, widget.x, widget.y, widget.anchor)
        self._register_widget_mappings(widget, tk_widget, canvas_item_id)
        self._bind_tk_widget_events(tk_widget)
        return tk_widget, canvas_item_id

    def _update_tk_widget(self, tk_widget, canvas_item_id, widget):
        self.canvas.coords(canvas_item_id, widget.x, widget.y)
        tk_widget.config(
            bg=widget.bg,
            fg=widget.fg
        )

        if widget.type in (WidgetType.LABEL, WidgetType.BUTTON):
            tk_widget.config(text=widget.text)

        self.canvas.itemconfig(
            canvas_item_id,
            anchor=widget.anchor,
            width=widget.width,
            height=widget.height
        )

    def _instantiate_tk_widget(self, widget_type):
        """instantiate a Tk widget instance based on the widget type"""
        if widget_type == WidgetType.LABEL:
            return tk.Label(self.canvas)
        elif widget_type == WidgetType.ENTRY:
            return tk.Entry(self.canvas)
        elif widget_type == WidgetType.BUTTON:
            return tk.Button(self.canvas)
        raise ValueError(f"WidgetView - Tk widget instantiation failed: unsupported type \"{widget_type}\"")

    def _insert_tk_widget_into_canvas(self, tk_widget, x, y, anchor):
        """insert the Tk widget into the canvas and return resulting canvas item ID"""
        canvas_item_id = self.canvas.create_window(
            x, y,
            window=tk_widget,
            anchor=anchor,
            tags="widget"
        )
        return canvas_item_id

    def _register_widget_mappings(self, widget, tk_widget, canvas_item_id):
        """insert the given Tk widget and domain widget into the widget map (keyed by canvas item ID) and register canvas item ID <> widget ID mappings"""
        self.widget_map[canvas_item_id] = {"widget": widget, "tk_widget": tk_widget}
        self.canvas_item_id_to_widget_id[canvas_item_id] = widget.id
        self.widget_id_to_canvas_item_id[widget.id] = canvas_item_id

    def _bind_tk_widget_events(self, tk_widget):
        """forward Tk widget mouse events to the canvas"""
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

        #forward all mouse events from the Tk widget to the canvas
        tk_widget.bind("<ButtonPress-1>", lambda event: forward_to_canvas(event, "<ButtonPress-1>"))
        tk_widget.bind("<B1-Motion>", lambda event: forward_to_canvas(event, "<B1-Motion>"))
        tk_widget.bind("<ButtonRelease-1>", lambda event: forward_to_canvas(event, "<ButtonRelease-1>"))

    #Helpers------------------------------------------------------------------------------------------------------------
    def get_canvas_item_id_from_widget_id(self, widget_id: str) -> int | None:
        """return the canvas item ID associated with the given widget ID"""
        return self.widget_id_to_canvas_item_id.get(widget_id)

    def get_tk_widget_from_widget_id(self, widget_id: str) -> tk.Label | tk.Entry | tk.Button | None:
        """return the Tk widget associated with the given widget ID"""
        canvas_item_id = self.get_canvas_item_id_from_widget_id(widget_id)
        if canvas_item_id is None:
            return None #widget not created yet (valid state)

        entry = self.widget_map.get(canvas_item_id)
        if not entry:
            raise ValueError(f"WidgetView - Tk widget lookup failed: unknown canvas item ID \"{canvas_item_id}\"")
        return entry["tk_widget"]

    def get_widget_id_from_canvas_item_id(self, canvas_item_id: int) -> str | None:
        """return the widget ID associated with the given canvas item ID"""
        return self.canvas_item_id_to_widget_id.get(canvas_item_id)
