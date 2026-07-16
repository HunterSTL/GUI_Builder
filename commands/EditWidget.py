from model import BaseWidgetData
from commands import Command
from AppState import AppState

_EDITABLE_ATTRIBUTES = {"x", "y", "bg", "fg", "width", "height", "anchor", "text"}

class EditWidget(Command):
    def __init__(
        self,
        model: BaseWidgetData,
        app_state: AppState
    ) -> None:
        """store affected model ID and snapshot original attribute values; final attribute values are snapshotted at the end of the edit"""
        self._app_state = app_state

        self._model_id = model.id   #storing IDs and retrieving models protects against stale models
        self._original_snapshot = model.to_dict(include_id=True)
        self._final_snapshot = None

    def has_effect(self) -> bool:
        """return True if any attribute value changed since initialization"""
        model = self._app_state.get_model_from_model_id(self._model_id)
        current_snapshot = model.to_dict(include_id=True)

        for attribute in self._original_snapshot.keys() & _EDITABLE_ATTRIBUTES:
            if current_snapshot[attribute] != self._original_snapshot[attribute]:
                return True
        return False

    def apply_attribute_changes(self, attribute_changes: dict[str, str | int]) -> None:
        """apply attribute changes"""
        model = self._app_state.get_model_from_model_id(self._model_id)

        with self._app_state.batch():
            for attribute, value in attribute_changes.items():
                self._app_state.set_model_attribute(model, attribute, value)

    def record_final_snapshot(self) -> None:
        """record final attribute values at the end of an edit"""
        model = self._app_state.get_model_from_model_id(self._model_id)
        self._final_snapshot = model.to_dict(include_id=True)

    def execute(self) -> None:
        """apply attribute values from the final snapshot"""
        if self._final_snapshot is None:
            raise ValueError("EditWidget - execution failed: final attribute values were not recorded")

        self._apply_snapshot(self._final_snapshot)

    def undo(self) -> None:
        """restore attribute values from the original snapshot"""
        self._apply_snapshot(self._original_snapshot)

    def _apply_snapshot(self, snapshot: dict) -> None:
        """apply editable attribute values from a snapshot to the model"""
        model = self._app_state.get_model_from_model_id(self._model_id)

        with self._app_state.batch():
            for attribute, value in snapshot.items():
                if attribute not in _EDITABLE_ATTRIBUTES:
                    continue

                if value == getattr(model, attribute):
                    continue

                self._app_state.set_model_attribute(model, attribute, value)

    def __repr__(self):
        """called automatically when printing this object"""
        s = "[EditWidget]"
        s += f"\n\tmodel ID:\t\t\t{self._model_id}"
        s += f"\n\toriginal snapshot:\t{self._original_snapshot}"
        s += f"\n\tfinal snapshot:\t{self._final_snapshot}"
        return s