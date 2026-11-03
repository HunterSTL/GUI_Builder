from utility import Geometry

def test_compute_allowed_x_range_with_widget_width_exceeding_canvas_width() -> None:
    Geometry.allowed_x_range(
        canvas_width=100,
        widget_width=200,
        anchor="SW"
    )

def test_compute_allowed_x_range_with_invalid_anchor() -> None:
    Geometry.allowed_x_range(
        canvas_width=200,
        widget_width=100,
        anchor="INVALID_ANCHOR"
    )

def test_compute_allowed_y_range_with_widget_height_exceeding_canvas_height() -> None:
    Geometry.allowed_y_range(
        canvas_height=100,
        widget_height=200,
        anchor="SW"
    )

def test_compute_allowed_y_range_with_invalid_anchor() -> None:
    Geometry.allowed_y_range(
        canvas_height=200,
        widget_height=100,
        anchor="INVALID_ANCHOR"
    )

def test_compute_bounding_box_with_invalid_anchor() -> None:
    Geometry.compute_widget_bounding_box(
        x=0,
        y=0,
        width=50,
        height=20,
        anchor="INVALID_ANCHOR"
    )
