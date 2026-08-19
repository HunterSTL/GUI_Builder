import copy

from model import BaseWidget
from utility import WidgetType, clamped_delta, format_field, format_mapping

from AppState import AppState
from .BaseCommand import Command


class PasteWidgetsFromClipboard(Command):
    """Encapsulates widget pasting as an undoable command."""
    def __init__(
        self,
        clipboard: list[dict[str, str | int]],
        requested_x_offset: int,
        requested_y_offset: int,
        app_state: AppState
    ) -> None:
        self._clipboard: list[dict[str, str | int]] = copy.deepcopy(clipboard)
        self._requested_x_offset: int = requested_x_offset
        self._requested_y_offset: int = requested_y_offset
        self._app_state: AppState = app_state

        self._final_snapshot: list[dict[str, str | int]] | None = None  #populated on first execution to prevent mutating project state at construction (ID counters), reused on redo
        self._clamped_x_offset: int | None = None
        self._clamped_y_offset: int | None = None

    def _create_final_snapshot(
        self
    ) -> list[dict[str, str | int]]:
        """
        Copy widget data from the clipboard,
        replace the source ID with a newly created one,
        create widgets from the widget data,
        clamp the requested paste offset to canvas bounds,
        apply the clamped offset and serialize the widgets into the final snapshot.
        """
        created_widgets: list[BaseWidget] = []

        for clipboard_data in self._clipboard:
            widget_data = clipboard_data.copy()
            widget_type = WidgetType(widget_data["type"])
            widget_id = self._app_state.project.id_counters.generate_id(widget_type)
            widget_data["id"] = widget_id   #clipboard data contains the source ID, but pasted widgets must receive new IDs
            created_widgets.append(BaseWidget.from_dict(widget_data))

        clamped_x_offset, clamped_y_offset = clamped_delta(
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_widget_group_bounding_box(created_widgets),
            dx=self._requested_x_offset,
            dy=self._requested_y_offset
        )

        self._clamped_x_offset = clamped_x_offset
        self._clamped_y_offset = clamped_y_offset

        final_snapshot = []
        for widget in created_widgets:
            widget.x += clamped_x_offset    #widgets can be safely edited because they are not yet owned by AppState
            widget.y += clamped_y_offset
            final_snapshot.append(widget.to_dict())

        return final_snapshot

    def execute(
        self
    ) -> None:
        """
        Create the final snapshot if it doesn't already exist,
        then create widgets from the final snapshot,
        add them to the project through AppState
        and select all created widgets.
        """
        if self._final_snapshot is None:
            self._final_snapshot = self._create_final_snapshot()

        with self._app_state.batch():
            for widget_data in self._final_snapshot:
                widget = BaseWidget.from_dict(widget_data)
                self._app_state.add_widget(widget)  #selects only the added widget

            self._app_state.selection_clear()
            for widget_data in self._final_snapshot:
                self._app_state.selection_toggle(widget_data["id"])

    def undo(
        self
    ) -> None:
        """Remove previously created widgets from the project through AppState."""
        with self._app_state.batch():
            for widget_data in self._final_snapshot:
                widget = self._app_state.get_widget_from_widget_id(widget_data["id"])
                self._app_state.remove_widget(widget)

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

        if self._final_snapshot is None:
            return "\n".join(lines)

        for widget_data in self._final_snapshot:
            widget_data = widget_data.copy()    #prevents mutating the snapshot
            widget_id = widget_data.pop("id")
            lines.append(
                format_mapping(
                    label=widget_id,
                    mapping=widget_data
                )
            )
        return "\n".join(lines)
