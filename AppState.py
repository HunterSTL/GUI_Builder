from typing import Iterable
from model import ProjectDocument, SelectionState, BaseWidgetData
from utility import call_tracer, BoundingBox, compute_model_bounding_box

class AppState:
    """AppState is the central place where all model state changes happen"""
    def __init__(
        self,
        project_document: ProjectDocument
    ):
        self.project = project_document         #must only be mutated using AppState API (add_widget, set_grid_visible, set_title...)
        self.selection = SelectionState()

        #State change notifications-------------------------------------------------------------------------------------
        self._subscribers = []                  #functions that get called when any mutation happens
        self.dirty_model_ids: set[str] = set()  #holds the IDs of models that changed
        self.structural_change = False          #signals whether a full re-render is necessary
        self.selection_change = False           #signals whether the selection outlines need to be redrawn

        #Batching-------------------------------------------------------------------------------------------------------
        self._batch_depth = 0                   #keeps track of batch depth so only the outer most batch calls _notify (batches can be nested)
        self._pending_notify = False            #signals whether _notify will be called at the end of the batch

        #Model dictionary-----------------------------------------------------------------------------------------------
        self._model_by_id = {}                  #{model.id: model} for O(1) lookup; maintained in add_/remove_widget()

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
            #don't call the subscribers if called while batching (with batch():)
            #instead set flag to notify once batching is complete
            self._pending_notify = True
            return

        for function in self._subscribers:
            function(self)

        #reset flags and clear dirty models after all subscribers have been called
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
    #Widgets------------------------------------------------------------------------------------------------------------
    def add_widget(self, model):
        """append a new widget model to the ProjectDocument"""
        if not model.id:
            raise ValueError("AppState - model addition failed: missing ID")

        if model.id in self._model_by_id:
            raise ValueError(f"AppState - model addition failed: duplicate ID \"{model.id}\"")

        self._model_by_id[model.id] = model
        self.project.widget_models.append(model)
        self.structural_change = True
        self._notify()

    def remove_widget(self, model):
        """remove an existing widget model from the ProjectDocument"""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model removal failed: unknown ID \"{model.id}\"")

        self._model_by_id.pop(model.id, None)
        self.project.widget_models.remove(model)
        self.structural_change = True
        self._notify()

    def move_widget_to(self, model, x: int, y: int):
        """set absolute model coordinates"""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model position update failed: unknown ID \"{model.id}\"")

        model.x = x
        model.y = y
        self.dirty_model_ids.add(model.id)
        self._notify()

    def move_widget_by(self, model, dx: int, dy: int):
        """update model coordinates by a delta"""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model position update failed: unknown ID \"{model.id}\"")

        model.x += dx
        model.y += dy
        self.dirty_model_ids.add(model.id)
        self._notify()

    def set_widget_attribute(self, model, attribute, value):
        """set a model attribute to value if present"""
        if not hasattr(model, attribute):
            raise ValueError(f"AppState - model attribute update failed: unknown attribute \"{attribute}\" [{model.id}]")

        setattr(model, attribute, value)
        self.dirty_model_ids.add(model.id)
        self._notify()

    #Grid/Project-------------------------------------------------------------------------------------------------------
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

    def set_title(self, title: str):
        self.project.title = title
        self._notify()

    #Selection----------------------------------------------------------------------------------------------------------
    def selection_clear(self):
        """clear all selected models and notify subscribers"""
        if not self.selection_is_empty():
            self._clear_selection_state()
            self.selection_change = True        #forces redraw of selection outlines
            self._notify()

    def selection_select_only(self, model_id: str):
        """replace the current selection with the given model and notify subscribers"""
        self.selection.selected_models = {model_id}
        self.selection.last_selected_model = model_id
        self.selection_change = True
        self._notify()

    def selection_toggle(self, model_id: str):
        """add the given model to the selection or remove it if it's already selected and notify subscribers"""
        if self.selection_contains(model_id):   #already selected → remove from selection
            self.selection.selected_models.remove(model_id)
            if self.selection.last_selected_model == model_id:
                self.selection.last_selected_model = None
        else:                                   #not yet selected → add to selection
            self.selection.selected_models.add(model_id)
            self.selection.last_selected_model = model_id

        self.selection_change = True
        self._notify()

    def selection_handle_click(self, model_id: str, is_additive: bool):
        """toggle the model if selection is additive, otherwise replace selection with the given model"""
        if model_id not in self._model_by_id:
            raise ValueError(f"AppState - selection update failed: unknown ID \"{model_id}\"")

        if is_additive:
            self.selection_toggle(model_id)
        else:
            if not self.selection_contains(model_id):
                self.selection_select_only(model_id)

    def selection_select_all(self):
        """select all widget models in the project_document"""
        self.selection.selected_models = {model.id for model in self.project.widget_models}

        if not self.selection_is_empty():
            self.selection.last_selected_model = next(iter(self.selection.selected_models))
        else:
            self.selection.last_selected_model = None

        self.selection_change = True
        self._notify()

    def _clear_selection_state(self):
        self.selection.selected_models.clear()
        self.selection.last_selected_model = None

    #Rectangle selection------------------------------------------------------------------------------------------------
    def apply_rectangle_selection(self, enclosed_model_ids: set[str], is_additive):
        """
        finalize a rectangle selection gesture and notify subscribers
            -if additive: add enclosed model to selection
            -if not additive: replace selection entirely
        """
        if not is_additive:
            self._clear_selection_state()
            self.selection_change = True

        for model_id in enclosed_model_ids: #add models to selection if they are not already selected
            if model_id not in self.selection.selected_models:
                self.selection.selected_models.add(model_id)
                self.selection.last_selected_model = model_id
                self.selection_change = True

        self._notify()

    #Model helpers------------------------------------------------------------------------------------------------------
    def get_model_from_model_id(self, model_id: str) -> BaseWidgetData:
        """return the model associated with the given model_id"""
        try:
            return self._model_by_id[model_id]
        except KeyError:
            raise ValueError(f"AppState - model lookup failed: unknown ID \"{model_id}\"")

    def get_model_coordinates_from_model_id(self, model_id: str) -> tuple[int, int]:
        """return the X- and Y-coordinate of the model"""
        model = self.get_model_from_model_id(model_id)
        return model.x, model.y

    def get_model_bounding_box_from_model_id(self, model_id: str) -> BoundingBox:
        """return the model's bounding box"""
        model = self.get_model_from_model_id(model_id)
        return compute_model_bounding_box(model.x, model.y, model.width, model.height, model.anchor)

    def get_model_bounding_box_from_model_ids(self, model_ids: Iterable[str]) -> BoundingBox:
        """return the collective bounding box of all given models"""
        first_model_id = next(iter(model_ids))
        first_model_bounding_box = self.get_model_bounding_box_from_model_id(first_model_id)
        left = first_model_bounding_box.left
        top = first_model_bounding_box.top
        right = first_model_bounding_box.right
        bottom = first_model_bounding_box.bottom

        for model_id in model_ids:
            if model_id == first_model_id:
                continue

            model_bounding_box = self.get_model_bounding_box_from_model_id(model_id)
            left = min(left, model_bounding_box.left)
            top = min(top, model_bounding_box.top)
            right = max(right, model_bounding_box.right)
            bottom = max(bottom, model_bounding_box.bottom)

        return BoundingBox(
            left=left,
            top=top,
            right=right,
            bottom=bottom
        )

    #Selection helpers--------------------------------------------------------------------------------------------------
    def selection_currently_selected(self) -> frozenset[str]:
        return frozenset(self.selection.selected_models)

    def selection_last_selected(self) -> str:
        return self.selection.last_selected_model

    def selection_is_empty(self) -> bool:
        return len(self.selection.selected_models) == 0

    def selection_contains(self, model_id: str) -> bool:
        return model_id in self.selection.selected_models
