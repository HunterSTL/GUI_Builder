from collections.abc import Iterable
from copy import copy

from app_state import AppState
from commands.base_command import InteractiveCommand
from model import Widget
from utility.edge import Edge
from utility.geometry import (
    BoundingBox,
    clamp,
    compute_widget_position_from_bounding_box
)
from utility.string_utilities import format_mapping_changes


class ResizeWidgets(InteractiveCommand):
    """Encapsulates widget resizing as an undoable command."""
    def __init__(
        self,
        widgets: Iterable[Widget],
        app_state: AppState
    ) -> None:
        self._app_state: AppState = app_state

        widgets = tuple(widgets)                                            #freezes iteration order for deterministic undo and redo behaviour
        self._widget_ids: list[str] = [widget.id for widget in widgets]     #storing IDs and retrieving widgets protects against stale widget references

        self._original_bboxes: dict[str, BoundingBox] = {
            widget.id: self._app_state.get_widget_bounding_box(widget)
            for widget in widgets
        }
        self._final_bboxes: dict[str, BoundingBox] = {}

    def has_effect(
        self
    ) -> bool:
        """Return True if at least one widget's bounding box differs from its original bounding box."""
        if not self._final_bboxes:
            raise ValueError("ResizeWidgets - effect check failed: final bounding boxes were not recorded")

        return any(
            self._original_bboxes[widget_id] != self._final_bboxes[widget_id]
            for widget_id in self._widget_ids
        )

    def apply_resize_delta(
        self,
        total_dx: int,
        total_dy: int,
        edge: Edge
    ) -> None:
        """Apply a total resize delta to the widgets."""
        with self._app_state.batch():
            for widget_id in self._widget_ids:
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                original_bbox = self._original_bboxes[widget_id]
                bbox = copy(original_bbox)

                match edge:
                    case Edge.LEFT:
                        bbox.left = clamp(original_bbox.left + total_dx, 0, bbox.right - 1)
                    case Edge.TOP:
                        bbox.top = clamp(original_bbox.top + total_dy, 0, bbox.bottom - 1)
                    case Edge.RIGHT:
                        bbox.right = clamp(original_bbox.right + total_dx, bbox.left + 1, self._app_state.project.width)
                    case Edge.BOTTOM:
                        bbox.bottom = clamp(original_bbox.bottom + total_dy, bbox.top + 1, self._app_state.project.height)

                self._apply_bounding_box_to_widget(bbox, widget)

    def record_final_bounding_boxes(
        self
    ) -> None:
        """Record the widgets' current dimensions as their final dimensions."""
        final_bboxes = {}

        for widget_id in self._widget_ids:
            widget = self._app_state.get_widget_from_widget_id(widget_id)
            final_bboxes[widget_id] = self._app_state.get_widget_bounding_box(widget)

        self._final_bboxes = final_bboxes

    def execute(
        self
    ) -> None:
        """Apply the stored final bounding boxes to the widgets."""
        if not self._final_bboxes:
            raise ValueError("ResizeWidgets - execution failed: final bounding boxes were not recorded")

        with self._app_state.batch():
            for widget_id, bbox in self._final_bboxes.items():
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                self._apply_bounding_box_to_widget(bbox, widget)

    def undo(
        self
    ) -> None:
        """Restore the widgets to their stored original bounding boxes."""
        with self._app_state.batch():
            for widget_id, bbox in self._original_bboxes.items():
                widget = self._app_state.get_widget_from_widget_id(widget_id)
                self._apply_bounding_box_to_widget(bbox, widget)

    def _apply_bounding_box_to_widget(
        self,
        bounding_box: BoundingBox,
        widget: Widget
    ) -> None:
        x, y = compute_widget_position_from_bounding_box(bounding_box, widget.anchor)
        self._app_state.set_widget_attribute(widget, "x", x)
        self._app_state.set_widget_attribute(widget, "y", y)
        self._app_state.set_widget_attribute(widget, "width", bounding_box.right - bounding_box.left)
        self._app_state.set_widget_attribute(widget, "height", bounding_box.bottom - bounding_box.top)

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command."""
        lines = [
            "[ResizeWidgets]",
            format_mapping_changes(
                label="bounding boxes",
                before_mapping=self._original_bboxes,
                after_mapping=self._final_bboxes
            )
        ]
        return "\n".join(lines)
