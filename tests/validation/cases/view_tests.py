from tests.validation.helpers import (
    create_designer,
    create_valid_widget,
    destroy_designer
)

def test_measure_preview_tk_widget_with_unsupported_type() -> None:
    designer = create_designer()

    try:
        designer._widget_view.measure_preview_tk_widget(
            widget_type="UNSUPPORTED_TYPE",
            text="text"
        )
    finally:
        destroy_designer(designer)

def test_look_up_widget_with_unknown_canvas_item_id() -> None:
    designer = create_designer()

    try:
        widget = create_valid_widget()
        designer._widget_view.render_widget_visual_for(widget)
        widget_visual = designer._widget_view._widget_visual_by_widget_id[widget.id]
        designer._widget_view._widget_id_by_canvas_item_id.pop(widget_visual.rectangle_id)
        designer._widget_view.get_widget_id_from_canvas_item_id(widget_visual.rectangle_id)
    finally:
        destroy_designer(designer)
