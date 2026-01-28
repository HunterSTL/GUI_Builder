def allowed_x_range(canvas_width: int, widget_width: int, anchor: str):
    if anchor in ["sw", "w", "nw"]:
        return 0, canvas_width - widget_width
    elif anchor in ["ne", "e", "se"]:
        return widget_width, canvas_width
    elif anchor in ["n", "s", "center"]:
        return widget_width // 2, canvas_width - (widget_width // 2)
    return 0, canvas_width

def allowed_y_range(canvas_height: int, widget_height: int, anchor: str):
    if anchor in ["sw", "s", "se"]:
        return widget_height, canvas_height
    elif anchor in ["nw", "n", "ne"]:
        return 0, canvas_height - widget_height
    elif anchor in ["w", "e", "center"]:
        return widget_height // 2, canvas_height - (widget_height // 2)
    return 0, canvas_height

def clamp(value: int, minimum: int, maximum: int):
    return max(minimum, min(maximum, value))

def clamped_delta(canvas_width, canvas_height, bbox: tuple[int, int, int, int], dx: int, dy: int) -> tuple[int, int]:
    if not bbox:
        return 0, 0

    x0, y0, x1, y1 = bbox
    min_dx, min_dy = -x0, -y0
    max_dx, max_dy = canvas_width - x1, canvas_height - y1
    return clamp(dx, min_dx, max_dx), clamp(dy, min_dy, max_dy)