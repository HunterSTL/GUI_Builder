from collections.abc import Callable, Iterable

from model import ProjectDocument, BaseWidget
from utility import BoundingBox, compute_widget_bounding_box


class AppState:
    """Applies project mutations and notifies subscribers of state changes."""
    def __init__(
        self,
        project_document: ProjectDocument
    ) -> None:
        self.project: ProjectDocument = project_document            #must only be mutated using AppState API (add_widget, set_grid_visible, set_title...)

        #Persistent project state (survives across notifications)-------------------------------------------------------
        self._is_dirty: bool = False                                #signals whether unsaved changes exist

        #Transient change information (resets after each notification)--------------------------------------------------
        self._dirty_widget_ids: set[str] = set()                    #IDs of widgets that changed
        self._removed_widget_ids: set[str] = set()                  #IDs of widgets that were removed
        self.selection_change: bool = False                         #signals whether the selection outlines need to be re-rendered
        self.grid_change: bool = False                              #signals whether the grid needs to be re-rendered

        #Notification system--------------------------------------------------------------------------------------------
        self._subscribers: list[Callable[["AppState"], None]] = []  #functions that get called when any mutation happens
        self._batch_depth: int = 0                                  #keeps track of batch depth so only the outermost batch calls _notify (batches can be nested)
        self._pending_notify: bool = False                          #signals whether _notify will be called at the end of the batch

        #Widget dictionary----------------------------------------------------------------------------------------------
        self._widget_by_id: dict[str, BaseWidget] = {}              #{widget.id: widget} for O(1) lookup; maintained in add_/remove_widget()

        #Selection------------------------------------------------------------------------------------------------------
        self._selected_widget_ids: list[str] = []                   #IDs of widgets in the order they were selected (newest is last)

        for widget in self.project.widgets:
            self._widget_by_id[widget.id] = widget

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
        self._dirty_widget_ids.clear()
        self._removed_widget_ids.clear()

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

    #Widget API---------------------------------------------------------------------------------------------------------
    def add_widget(
        self,
        widget: BaseWidget
    ) -> None:
        """Add a new widget to the project document."""
        if not widget.id:
            raise ValueError("AppState - widget addition failed: missing widget ID")

        if widget.id in self._widget_by_id:
            raise ValueError(f"AppState - widget addition failed: duplicate widget ID \"{widget.id}\"")

        self.project.widgets.append(widget)
        self._widget_by_id[widget.id] = widget
        self._dirty_widget_ids.add(widget.id)

        #select the created widget without notifying
        self._selected_widget_ids = [widget.id]
        self.selection_change = True

        self._mark_dirty()

    def remove_widget(
        self,
        widget: BaseWidget
    ) -> None:
        """Remove an existing widget from the project document."""
        if widget.id not in self._widget_by_id:
            raise ValueError(f"AppState - widget removal failed: unknown widget ID \"{widget.id}\"")

        widget = self.get_widget_from_widget_id(widget.id)  #prevents removing a stale widget
        self.project.widgets.remove(widget)
        self._widget_by_id.pop(widget.id, None)
        self._removed_widget_ids.add(widget.id)

        if widget.id in self._selected_widget_ids:
            self._selected_widget_ids.remove(widget.id)
            self.selection_change = True

        self._mark_dirty()

    def set_widget_position(
        self,
        widget: BaseWidget,
        x: int,
        y: int
    ) -> None:
        """Set the absolute position of a widget."""
        if widget.id not in self._widget_by_id:
            raise ValueError(f"AppState - widget position update failed: unknown widget ID \"{widget.id}\"")

        widget = self.get_widget_from_widget_id(widget.id)  #prevents updating a stale widget

        if widget.x == x and widget.y == y:
            return

        widget.x = x
        widget.y = y
        self._dirty_widget_ids.add(widget.id)
        self._mark_dirty()

    def offset_widget_position(
        self,
        widget: BaseWidget,
        dx: int,
        dy: int
    ) -> None:
        """Offset the widget position by a delta."""
        if widget.id not in self._widget_by_id:
            raise ValueError(f"AppState - widget position update failed: unknown widget ID \"{widget.id}\"")

        widget = self.get_widget_from_widget_id(widget.id)  #prevents updating a stale widget
        widget.x += dx
        widget.y += dy
        self._dirty_widget_ids.add(widget.id)
        self._mark_dirty()

    def set_widget_attribute(
        self,
        widget: BaseWidget,
        attribute: str,
        value: str | int
    ) -> None:
        """Set a widget attribute to the given value."""
        if widget.id not in self._widget_by_id:
            raise ValueError(f"AppState - widget attribute update failed: unknown widget ID \"{widget.id}\"")

        widget = self.get_widget_from_widget_id(widget.id)  #prevents updating a stale widget

        if not hasattr(widget, attribute):
            raise ValueError(f"AppState - widget attribute update failed: unknown attribute \"{attribute}\" [{widget.id}]")

        if getattr(widget, attribute) == value:
            return

        setattr(widget, attribute, value)
        self._dirty_widget_ids.add(widget.id)
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

        self._selected_widget_ids.clear()
        self._mark_selection_change()

    def selection_select_only(
        self,
        widget_id: str
    ) -> None:
        """Replace the current selection with the given widget ID."""
        if self._selected_widget_ids == [widget_id]:
            return

        self._selected_widget_ids = [widget_id]
        self._mark_selection_change()

    def selection_toggle(
        self,
        widget_id: str
    ) -> None:
        """Add the given widget ID to the selection or remove it if it's already selected."""
        if self.selection_contains(widget_id):
            self._selected_widget_ids.remove(widget_id)
        else:
            self._selected_widget_ids.append(widget_id)

        self._mark_selection_change()

    def selection_select_all(
        self
    ) -> None:
        """Select all widget IDs in the project document."""
        if self._selected_widget_ids == [widget.id for widget in self.project.widgets]:
            return

        self._selected_widget_ids = [widget.id for widget in self.project.widgets]
        self._mark_selection_change()

    def selection_handle_click(
        self,
        widget_id: str,
        is_additive: bool
    ) -> None:
        """Apply additive or exclusive selection for the given widget ID."""
        if widget_id not in self._widget_by_id:
            raise ValueError(f"AppState - widget selection failed: unknown widget ID \"{widget_id}\"")

        if is_additive:
            self.selection_toggle(widget_id)
        else:
            if not self.selection_contains(widget_id):
                self.selection_select_only(widget_id)

    def apply_rectangle_selection(
        self,
        enclosed_widget_ids: list[str],
        is_additive: bool
    ) -> None:
        """Apply additive or exclusive rectangle selection for the given enclosed widget IDs."""
        if not is_additive:
            self.selection_clear()

        for widget_id in enclosed_widget_ids:
            if widget_id not in self._selected_widget_ids:
                self._selected_widget_ids.append(widget_id)
                self.selection_change = True

        self._notify()

    #Widget query API----------------------------------------------------------------------------------------------------
    def get_widget_from_widget_id(
        self,
        widget_id: str
    ) -> BaseWidget:
        """Return the widget associated with the given widget ID."""
        try:
            return self._widget_by_id[widget_id]
        except KeyError:
            raise ValueError(f"AppState - widget lookup failed: unknown widget ID \"{widget_id}\"")

    def get_dirty_widgets(
        self
    ) -> tuple[BaseWidget, ...]:
        """Return all dirty widgets."""
        return tuple(
            widget
            for widget in self.project.widgets  #iterates over all widgets for stable order
            if widget.id in self._dirty_widget_ids
        )

    def get_removed_widget_ids(
        self
    ) -> frozenset[str]:
        """Return the IDs of removed widgets."""
        return frozenset(self._removed_widget_ids)

    def get_all_widgets(
        self
    ) -> tuple[BaseWidget, ...]:
        """Return all widgets in the project document."""
        return tuple(self.project.widgets)

    @staticmethod
    def get_widget_bounding_box(
        widget: BaseWidget
    ) -> BoundingBox:
        """Return the given widget's bounding box."""
        if widget is None:
            raise ValueError("AppState - widget bounding box lookup failed: no widget provided")

        return compute_widget_bounding_box(widget.x, widget.y, widget.width, widget.height, widget.anchor)

    def get_widget_group_bounding_box(
        self,
        widgets: Iterable[BaseWidget]
    ) -> BoundingBox:
        """Return the collective bounding box of all given widgets."""
        widgets = tuple(widgets)

        if not widgets:
            raise ValueError("AppState - widget group bounding box lookup failed: no widgets provided")

        first_widget = widgets[0]
        bounding_box = self.get_widget_bounding_box(first_widget)

        left = bounding_box.left
        top = bounding_box.top
        right = bounding_box.right
        bottom = bounding_box.bottom

        for widget in widgets[1:]:  #skips the first widget
            bounding_box = self.get_widget_bounding_box(widget)
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
        return len(self._selected_widget_ids) == 0

    def selection_contains(
        self,
        widget_id: str
    ) -> bool:
        """Return whether the selection contains the given widget ID."""
        return widget_id in self._selected_widget_ids

    def get_selected_widgets(
        self
    ) -> tuple[BaseWidget, ...]:
        """Return the selected widgets in selection order."""
        return tuple(
            self.get_widget_from_widget_id(widget_id)
            for widget_id in self._selected_widget_ids
        )

    def get_last_selected_widget_id(
        self
    ) -> str | None:
        """Return the ID of the last selected widget or None when the selection is empty."""
        if not self._selected_widget_ids:
            return None
        return self._selected_widget_ids[-1]

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
