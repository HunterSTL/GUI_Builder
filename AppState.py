from collections.abc import Callable, Iterable

from model import ProjectDocument, BaseWidgetData
from utility import BoundingBox, compute_model_bounding_box


class AppState:
    """Applies project mutations and notifies subscribers of state changes."""
    def __init__(
        self,
        project_document: ProjectDocument
    ) -> None:
        self.project: ProjectDocument = project_document            #must only be mutated using AppState API (add_model, set_grid_visible, set_title...)

        #Persistent project state (survives across notifications)-------------------------------------------------------
        self._is_dirty: bool = False                                #signals whether unsaved changes exist

        #Transient change information (resets after each notification)--------------------------------------------------
        self._dirty_model_ids: set[str] = set()                     #IDs of models that changed
        self._removed_model_ids: set[str] = set()                   #IDs of models that were removed
        self.selection_change: bool = False                         #signals whether the selection outlines need to be re-rendered
        self.grid_change: bool = False                              #signals whether the grid needs to be re-rendered

        #Notification system--------------------------------------------------------------------------------------------
        self._subscribers: list[Callable[["AppState"], None]] = []  #functions that get called when any mutation happens
        self._batch_depth: int = 0                                  #keeps track of batch depth so only the outermost batch calls _notify (batches can be nested)
        self._pending_notify: bool = False                          #signals whether _notify will be called at the end of the batch

        #Model dictionary-----------------------------------------------------------------------------------------------
        self._model_by_id: dict[str, BaseWidgetData] = {}           #{model.id: model} for O(1) lookup; maintained in add_/remove_model()

        #Selection------------------------------------------------------------------------------------------------------
        self._selected_model_ids: list[str] = []                    #IDs of models in the order they were selected (newest is last)

        for model in self.project.widget_models:
            self._model_by_id[model.id] = model

    #Notification system------------------------------------------------------------------------------------------------
    def subscribe(
        self,
        function: Callable[["AppState"], None]
    ) -> None:
        """Subscribe a function to be called when the state changes."""
        if not callable(function):
            raise ValueError("AppState - subscription failed: subscriber must be callable")
        self._subscribers.append(function)

    def batch(
        self
    ) -> "_AppStateBatch":
        """Batch state change notifications so subscribers are notified once after the outermost batch exits."""
        return _AppStateBatch(self)

    def _notify(
        self
    ) -> None:
        """Notify all subscribers of state changes then reset transient change information."""
        if self._batch_depth > 0:
            self._pending_notify = True #defers notification to the outermost batch
            return

        for function in self._subscribers:
            function(self)

        self.selection_change = False
        self.grid_change = False
        self._dirty_model_ids.clear()
        self._removed_model_ids.clear()

    #Dirty state API----------------------------------------------------------------------------------------------------
    def is_dirty(
        self
    ) -> bool:
        """Return whether the project contains unsaved changes."""
        return self._is_dirty

    def mark_clean(
        self
    ) -> None:
        """Clear the dirty state and notify subscribers."""
        if not self._is_dirty:
            return

        self._is_dirty = False
        self._notify()

    #Model API----------------------------------------------------------------------------------------------------------
    def add_model(
        self,
        model: BaseWidgetData
    ) -> None:
        """Add a new model to the project document."""
        if not model.id:
            raise ValueError("AppState - model addition failed: missing ID")

        if model.id in self._model_by_id:
            raise ValueError(f"AppState - model addition failed: duplicate ID \"{model.id}\"")

        self.project.widget_models.append(model)
        self._model_by_id[model.id] = model
        self._dirty_model_ids.add(model.id)

        #select the created widget without notifying
        self._selected_model_ids = [model.id]
        self.selection_change = True

        self._mark_dirty()

    def remove_model(
        self,
        model: BaseWidgetData
    ) -> None:
        """Remove an existing model from the project document."""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model removal failed: unknown ID \"{model.id}\"")

        model = self.get_model_from_model_id(model.id)  #prevents removing a stale model
        self.project.widget_models.remove(model)
        self._model_by_id.pop(model.id, None)
        self._removed_model_ids.add(model.id)

        if model.id in self._selected_model_ids:
            self._selected_model_ids.remove(model.id)
            self.selection_change = True

        self._mark_dirty()

    def set_model_position(
        self,
        model: BaseWidgetData,
        x: int,
        y: int
    ) -> None:
        """Set the absolute position of a model."""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model position update failed: unknown ID \"{model.id}\"")

        model = self.get_model_from_model_id(model.id)  #prevents updating a stale model

        if model.x == x and model.y == y:
            return

        model.x = x
        model.y = y
        self._dirty_model_ids.add(model.id)
        self._mark_dirty()

    def offset_model_position(
        self,
        model: BaseWidgetData,
        dx: int,
        dy: int
    ) -> None:
        """Offset the model position by a delta."""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model position update failed: unknown ID \"{model.id}\"")

        model = self.get_model_from_model_id(model.id)  #prevents updating a stale model
        model.x += dx
        model.y += dy
        self._dirty_model_ids.add(model.id)
        self._mark_dirty()

    def set_model_attribute(
        self,
        model: BaseWidgetData,
        attribute: str,
        value: str | int
    ) -> None:
        """Set a model attribute to the given value."""
        if model.id not in self._model_by_id:
            raise ValueError(f"AppState - model attribute update failed: unknown ID \"{model.id}\"")

        model = self.get_model_from_model_id(model.id)  #prevents updating a stale model

        if not hasattr(model, attribute):
            raise ValueError(f"AppState - model attribute update failed: unknown attribute \"{attribute}\" [{model.id}]")

        if getattr(model, attribute) == value:
            return

        setattr(model, attribute, value)
        self._dirty_model_ids.add(model.id)
        self._mark_dirty()

    #Grid API-----------------------------------------------------------------------------------------------------------
    def set_grid_visible(
        self,
        visible: bool
    ) -> None:
        """Set the grid visibility."""
        if self.project.grid.visible == visible:
            return

        self.project.grid.visible = visible
        self.grid_change = True
        self._mark_dirty()

    def set_grid_size(
        self,
        size: int
    ) -> None:
        """Set the grid size."""
        if self.project.grid.size == size:
            return

        self.project.grid.size = size
        self.grid_change = True
        self._mark_dirty()

    def set_grid_color(
        self,
        color: str
    ) -> None:
        """Set the grid color."""
        if self.project.grid.color == color:
            return

        self.project.grid.color = color
        self.grid_change = True
        self._mark_dirty()

    #Project API--------------------------------------------------------------------------------------------------------
    def set_title(
        self,
        title: str
    ) -> None:
        """Set the project title."""
        if self.project.title == title:
            return

        self.project.title = title
        self._mark_dirty()

    #Selection API------------------------------------------------------------------------------------------------------
    def selection_clear(
        self
    ) -> None:
        """Clear the current selection."""
        if self.selection_is_empty():
            return

        self._selected_model_ids.clear()
        self._mark_selection_change()

    def selection_select_only(
        self,
        model_id: str
    ) -> None:
        """Replace the current selection with the given model ID."""
        if self._selected_model_ids == [model_id]:
            return

        self._selected_model_ids = [model_id]
        self._mark_selection_change()

    def selection_toggle(
        self,
        model_id: str
    ) -> None:
        """Add the given model ID to the selection or remove it if it's already selected."""
        if self.selection_contains(model_id):
            self._selected_model_ids.remove(model_id)
        else:
            self._selected_model_ids.append(model_id)

        self._mark_selection_change()

    def selection_select_all(
        self
    ) -> None:
        """Select all model IDs in the project document."""
        if self._selected_model_ids == [model.id for model in self.project.widget_models]:
            return

        self._selected_model_ids = [model.id for model in self.project.widget_models]
        self._mark_selection_change()

    def selection_handle_click(
        self,
        model_id: str,
        is_additive: bool
    ) -> None:
        """Apply additive or exclusive selection for the given model ID."""
        if model_id not in self._model_by_id:
            raise ValueError(f"AppState - model selection failed: unknown ID \"{model_id}\"")

        if is_additive:
            self.selection_toggle(model_id)
        else:
            if not self.selection_contains(model_id):
                self.selection_select_only(model_id)

    def apply_rectangle_selection(
        self,
        enclosed_model_ids: list[str],
        is_additive: bool
    ) -> None:
        """Apply additive or exclusive rectangle selection for the given enclosed model IDs."""
        if not is_additive:
            self.selection_clear()

        for model_id in enclosed_model_ids:
            if model_id not in self._selected_model_ids:
                self._selected_model_ids.append(model_id)
                self.selection_change = True

        self._notify()

    #Model query API----------------------------------------------------------------------------------------------------
    def get_model_from_model_id(
        self,
        model_id: str
    ) -> BaseWidgetData:
        """Return the model associated with the given model ID."""
        try:
            return self._model_by_id[model_id]
        except KeyError:
            raise ValueError(f"AppState - model lookup failed: unknown ID \"{model_id}\"")

    def get_dirty_models(
        self
    ) -> tuple[BaseWidgetData, ...]:
        """Return all dirty models."""
        return tuple(
            model
            for model in self.project.widget_models #iterates over all models for stable order
            if model.id in self._dirty_model_ids
        )

    def get_removed_model_ids(
        self
    ) -> frozenset[str]:
        """Return the IDs of removed models."""
        return frozenset(self._removed_model_ids)

    def get_all_models(
        self
    ) -> tuple[BaseWidgetData, ...]:
        """Return all models in the project document."""
        return tuple(self.project.widget_models)

    @staticmethod
    def get_model_bounding_box(
        model: BaseWidgetData
    ) -> BoundingBox:
        """Return the given model's bounding box."""
        if model is None:
            raise ValueError("AppState - model bounding box lookup failed: no model provided")

        return compute_model_bounding_box(model.x, model.y, model.width, model.height, model.anchor)

    def get_model_group_bounding_box(
        self,
        models: Iterable[BaseWidgetData]
    ) -> BoundingBox:
        """Return the collective bounding box of all given models."""
        models = tuple(models)

        if not models:
            raise ValueError("AppState - model group bounding box lookup failed: no models provided")

        first_model = models[0]
        bounding_box = self.get_model_bounding_box(first_model)

        left = bounding_box.left
        top = bounding_box.top
        right = bounding_box.right
        bottom = bounding_box.bottom

        for model in models[1:]:    #skips the first model
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
    def selection_is_empty(
        self
    ) -> bool:
        """Return whether the selection is empty."""
        return len(self._selected_model_ids) == 0

    def selection_contains(
        self,
        model_id: str
    ) -> bool:
        """Return whether the selection contains the given model ID."""
        return model_id in self._selected_model_ids

    def get_selected_models(
        self
    ) -> tuple[BaseWidgetData, ...]:
        """Return the selected models in selection order."""
        return tuple(
            self.get_model_from_model_id(model_id)
            for model_id in self._selected_model_ids
        )

    def get_last_selected_model_id(
        self
    ) -> str | None:
        """Return the ID of the last selected model or None when the selection is empty."""
        if not self._selected_model_ids:
            return None
        return self._selected_model_ids[-1]

    #Internals----------------------------------------------------------------------------------------------------------
    def _mark_dirty(
        self
    ) -> None:
        self._is_dirty = True
        self._notify()

    def _mark_selection_change(
        self
    ) -> None:
        self.selection_change = True
        self._notify()


# noinspection PyProtectedMember
class _AppStateBatch:
    """Coalesces multiple AppState mutations into a single state change notification."""
    def __init__(
        self,
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

    def __enter__(
        self
    ) -> None:
        self._app_state._batch_depth += 1

    def __exit__(
        self,
        exc_type: object | None,
        exc_val: object | None,
        exc_tb: object | None
    ) -> bool:
        state = self._app_state
        state._batch_depth -= 1

        if state._batch_depth == 0 and state._pending_notify:
            state._pending_notify = False
            state._notify()

        return False    #propagates exceptions
