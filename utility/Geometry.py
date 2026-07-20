from math import floor, ceil
from dataclasses import dataclass

@dataclass
class BoundingBox:
    left: int
    top: int
    right: int
    bottom: int

def allowed_x_range(canvas_width: int, widget_width: int, anchor: str) -> tuple[int, int]:
    """return the allowed X-coordinate range for a model based on its anchor and canvas dimensions"""
    if anchor in ["sw", "w", "nw"]:
        return 0, canvas_width - widget_width
    elif anchor in ["ne", "e", "se"]:
        return widget_width, canvas_width
    elif anchor in ["n", "s", "center"]:
        return widget_width // 2, canvas_width - (widget_width // 2)
    return 0, canvas_width

def allowed_y_range(canvas_height: int, widget_height: int, anchor: str) -> tuple[int, int]:
    """return the allowed Y-coordinate range for a model based on its anchor and canvas dimensions"""
    if anchor in ["sw", "s", "se"]:
        return widget_height, canvas_height
    elif anchor in ["nw", "n", "ne"]:
        return 0, canvas_height - widget_height
    elif anchor in ["w", "e", "center"]:
        return widget_height // 2, canvas_height - (widget_height // 2)
    return 0, canvas_height

def clamp(value: int, minimum: int, maximum: int) -> int:
    """clamp a value into the given minimum - maximum range"""
    return max(minimum, min(maximum, value))

def clamped_delta(canvas_width, canvas_height, bounding_box: BoundingBox, dx: int, dy: int) -> tuple[int, int]:
    """clamp a movement delta so the given bounding box (of one or more models) stays fully within the canvas bounds"""
    if not bounding_box:
        return 0, 0

    x0, y0, x1, y1 = bounding_box.left, bounding_box.top, bounding_box.right, bounding_box.bottom
    min_dx, min_dy = -x0, -y0
    max_dx, max_dy = canvas_width - x1, canvas_height - y1
    return clamp(dx, min_dx, max_dx), clamp(dy, min_dy, max_dy)

def screen_offset_to_center_window(screen_width, screen_height, window_width, window_height) -> tuple[int, int]:
    """return the X- and Y-offset needed to center the window on the screen"""
    return (screen_width // 2) - (window_width // 2), (screen_height // 2) - (window_height // 2)

def nearest_in_bounds_grid_step(value: int, grid_size: int, min_value: int, max_value: int) -> int:
    """return the value of the nearest grid step of size grid_size that lies within the allowed range"""
    #no grid size → just clamp
    if grid_size <= 0:
        return clamp(value, min_value, max_value)

    #nearest grid step to the actual value
    nearest_grid_step = round(value / grid_size) * grid_size

    #return the nearest grid step if it is within bounds
    if min_value <= nearest_grid_step <= max_value:
        return nearest_grid_step

    #first and last grid steps that are within the allowed range
    first_in_bound_grid_step = ceil(min_value / grid_size) * grid_size
    last_in_bound_grid_step = floor(max_value / grid_size) * grid_size

    #if at least one in-bound grid step exists → choose the nearest grid step
    if first_in_bound_grid_step <= last_in_bound_grid_step:
        if nearest_grid_step < first_in_bound_grid_step:
            return first_in_bound_grid_step
        elif nearest_grid_step > last_in_bound_grid_step:
            return last_in_bound_grid_step

    #if there are no grid steps inside the allowed range → only clamp to allowed range
    return clamp(value, min_value, max_value)

def compute_model_bounding_box(x: int, y: int, width: int, height: int, anchor: str) -> BoundingBox:
    """compute the model's bounding box based on position, size and anchor"""
    if x is None:
        raise ValueError("Geometry - computation failed: missing x coordinate")
    if y is None:
        raise ValueError("Geometry - computation failed: missing y coordinate")
    if width is None:
        raise ValueError("Geometry - computation failed: missing width")
    if height is None:
        raise ValueError("Geometry - computation failed: missing height")

    if anchor == "sw":
        left, right = x, x + width
        top, bottom = y - height, y
    elif anchor == "w":
        left, right = x, x + width
        top, bottom = y - (height // 2), y + (height - (height // 2))
    elif anchor == "nw":
        left, right = x, x + width
        top, bottom = y, y + height
    elif anchor == "n":
        left, right = x - (width // 2), x + (width - (width // 2))
        top, bottom = y, y + height
    elif anchor == "ne":
        left, right = x - width, x
        top, bottom = y, y + height
    elif anchor == "e":
        left, right = x - width, x
        top, bottom = y - (height // 2), y + (height - (height // 2))
    elif anchor == "se":
        left, right = x - width, x
        top, bottom = y - height, y
    elif anchor == "s":
        left, right = x - (width // 2), x + (width - (width // 2))
        top, bottom = y - height, y
    elif anchor == "center":
        left, right = x - (width // 2), x + (width - (width // 2))
        top, bottom = y - (height // 2), y + (height - (height // 2))
    else:
        raise ValueError(f"Geometry - computation failed: invalid anchor \"{anchor}\"")

    return BoundingBox(
        left=left,
        top=top,
        right=right,
        bottom=bottom
    )
