import tkinter as tk

from model import BaseWidget
from utility import WidgetType


class WidgetView:
    """Renders Tk widgets and maintains their canvas and domain identity mappings."""
    def __init__(
        self,
        canvas: tk.Canvas
    ) -> None:
        self._canvas: tk.Canvas = canvas

        self._tk_widget_by_canvas_item_id: dict[int, tk.Label | tk.Entry | tk.Button] = {}
        self._canvas_item_id_by_widget_id: dict[str, int] = {}
        self._widget_id_by_canvas_item_id: dict[int, str] = {}

    def render_tk_widget_for(
        self,
        widget: BaseWidget
    ) -> None:
        """Create or update the Tk widget for the given domain widget."""
        canvas_item_id = self.get_canvas_item_id_from_widget_id(widget.id)

        if canvas_item_id is None:
            canvas_item_id = self._create_tk_widget_for(widget)

        self._update_tk_widget(canvas_item_id, widget)

    def delete_tk_widget_for(
        self,
        widget_id: str
    ) -> None:
        """Delete the Tk widget associated with the given widget ID."""
        canvas_item_id = self.get_canvas_item_id_from_widget_id(widget_id)

        if canvas_item_id is None:
            return

        tk_widget = self._tk_widget_by_canvas_item_id.get(canvas_item_id)

        if tk_widget is None:
            raise ValueError(f"WidgetView - Tk widget deletion failed: missing Tk widget for canvas item \"{canvas_item_id}\"")

        self._canvas.delete(canvas_item_id)
        tk_widget.destroy()

        self._tk_widget_by_canvas_item_id.pop(canvas_item_id)
        self._canvas_item_id_by_widget_id.pop(widget_id)
        self._widget_id_by_canvas_item_id.pop(canvas_item_id)

    def measure_preview_tk_widget(
        self,
        widget_type: WidgetType,
        text: str
    ) -> tuple[int, int]:
        """Create and measure a temporary Tk widget, then return its required size."""
        tk_widget = self._instantiate_tk_widget(widget_type)

        try:
            if widget_type in (WidgetType.LABEL, WidgetType.BUTTON):
                tk_widget.config(text=text)

            tk_widget.update_idletasks()
            widget_width = tk_widget.winfo_reqwidth()
            widget_height = tk_widget.winfo_reqheight()
        finally:
            tk_widget.destroy()
        return widget_width, widget_height

    def get_canvas_item_id_from_widget_id(
        self,
        widget_id: str
    ) -> int | None:
        """Return the canvas item ID associated with the given widget ID."""
        return self._canvas_item_id_by_widget_id.get(widget_id)

    def get_widget_id_from_canvas_item_id(
        self,
        canvas_item_id: int
    ) -> str:
        """Return the widget ID associated with the given canvas item ID."""
        try:
            return self._widget_id_by_canvas_item_id[canvas_item_id]
        except KeyError:
            raise ValueError(f"WidgetView - widget lookup failed: unknown canvas item ID \"{canvas_item_id}\"")

    def _create_tk_widget_for(
        self,
        widget: BaseWidget
    ) -> int:
        """Create and register a Tk widget for the given domain widget."""
        tk_widget = self._instantiate_tk_widget(widget.type)
        canvas_item_id = self._insert_tk_widget_into_canvas(
            tk_widget=tk_widget,
            x=widget.x,
            y=widget.y,
            anchor=widget.anchor
        )
        self._register_widget_mappings(
            widget_id=widget.id,
            tk_widget=tk_widget,
            canvas_item_id=canvas_item_id
        )
        self._bind_tk_widget_events(tk_widget)
        return canvas_item_id

    def _update_tk_widget(
        self,
        canvas_item_id: int,
        widget: BaseWidget
    ) -> None:
        tk_widget = self._tk_widget_by_canvas_item_id.get(canvas_item_id)

        if tk_widget is None:
            raise ValueError(f"WidgetView - Tk widget rendering failed: missing Tk widget for canvas item \"{canvas_item_id}\"")

        self._canvas.coords(canvas_item_id, widget.x, widget.y)
        tk_widget.config(
            bg=widget.bg,
            fg=widget.fg
        )

        if widget.type in (WidgetType.LABEL, WidgetType.BUTTON):
            tk_widget.config(text=widget.text)

        self._canvas.itemconfig(
            canvas_item_id,
            anchor=widget.anchor,
            width=widget.width,
            height=widget.height
        )

    def _instantiate_tk_widget(
        self,
        widget_type: WidgetType
    ) -> tk.Label | tk.Entry | tk.Button:
        """Instantiate a Tk widget for the given widget type."""
        if widget_type == WidgetType.LABEL:
            return tk.Label(self._canvas)
        elif widget_type == WidgetType.ENTRY:
            return tk.Entry(self._canvas)
        elif widget_type == WidgetType.BUTTON:
            return tk.Button(self._canvas)
        raise ValueError(f"WidgetView - Tk widget instantiation failed: unsupported type \"{widget_type}\"")

    def _insert_tk_widget_into_canvas(
        self,
        tk_widget: tk.Label | tk.Entry | tk.Button,
        x: int,
        y: int,
        anchor: str
    ) -> int:
        """Insert the Tk widget into the canvas and return the resulting canvas item ID."""
        canvas_item_id = self._canvas.create_window(
            x, y,
            window=tk_widget,
            anchor=anchor,
            tags="widget"
        )
        return canvas_item_id

    def _register_widget_mappings(
        self,
        widget_id: str,
        tk_widget: tk.Label | tk.Entry | tk.Button,
        canvas_item_id: int
    ) -> None:
        self._tk_widget_by_canvas_item_id[canvas_item_id] = tk_widget
        self._widget_id_by_canvas_item_id[canvas_item_id] = widget_id
        self._canvas_item_id_by_widget_id[widget_id] = canvas_item_id

    def _bind_tk_widget_events(
        self,
        tk_widget: tk.Label | tk.Entry | tk.Button
    ) -> None:
        """Forward Tk widget mouse events to the canvas."""
        def forward_to_canvas(
            event: tk.Event,
            sequence: str
        ) -> str:
            canvas_x = event.x_root - self._canvas.winfo_rootx()
            canvas_y = event.y_root - self._canvas.winfo_rooty()

            self._canvas.event_generate(
                sequence,
                x=canvas_x,
                y=canvas_y,
                state=event.state
            )
            return "break"

        tk_widget.bind("<ButtonPress-1>", lambda event: forward_to_canvas(event, "<ButtonPress-1>"))
        tk_widget.bind("<B1-Motion>", lambda event: forward_to_canvas(event, "<B1-Motion>"))
        tk_widget.bind("<ButtonRelease-1>", lambda event: forward_to_canvas(event, "<ButtonRelease-1>"))
