from model import BaseWidget
from utility import format_mapping_changes

from AppState import AppState
from .BaseCommand import Command

_EDITABLE_ATTRIBUTES = {"x", "y", "bg", "fg", "width", "height", "anchor", "text"}

class EditWidget(Command):
    """Encapsulates widget attribute editing as an undoable command."""
    def __init__(
        self,
        widget: BaseWidget,
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        self._widget_id: str = widget.id    #storing IDs and retrieving widgets protects against stale widget references
        self._original_snapshot: dict[str, str | int] = widget.to_dict()
        self._final_snapshot: dict[str, str | int] | None = None

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one attribute value."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)
        current_snapshot = widget.to_dict()

        for attribute in self._original_snapshot.keys() & _EDITABLE_ATTRIBUTES:
            if current_snapshot[attribute] != self._original_snapshot[attribute]:
                return True
        return False

    def apply_attribute_changes(
        self,
        attribute_changes: dict[str, str | int]
    ) -> None:
        """Apply attribute changes to the widget through AppState."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)

        with self._app_state.batch():
            for attribute, value in attribute_changes.items():
                self._app_state.set_widget_attribute(widget, attribute, value)

    def record_final_snapshot(
        self
    ) -> None:
        """Record final attribute values."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)
        self._final_snapshot = widget.to_dict()

    def execute(
        self
    ) -> None:
        """Apply the snapshotted final attribute values to the widget through AppState."""
        if self._final_snapshot is None:
            raise ValueError("EditWidget - execution failed: final attribute values were not recorded")

        self._apply_snapshot(self._final_snapshot)

    def undo(
        self
    ) -> None:
        """Restore the snapshotted original attribute values to the widget through AppState."""
        self._apply_snapshot(self._original_snapshot)

    def _apply_snapshot(
        self,
        snapshot: dict[str, str | int]
    ) -> None:
        """Apply attribute values from the snapshot to the widget for all editable attributes."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)

        with self._app_state.batch():
            for attribute, value in snapshot.items():
                if attribute not in _EDITABLE_ATTRIBUTES:
                    continue

                if value == getattr(widget, attribute):
                    continue

                self._app_state.set_widget_attribute(widget, attribute, value)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[EditWidget]",
            format_mapping_changes(
                label=self._original_snapshot["id"],
                before_mapping=self._original_snapshot,
                after_mapping=self._final_snapshot
            )
        ]
        return "\n".join(lines)
