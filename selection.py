import tkinter as tk
from theme import *
from typing import Dict, Optional, Set

class SelectionManager:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self._selected: Set[int] = set()          #selected canvas item IDs (window items)
        self._rects: Dict[int, int] = {}          #window_id -> rectangle_id
        self._last_selected = None

    def clear(self):
        for item_id in list(self._selected):
            self._remove_highlight(item_id)
        self._selected.clear()

    def select_only(self, item_id: Optional[int]):
        if item_id is None:
            self.clear()
            return
        for other in list(self._selected):
            if other != item_id:
                self._remove_highlight(other)
        self._selected = {item_id}
        self._last_selected = item_id
        self._ensure_highlight(item_id)

    def toggle(self, item_id: Optional[int]):
        if item_id is None:
            return
        if item_id in self._selected:
            self._remove_highlight(item_id)
            self._selected.remove(item_id)
        else:
            self._selected.add(item_id)
            self._last_selected = item_id
            self._ensure_highlight(item_id)

    def selected_ids(self) -> Set[int]:
        return set(self._selected)

    def refresh(self, item_id: int):
        if item_id in self._selected:
            self._ensure_highlight(item_id)

    def refresh_all(self):
        for item_id in list(self._selected):
            self._ensure_highlight(item_id)

    def _ensure_highlight(self, item_id: int):
        bbox = self.canvas.bbox(item_id)
        rect_id = self._rects.get(item_id)

        if not bbox:
            #item is outside view
            return

        x1, y1, x2, y2 = bbox
        x1 -= SELECTION_PADDING
        y1 -= SELECTION_PADDING
        x2 += SELECTION_PADDING
        y2 += SELECTION_PADDING

        outline_color = LAST_SELECTED_COLOR if self._last_selected == item_id else SELECTION_COLOR

        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.coords(rect_id, x1, y1, x2, y2)
            self.canvas.itemconfig(rect_id, outline=outline_color)
        else:
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=outline_color,
                width=SELECTION_WIDTH,
                dash=SELECTION_DASH,
                fill=""
            )
            self._rects[item_id] = rect_id
        self.canvas.tag_raise(rect_id)

    def _remove_highlight(self, item_id: int):
        rect_id = self._rects.pop(item_id, None)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.delete(rect_id)