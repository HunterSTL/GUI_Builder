from _dataclasses import ProjectDocument, SelectionState
from CallTracer import call_tracer

class AppState:
    """AppState is the central place where all model state changes happen"""
    def __init__(
        self,
        project_document: ProjectDocument
    ):
        self.project = project_document
        self.selection = SelectionState()

        self._listeners = []                    #functions that get called when any mutation happens

        self._batch_depth = 0                   #keeps track of batch depth so only the outer most batch calls _notify (batches can be nested)
        self._pending_notify = False            #signals whether _notify will be called at the end of the batch

        self.dirty_model_ids: set[str] = set()  #holds the ids of models that changed
        self.structural_change = False          #signals whether a full re-render is necessary
        self.selection_change = False           #signals whether the selection outlines need to be redrawn

    #State change notifications-----------------------------------------------------------------------------------------
    def subscribe(self, function):
        """register a listener"""
        if not callable(function):
            raise TypeError("listener must be callable")
        self._listeners.append(function)

    def _notify(self):
        """notify all listeners"""
        if self._batch_depth > 0:
            #don't call the listeners if called while batching (with batch():)
            #instead set flag to notify once batching is complete
            self._pending_notify = True
            return

        for function in self._listeners:
            function(self)

        #reset flags and clear dirty models after all listeners have been called
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
                return False #propagate exceptions so notify → re-render doen't happen on exceptions

        return _Batch(self)
    #Widgets------------------------------------------------------------------------------------------------------------
    def add_widget(self, model):
        """append a new widget model to the ProjectDocument"""
        self.project.widget_models.append(model)
        self.structural_change = True
        self._notify()

    def remove_widget(self, model):
        """remove an existing widget model from the ProjectDocument"""
        try:
            self.project.widget_models.remove(model)
            self.structural_change = True
            self._notify()
        except ValueError:
            pass

    def move_widget_to(self, model, x: int, y: int):
        """set absolute model coordinates"""
        call_tracer.log_event(f"move widget {model.id} to {x}|{y}")
        model.x = x
        model.y = y
        self.dirty_model_ids.add(model.id)
        self._notify()

    def move_widget_by(self, model, dx: int, dy: int):
        """update model coordinates by a delta"""
        call_tracer.log_event(f"move widget {model.id} by {dx}|{dy}")
        model.x += dx
        model.y += dy
        self.dirty_model_ids.add(model.id)
        self._notify()

    def set_widget_attribute(self, model, attribute, value):
        """set a model attribute to value if present"""
        call_tracer.log_event(f"set {model.id} attribute {attribute} to value {value}")
        if hasattr(model, attribute):
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
        """clear all selected models and notify listeners"""
        if self.selection.selected_models:
            self.selection = SelectionState()   #simple reset
            self.selection_change = True        #forces redraw of selection outlines
            self._notify()

    def selection_select_only(self, model_id: str):
        """replace the current selection with the given model and notify listeners"""
        if model_id is None:
            return

        self.selection.selected_models = {model_id}
        self.selection.last_selected_model = model_id
        self.selection_change = True
        self._notify()

    def selection_toggle(self, model_id: str):
        """add the given model to the selection or remove it if it's already selected and notify listeners"""
        if model_id is None:
            return

        if model_id in self.selection.selected_models:      #already selected → remove from selection
            self.selection.selected_models.remove(model_id)
            if self.selection.last_selected_model == model_id:
                self.selection.last_selected_model = None
        else:                                               #not yet selected → add to selection
            self.selection.selected_models.add(model_id)
            self.selection.last_selected_model = model_id

        self.selection_change = True
        self._notify()

    def selection_handle_click(self, model_id: str, is_additive: bool):
        """toggle the model if selection is additive, otherwise replace selection with the given model"""
        if is_additive:
            self.selection_toggle(model_id)
        else:
            if model_id not in self.selection.selected_models:
                self.selection_select_only(model_id)

    def selection_select_all(self):
        """select all widget models in the project_document"""
        self.selection.selected_models = {model.id for model in self.project.widget_models}

        if self.selection.selected_models:
            self.selection.last_selected_model = next(iter(self.selection.selected_models))
        else:
            self.selection.last_selected_model = None

        self.selection_change = True
        self._notify()

    #Selection helpers--------------------------------------------------------------------------------------------------
    def selection_currently_selected(self):
        return frozenset(self.selection.selected_models)

    def selection_last_selected(self):
        return self.selection.last_selected_model

    def selection_is_empty(self):
        return len(self.selection.selected_models) == 0

    def selection_contains(self, model_id: str):
        return model_id in self.selection.selected_models

    #Rectangle selection------------------------------------------------------------------------------------------------
    def apply_rectangle_selection(self, encosed_model_ids: set[str], is_additive):
        """
        finalize a rectangle selection gesture
            -if additive: add enclosed model to selection
            -if not additive: replace selection entirely
        resets transient rectangle state and notifies listeners once.
        """
        if not is_additive:
            #replace current selection if not additive
            self.selection = SelectionState()

        for model_id in encosed_model_ids:  #add models to selection if they are not already selected
            if model_id not in self.selection.selected_models:
                self.selection.selected_models.add(model_id)
                self.selection.last_selected_model = model_id
                self.selection_change = True

        self._notify()