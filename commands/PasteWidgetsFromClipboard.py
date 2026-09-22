from copy import deepcopy

from model import BaseWidget
from utility import clamped_delta, format_field, format_mapping

from AppState import AppState
from .BaseCommand import Command


class PasteWidgetsFromClipboard(Command):
    """Encapsulates widget pasting as an undoable command."""
    def __init__(
        self,
        clipboard: list[dict[str, str | int | None]],
        requested_x_offset: int,
        requested_y_offset: int,
        app_state: AppState
    ) -> None:
        self._requested_x_offset: int = requested_x_offset
        self._requested_y_offset: int = requested_y_offset
        self._app_state: AppState = app_state

        created_widgets: list[BaseWidget] = []

        for clipboard_data in deepcopy(clipboard):
            widget_data = clipboard_data.copy()
            created_widgets.append(BaseWidget.from_dict(widget_data))

        clamped_x_offset, clamped_y_offset = clamped_delta(
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_widget_group_bounding_box(created_widgets),
            dx=self._requested_x_offset,
            dy=self._requested_y_offset
        )

        self._clamped_x_offset: int | None = clamped_x_offset
        self._clamped_y_offset: int | None = clamped_y_offset
        self._widget_data_list: list[dict[str, str | int | None]] = []

        for widget in created_widgets:
            widget.x += clamped_x_offset    #widgets can be safely edited because they are not yet owned by AppState
            widget.y += clamped_y_offset
            self._widget_data_list.append(widget.to_dict())

    def execute(
        self
    ) -> None:
        """Create widgets from the stored widget data, assign them new IDs, add them to the project and select all created widgets."""
        with self._app_state.batch():
            for widget_data in self._widget_data_list:
                widget = BaseWidget.from_dict(widget_data)
                widget.id = self._app_state.project.id_counters.generate_id(widget.type)
                self._app_state.add_widget(widget)  #selects only the added widget
                widget_data["id"] = widget.id


            self._app_state.selection_clear()
            for widget_data in self._widget_data_list:
                self._app_state.selection_toggle(widget_data["id"])

    def undo(
        self
    ) -> None:
        """Remove the previously created widgets from the project."""
        with self._app_state.batch():
            for widget_data in self._widget_data_list:
                widget = self._app_state.get_widget_from_widget_id(widget_data["id"])
                self._app_state.project.id_counters.decrement_counter(widget.type)
                self._app_state.remove_widget(widget)
                widget_data["id"] = None

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[PasteWidgetsFromClipboard]",
            format_field(
                label="requested offset",
                value=f"({self._requested_x_offset}, {self._requested_y_offset})"
            ),
            format_field(
                label="clamped offset",
                value=f"({self._clamped_x_offset}, {self._clamped_y_offset})"
            )
        ]

        for widget_data in self._widget_data_list:
            widget_data = widget_data.copy()    #prevents mutating the snapshot
            widget_id = widget_data.pop("id")
            lines.append(
                format_mapping(
                    label=widget_id,
                    mapping=widget_data
                )
            )
        return "\n".join(lines)
