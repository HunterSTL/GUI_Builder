from model import BaseWidgetData

from AppState import AppState
from .BaseCommand import Command

_EDITABLE_ATTRIBUTES = {"x", "y", "bg", "fg", "width", "height", "anchor", "text"}

class EditWidget(Command):
    """Encapsulates widget attribute editing as an undoable command."""
    def __init__(
        self,
        model: BaseWidgetData,
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        self._model_id: str = model.id   #storing the ID and retrieving the model protects against a stale model
        self._original_snapshot: dict[str, str | int] = model.to_dict()
        self._final_snapshot: dict[str, str | int] | None = None

    def has_effect(
        self
    ) -> bool:
        """Return True if execution would change at least one attribute value."""
        model = self._app_state.get_model_from_model_id(self._model_id)
        current_snapshot = model.to_dict()

        for attribute in self._original_snapshot.keys() & _EDITABLE_ATTRIBUTES:
            if current_snapshot[attribute] != self._original_snapshot[attribute]:
                return True
        return False

    def apply_attribute_changes(
        self,
        attribute_changes: dict[str, str | int]
    ) -> None:
        """Apply attribute changes to the widget model through AppState."""
        model = self._app_state.get_model_from_model_id(self._model_id)

        with self._app_state.batch():
            for attribute, value in attribute_changes.items():
                self._app_state.set_model_attribute(model, attribute, value)

    def record_final_snapshot(
        self
    ) -> None:
        """Record final attribute values."""
        model = self._app_state.get_model_from_model_id(self._model_id)
        self._final_snapshot = model.to_dict()

    def execute(
        self
    ) -> None:
        """Apply the snapshotted final attribute values to the widget model through AppState."""
        if self._final_snapshot is None:
            raise ValueError("EditWidget - execution failed: final attribute values were not recorded")

        self._apply_snapshot(self._final_snapshot)

    def undo(
        self
    ) -> None:
        """Restore the snapshotted original attribute values to the widget model through AppState."""
        self._apply_snapshot(self._original_snapshot)

    def _apply_snapshot(
        self,
        snapshot: dict[str, str | int]
    ) -> None:
        """Apply attribute values from the snapshot to the widget model for all editable attributes."""
        model = self._app_state.get_model_from_model_id(self._model_id)

        with self._app_state.batch():
            for attribute, value in snapshot.items():
                if attribute not in _EDITABLE_ATTRIBUTES:
                    continue

                if value == getattr(model, attribute):
                    continue

                self._app_state.set_model_attribute(model, attribute, value)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        s = "[EditWidget]"
        s += f"\n\tmodel ID:\t\t\t{self._model_id}"
        s += f"\n\toriginal snapshot:\t{self._original_snapshot}"
        s += f"\n\tfinal snapshot:\t{self._final_snapshot}"
        return s