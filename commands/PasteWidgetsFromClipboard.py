import copy

from model import BaseWidgetData
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
        Create widget models from the snapshotted clipboard data,
        clamp the requested paste offset to canvas bounds,
        apply the offset, add the models to the project and select them.
        """
        created_models: list[BaseWidgetData] = []

        for i, clipboard_data in enumerate(self._clipboard):
            model_data = clipboard_data.copy()

            if self._first_execution:       #generates new IDs during the first execution
                widget_type = WidgetType(model_data["type"])
                model_id = self._app_state.project.id_counters.generate_id(widget_type)
                self._pasted_ids.append(model_id)
            else:                           #reuses generated IDs during subsequent executions
                model_id = self._pasted_ids[i]

            model_data["id"] = model_id     #clipboard data contains the source ID, but pasted widgets must receive new IDs
            model = BaseWidgetData.from_dict(model_data)
            created_models.append(model)

        x_offset, y_offset = clamped_delta(
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_model_group_bounding_box(created_models),
            dx=self._dx,
            dy=self._dy
        )

        for model in created_models:
            model.x += x_offset     #models can be safely edited because they are not yet owned by AppState
            model.y += y_offset

        with self._app_state.batch():
            for model in created_models:
                self._app_state.add_model(model)    #selects only the added model

            self._app_state.selection_clear()
            for model in created_models:
                self._app_state.selection_toggle(model.id)

        self._first_execution = False

    def undo(
        self
    ) -> None:
        """Remove previously created widget models from the project through AppState."""
        with self._app_state.batch():
            for pasted_id in self._pasted_ids:
                model = self._app_state.get_model_from_model_id(pasted_id)
                self._app_state.remove_model(model)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[PasteWidgetsFromClipboard]"
        for model_data in self._clipboard:
            s += f"\n\t{model_data}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        s += f"\n\tpasted IDs:\t\t{self._pasted_ids}"
        return s
