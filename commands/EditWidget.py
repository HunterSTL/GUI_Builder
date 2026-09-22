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
        self._original_widget_data: dict[str, str | int | None] = widget.to_dict()
        self._final_widget_data: dict[str, str | int | None] | None = None

    def has_effect(
        self
    ) -> bool:
        """Return True if at least one editable attribute differs from its original value."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)
        current_widget_data = widget.to_dict()

        for attribute in self._original_widget_data.keys() & _EDITABLE_ATTRIBUTES:
            if current_widget_data[attribute] != self._original_widget_data[attribute]:
                return True
        return False

    def apply_attribute_changes(
        self,
        attribute_changes: dict[str, str | int]
    ) -> None:
        """Apply the given attribute changes to the widget."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)

        with self._app_state.batch():
            for attribute, value in attribute_changes.items():
                self._app_state.set_widget_attribute(widget, attribute, value)

    def record_final_widget_data(
        self
    ) -> None:
        """Record the widget's current attribute values as its final widget data."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)
        self._final_widget_data = widget.to_dict()

    def execute(
        self
    ) -> None:
        """Apply the stored final attribute values to the widget."""
        if self._final_widget_data is None:
            raise ValueError("EditWidget - execution failed: final attribute values were not recorded")

        self._apply_widget_data(self._final_widget_data)

    def undo(
        self
    ) -> None:
        """Restore the widget's stored original attribute values."""
        self._apply_widget_data(self._original_widget_data)

    def _apply_widget_data(
        self,
        widget_data: dict[str, str | int | None]
    ) -> None:
        """Apply the editable attribute values from the given widget data."""
        widget = self._app_state.get_widget_from_widget_id(self._widget_id)

        with self._app_state.batch():
            for attribute, value in widget_data.items():
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
                label=self._original_widget_data["id"],
                before_mapping=self._original_widget_data,
                after_mapping=self._final_widget_data
            )
        ]
        return "\n".join(lines)
