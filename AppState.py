from _dataclasses import ProjectDocument
from CallTracer import call_tracer

class AppState:
    """AppState is the central place where all model state changes happen"""
    def __init__(
        self,
        project_document: ProjectDocument
    ):
        self.project = project_document

        self._listeners = []                    #functions that get called when any mutation happens

        self._batch_depth = 0                   #keeps track of batch depth so only the outer most batch calls _notify (batches can be nested)
        self._pending_notify = False            #signals whether _notify will be called at the end of the batch

        self.dirty_model_ids: set[str] = set()  #holds the ids of models that changed
        self.structural_change = False          #signals whether a full re-render is necessary

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

        #reset flag and clear dirty models after all listeners have been called
        self.structural_change = False
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