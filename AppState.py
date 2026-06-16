from collections.abc import Iterable
from model import ProjectDocument, SelectionState, BaseWidgetData
from utility import call_tracer, BoundingBox, compute_model_bounding_box

class AppState:
    """AppState is the central place where all model state changes happen"""
    def __init__(
        self,
        project_document: ProjectDocument
    ):
        self.project = project_document         #must only be mutated using AppState API (add_model, set_grid_visible, set_title...)
        self._selection = SelectionState()

        #State change notifications-------------------------------------------------------------------------------------
        self._subscribers = []                  #functions that get called when any mutation happens
        self.dirty_model_ids: set[str] = set()  #holds the IDs of models that changed
        self.structural_change = False          #signals whether a full re-render is necessary
        self.selection_change = False           #signals whether the selection outlines need to be redrawn

        #Batching-------------------------------------------------------------------------------------------------------
        self._batch_depth = 0                   #keeps track of batch depth so only the outer most batch calls _notify (batches can be nested)
        self._pending_notify = False            #signals whether _notify will be called at the end of the batch

        #Model dictionary-----------------------------------------------------------------------------------------------
        self._model_by_id = {}                  #{model.id: model} for O(1) lookup; maintained in add_/remove_model()

        #add existing models in ProjectDocument to the dictionary
        for model in self.project.widget_models:
            self._model_by_id[model.id] = model

    #State change notifications-----------------------------------------------------------------------------------------
    def subscribe(self, function):
        """register a function to be called when the state changes"""
        if not callable(function):
            raise ValueError("AppState - subscription failed: subscriber must be callable")
        self._subscribers.append(function)

    def _notify(self):
        """notify all subscribers"""
        if self._batch_depth > 0:
            self._pending_notify = True #defers notification to the outer most batch
            return

        for function in self._subscribers:
            function(self)

        #reset flags and clear dirty model IDs after all subscribers have been called
        self.structural_change = False
        self.selection_change = False
        self.dirty_model_ids.clear()

    def batch(self):
        class _Batch:
            def __init__(self, state: AppState):
                self._state = state

            def __enter__(self):
                self._state._batch_depth += 1

            def __exit__(self, exc_type, exc_val, exc_tb):
                state = self._state
                state._batch_depth -= 1

                if state._batch_depth == 0 and state._pending_notify:
                    state._pending_notify = False
                    state._notify()
                return False #propagate exceptions so notify → re-render doesn't happen on exceptions

        return _Batch(self)

    #Model API----------------------------------------------------------------------------------------------------------
    def add_model(self, model):
        """append a new model to the ProjectDocument"""
        if not model.id:
            raise ValueError("AppState - model addition failed: missing ID")

        if model.id in self._model_by_id:
            raise ValueError(f"AppState - model addition failed: duplicate ID \"{model.id}\"")

        self._model_by_id[model.id] = model
        self.project.widget_models.append(model)
        self.structural_change = True
        self._notify()

    def remove_model(self, model):
        """remove an existing model from the ProjectDocument"""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model removal failed: unknown ID \"{model.id}\"")

        self._model_by_id.pop(model.id, None)
        self.project.widget_models.remove(model)
        self.structural_change = True
        self._notify()

    def set_model_position(self, model, x: int, y: int):
        """set absolute model position"""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model position update failed: unknown ID \"{model.id}\"")

        model.x = x
        model.y = y
        self.dirty_model_ids.add(model.id)
        self._notify()

    def offset_model_position(self, model, dx: int, dy: int):
        """offset model position by a delta"""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model position update failed: unknown ID \"{model.id}\"")

        model.x += dx
        model.y += dy
        self.dirty_model_ids.add(model.id)
        self._notify()

    def set_model_attribute(self, model, attribute, value):
        """set a model attribute to value if present"""
        if not hasattr(model, attribute):
            raise ValueError(f"AppState - model attribute update failed: unknown attribute \"{attribute}\" [{model.id}]")

        setattr(model, attribute, value)
        self.dirty_model_ids.add(model.id)
        self._notify()

    #Grid API-----------------------------------------------------------------------------------------------------------
    def set_grid_visible(self, visible: bool):
        self.project.grid.visible = visible
        self.structural_change = True
        self._notify()

    def set_grid_size(self, size: int):
        self.project.grid.size = size
        self.structural_change = True
        self._notify()

    def set_grid_color(self, color: str):
        self.project.grid.color = color
        self.structural_change = True
        self._notify()

    #Project API--------------------------------------------------------------------------------------------------------
    def set_title(self, title: str):
        self.project.title = title
        self._notify()

    #Selection API------------------------------------------------------------------------------------------------------
    def selection_clear(self):
        """clear all selected model IDs then notify subscribers"""
        if not self.selection_is_empty():
            self._clear_selection_state()
            self.selection_change = True        #forces redraw of selection outlines
            self._notify()

    def selection_select_only(self, model_id: str):
        """replace the current selection with the given model ID then notify subscribers"""
        self._selection.selected_model_ids = {model_id}
        self._selection.last_selected_model_id = model_id
        self.selection_change = True
        self._notify()

    def selection_toggle(self, model_id: str):
        """add the given model ID to the selection or remove it if it's already selected then notify subscribers"""
        if self.selection_contains(model_id):   #already selected → remove from selection
            self._selection.selected_model_ids.remove(model_id)
            if self._selection.last_selected_model_id == model_id:
                self._selection.last_selected_model_id = None
        else:                                   #not yet selected → add to selection
            self._selection.selected_model_ids.add(model_id)
            self._selection.last_selected_model_id = model_id

        self.selection_change = True
        self._notify()

    def selection_select_all(self):
        """select all model IDs in the ProjectDocument then notify subscribers"""
        self._selection.selected_model_ids = {model.id for model in self.project.widget_models}

        if not self.selection_is_empty():
            self._selection.last_selected_model_id = next(iter(self._selection.selected_model_ids))
        else:
            self._selection.last_selected_model_id = None

        self.selection_change = True
        self._notify()

    def selection_handle_click(self, model_id: str, is_additive: bool):
        """toggle the selection for the given model ID if selection is additive, otherwise select only that model ID"""
        if model_id not in self._model_by_id:
            raise ValueError(f"AppState - selection update failed: unknown ID \"{model_id}\"")

        if is_additive:
            self.selection_toggle(model_id)
        else:
            if not self.selection_contains(model_id):
                self.selection_select_only(model_id)

    def apply_rectangle_selection(self, enclosed_model_ids: set[str], is_additive):
        """add model IDs of enclosed widgets to selection if selection is additive, otherwise replace selection entirely, then notify subscribers"""
        if not is_additive:
            self._clear_selection_state()
            self.selection_change = True

        for model_id in enclosed_model_ids: #add models to selection if they are not already selected
            if model_id not in self._selection.selected_model_ids:
                self._selection.selected_model_ids.add(model_id)
                self._selection.last_selected_model_id = model_id
                self.selection_change = True

        self._notify()

    #Model query API----------------------------------------------------------------------------------------------------
    def get_model_from_model_id(self, model_id: str) -> BaseWidgetData:
        """return the model associated with the given model ID"""
        try:
            return self._model_by_id[model_id]
        except KeyError:
            raise ValueError(f"AppState - model lookup failed: unknown ID \"{model_id}\"")

    def get_model_coordinates_from_model_id(self, model_id: str) -> tuple[int, int]:
        """return the model's position (x and y)"""
        model = self.get_model_from_model_id(model_id)
        return model.x, model.y

    def get_model_bounding_box_from_model_id(self, model_id: str) -> BoundingBox:
        """return the model's bounding box"""
        model = self.get_model_from_model_id(model_id)
        return self.get_model_bounding_box(model)

    def get_model_bounding_box_from_model_ids(self, model_ids: Iterable[str]) -> BoundingBox:
        """return the collective bounding box of all given models"""
        models = tuple(
            self.get_model_from_model_id(model_id)
            for model_id in model_ids
        )
        return self.get_model_group_bounding_box(models)

    def get_dirty_models(self) -> tuple[BaseWidgetData, ...]:
        """return all dirty models"""
        return tuple(
            model
            for model in self.project.widget_models #iterate all models for stable order
            if model.id in self.dirty_model_ids
        )

    def get_all_models(self) -> tuple[BaseWidgetData, ...]:
        """return all models in the ProjectDocument"""
        return tuple(self.project.widget_models)

    @staticmethod
    def get_model_bounding_box(model: BaseWidgetData) -> BoundingBox:
        """return the model's bounding box"""
        if model is None:
            raise ValueError("AppState - model bounding box lookup failed: no model provided")

        return compute_model_bounding_box(model.x, model.y, model.width, model.height, model.anchor)

    def get_model_group_bounding_box(self, models: Iterable[BaseWidgetData]) -> BoundingBox:
        """return the collective bounding box of all given models"""
        models = tuple(models)

        if not models:
            raise ValueError("AppState - model group bounding box lookup failed: no models provided")

        first_model = models[0]
        bounding_box = self.get_model_bounding_box(first_model)

        left = bounding_box.left
        top = bounding_box.top
        right = bounding_box.right
        bottom = bounding_box.bottom

        for model in models[1:]:    #skip first model
            bounding_box = self.get_model_bounding_box(model)
            left = min(left, bounding_box.left)
            top = min(top, bounding_box.top)
            right = max(right, bounding_box.right)
            bottom = max(bottom, bounding_box.bottom)

        return BoundingBox(
            left=left,
            top=top,
            right=right,
            bottom=bottom
        )

    #Selection query API------------------------------------------------------------------------------------------------
    def selection_currently_selected(self) -> frozenset[str]:
        return self.get_selected_model_ids()

    def selection_last_selected(self) -> str | None:
        return self.get_last_selected_model_id()

    def selection_is_empty(self) -> bool:
        return len(self._selection.selected_model_ids) == 0

    def selection_contains(self, model_id: str) -> bool:
        return model_id in self._selection.selected_model_ids

    def get_selected_models(self) -> tuple[BaseWidgetData, ...]:
        return tuple(
            model
            for model in self.project.widget_models #iterate all models for stable order
            if model.id in self._selection.selected_model_ids
        )

    def get_selected_model_ids(self) -> frozenset[str]:
        return frozenset(self._selection.selected_model_ids)

    def get_last_selected_model(self) -> BaseWidgetData | None:
        last_selected_model_id = self._selection.last_selected_model_id
        if last_selected_model_id is None:
            return None
        return self.get_model_from_model_id(last_selected_model_id)

    def get_last_selected_model_id(self) -> str | None:
        return self._selection.last_selected_model_id

    #Internals----------------------------------------------------------------------------------------------------------
    def _clear_selection_state(self):
        self._selection.selected_model_ids.clear()
        self._selection.last_selected_model_id = None
