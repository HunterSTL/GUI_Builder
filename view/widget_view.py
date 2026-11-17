import tkinter as tk
from dataclasses import dataclass

from model import Widget
from utility.geometry import compute_widget_bounding_box
from utility.widget_type import WidgetType


@dataclass
class _WidgetVisual:
    """Stores references to canvas items that visually represent a domain widget."""
    rectangle_id: int
    text_id: int | None


class WidgetView:
    """Renders widget visuals and maintains their canvas and domain identity mappings."""
    def __init__(
        self,
        canvas: tk.Canvas
    ) -> None:
        self._canvas: tk.Canvas = canvas

        self._widget_visual_by_widget_id: dict[str, _WidgetVisual] = {}
        self._widget_id_by_canvas_item_id: dict[int, str] = {}

    def render_widget_visual_for(
        self,
        widget: Widget
    ) -> None:
        """Create or update the widget visual for the given domain widget."""
        widget_visual = self._widget_visual_by_widget_id.get(widget.id)

        if not widget_visual:
            self._create_widget_visual_for(widget)

        self._update_widget_visual_for(widget)

    def delete_widget_visual_for(
        self,
        widget_id: str
    ) -> None:
        """Delete the widget visual associated with the given widget ID."""
        widget_visual = self._widget_visual_by_widget_id.get(widget_id)

        if not widget_visual:
            return

        self._widget_visual_by_widget_id.pop(widget_id)
        self._canvas.delete(widget_visual.rectangle_id)
        self._widget_id_by_canvas_item_id.pop(widget_visual.rectangle_id)

        if not widget_visual.text_id:
            return

        self._canvas.delete(widget_visual.text_id)
        self._widget_id_by_canvas_item_id.pop(widget_visual.text_id)

    def measure_preview_tk_widget(
        self,
        widget_type: WidgetType,
        text: str
    ) -> tuple[int, int]:
        """Create and measure a temporary Tk widget, then return its required size."""
        if widget_type == WidgetType.LABEL:
            tk_widget = tk.Label(self._canvas)
        elif widget_type == WidgetType.ENTRY:
            tk_widget = tk.Entry(self._canvas)
        elif widget_type == WidgetType.BUTTON:
            tk_widget = tk.Button(self._canvas)
        else:
            raise ValueError(f"WidgetView - Preview Tk widget measurement failed: unsupported type \"{widget_type}\"")

        try:
            if widget_type.supports_text:
                tk_widget.config(text=text)

            tk_widget.update_idletasks()
            widget_width = tk_widget.winfo_reqwidth()
            widget_height = tk_widget.winfo_reqheight()
        finally:
            tk_widget.destroy()
        return widget_width, widget_height

    def get_widget_id_from_canvas_item_id(
        self,
        canvas_item_id: int
    ) -> str:
        """Return the widget ID associated with the given canvas item ID."""
        try:
            return self._widget_id_by_canvas_item_id[canvas_item_id]
        except KeyError:
            raise ValueError(f"WidgetView - widget lookup failed: unknown canvas item ID \"{canvas_item_id}\"")

    def _create_widget_visual_for(
        self,
        widget: Widget
    ) -> None:
        """Create a widget visual for the given domain widget."""
        rectangle_id = self._canvas.create_rectangle(
            0, 0, 0, 0,
            tags="widget_visual"
        )
        self._widget_id_by_canvas_item_id[rectangle_id] = widget.id

        if widget.type.supports_text:
            text_id = self._canvas.create_text(0, 0)
            self._widget_id_by_canvas_item_id[text_id] = widget.id
        else:
            text_id = None

        widget_visual = _WidgetVisual(
            rectangle_id=rectangle_id,
            text_id=text_id
        )

        self._widget_visual_by_widget_id[widget.id] = widget_visual

    def _update_widget_visual_for(
        self,
        widget: Widget
    ) -> None:
        """Update the widget visual's rectangle and text to match the given domain widget."""
        widget_visual = self._widget_visual_by_widget_id[widget.id]

        bbox = compute_widget_bounding_box(
            x=widget.x,
            y=widget.y,
            width=widget.width,
            height=widget.height,
            anchor=widget.anchor
        )

        self._canvas.coords(
            widget_visual.rectangle_id,
            bbox.left,
            bbox.top,
            bbox.right,
            bbox.bottom
        )

        self._canvas.itemconfig(
            widget_visual.rectangle_id,
            fill=widget.bg
        )

        if not widget_visual.text_id:
            return

        self._canvas.coords(
            widget_visual.text_id,
            bbox.center
        )

        self._canvas.itemconfig(
            widget_visual.text_id,
            text=widget.text,
            fill=widget.fg
        )
