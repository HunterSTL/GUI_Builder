from typing import TypedDict


class DimensionConstants(TypedDict):
    """Defines minimum and maximum dimensions."""
    min_width: int
    min_height: int
    max_width: int
    max_height: int


class NudgeConstants(TypedDict):
    """Defines movement amounts for widget nudging."""
    small: int
    big: int


class SelectionConstants(TypedDict):
    """Defines selection outline dimensions and appearance."""
    width: int
    padding: int
    dash: tuple[int, int]


class ApplicationConstants(TypedDict):
    """Defines the structure of application constants."""
    window: DimensionConstants
    canvas: DimensionConstants
    nudge: NudgeConstants
    selection: SelectionConstants
    titlebar_height: int
    toolbar_height: int
    attributes_panel_width: int
    grid_size: int
    ctrl_key: int
    drag_threshold: int


CONSTANTS: ApplicationConstants = {
    "window": {
        "min_width": 600,
        "min_height": 400,
        "max_width": 1200,
        "max_height": 800
    },
    "canvas": {
        "min_width": 200,
        "min_height": 200,
        "max_width": 5000,
        "max_height": 5000
    },
    "nudge": {
        "small": 1,
        "big": 10
    },
    "selection": {
        "width": 2,
        "padding": 3,
        "dash": (3, 2)
    },
    "titlebar_height": 25,
    "toolbar_height": 25,
    "attributes_panel_width": 200,
    "grid_size": 10,
    "ctrl_key": 0x0004,
    "drag_threshold": 10
}
