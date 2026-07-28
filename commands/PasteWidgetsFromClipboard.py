import copy
from model import BaseWidgetData
from .BaseCommand import Command
from utility import clamped_delta
from AppState import AppState

class PasteWidgetsFromClipboard(Command):
    def __init__(
        self,
        clipboard: list[dict],
        dx: int,
        dy: int,
        app_state: AppState
    ) -> None:
        """snapshot the current clipboard data and movement delta"""
        self._clipboard = copy.deepcopy(clipboard)
        self._dx = dx
        self._dy = dy
        self._app_state = app_state

        self._first_execution = True
        self._pasted_ids = []   #populated on first execution, reused on redo

    def execute(self) -> None:
        """create, position, add and select widget models from the snapshotted clipboard data"""
        created_models: list[BaseWidgetData] = []

        #create models from clipboard data
        for i, model_data in enumerate(self._clipboard):
            model = BaseWidgetData.from_dict(model_data)
            created_models.append(model)

            #only create an ID during the first execution (subsequent redos reuse the same IDs)
            if self._first_execution:
                model.id = self._app_state.project.id_counters.generate_id(model.type)
                self._pasted_ids.append(model.id)
            else:
                model.id = self._pasted_ids[i]

        #compute offset by clamping the delta
        x_offset, y_offset = clamped_delta(
            canvas_width=self._app_state.project.width,
            canvas_height=self._app_state.project.height,
            bounding_box=self._app_state.get_model_group_bounding_box(created_models),
            dx=self._dx,
            dy=self._dy
        )

        #offset model positions
        for model in created_models:
            model.x += x_offset     #models can be safely edited because they are not yet owned by AppState
            model.y += y_offset

        #add created models to AppState and select them
        with self._app_state.batch():
            for model in created_models:
                self._app_state.add_model(model)    #selects only the added model

            #rebuild selection
            self._app_state.selection_clear()
            for model in created_models:
                self._app_state.selection_toggle(model.id)

        self._first_execution = False

    def undo(self) -> None:
        """remove all widget models created from the snapshot"""
        with self._app_state.batch():
            for pasted_id in self._pasted_ids:
                model = self._app_state.get_model_from_model_id(pasted_id)
                self._app_state.remove_model(model)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[PasteWidgetsFromClipboard]"
        for model_data in self._clipboard:
            s += f"\n\t{model_data}"
        s += f"\n\tdx|dy:\t\t\t\t{self._dx}|{self._dy}"
        s += f"\n\tpasted IDs:\t\t{self._pasted_ids}"
        return s
