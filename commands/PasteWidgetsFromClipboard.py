import copy

from model import BaseWidget
from utility import WidgetType, clamped_delta

from AppState import AppState
from .BaseCommand import Command


class PasteWidgetsFromClipboard(Command):
    """Encapsulates widget pasting as an undoable command."""
    def __init__(
        self,
        clipboard: list[dict[str, str | int | None]],
        dx: int,
        dy: int,
        app_state: AppState
    ) -> None:
        self._clipboard: list[dict[str, str | int | None]] = copy.deepcopy(clipboard)
        self._dx: int = dx
        self._dy: int = dy
        self._app_state: AppState = app_state

        self._first_execution: bool = True
        self._pasted_ids: list[str] = []    #populated on first execution, reused on redo

    def execute(
        self
    ) -> None:
        """
        Create widgets from the snapshotted clipboard data,
        clamp the requested paste offset to canvas bounds,
        apply the offset, add the widgets to the project and select them.
        """
        created_widgets: list[BaseWidget] = []

        for i, clipboard_data in enumerate(self._clipboard):
            widget_data = clipboard_data.copy()

            if self._first_execution:       #generates new IDs during the first execution
                widget_type = WidgetType(widget_data["type"])
                widget_id = self._app_state.project.id_counters.generate_id(widget_type)
                self._pasted_ids.append(widget_id)
            else:                           #reuses generated IDs during subsequent executions
                widget_id = self._pasted_ids[i]

            widget_data["id"] = widget_id   #clipboard data contains the source ID, but pasted widgets must receive new IDs
            widget = BaseWidget.from_dict(widget_data)
            created_widgets.append(widget)

        x_offset, y_offset = clamped_delta(
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_widget_group_bounding_box(created_widgets),
            dx=self._dx,
            dy=self._dy
        )

        for widget in created_widgets:
            widget.x += x_offset    #widgets can be safely edited because they are not yet owned by AppState
            widget.y += y_offset

        with self._app_state.batch():
            for widget in created_widgets:
                self._app_state.add_widget(widget)  #selects only the added widget

            self._app_state.selection_clear()
            for widget in created_widgets:
                self._app_state.selection_toggle(widget.id)

        self._first_execution = False

    def undo(
        self
    ) -> None:
        """Remove previously created widgets from the project through AppState."""
        with self._app_state.batch():
            for pasted_id in self._pasted_ids:
                widget = self._app_state.get_widget_from_widget_id(pasted_id)
                self._app_state.remove_widget(widget)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[PasteWidgetsFromClipboard]"
        for widget_data in self._clipboard:
            s += f"\n\t{widget_data}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        s += f"\n\tpasted IDs:\t\t{self._pasted_ids}"
        return s
