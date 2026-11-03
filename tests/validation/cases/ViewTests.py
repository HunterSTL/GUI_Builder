from tests.validation.Helpers import create_designer, destroy_designer, create_valid_widget

def test_delete_tk_widget_with_missing_tk_widget_mapping() -> None:
    designer = create_designer()

    try:
        widget = create_valid_widget()
        designer._widget_view.render_tk_widget_for(widget)
        canvas_item_id = designer._widget_view.get_canvas_item_id_from_widget_id(widget.id)
        designer._widget_view._tk_widget_by_canvas_item_id.pop(canvas_item_id)
        designer._widget_view.delete_tk_widget_for(widget.id)
    finally:
        destroy_designer(designer)

def test_look_up_widget_with_unknown_canvas_item_id() -> None:
    designer = create_designer()

    try:
        widget = create_valid_widget()
        designer._widget_view.render_tk_widget_for(widget)
        canvas_item_id = designer._widget_view._canvas_item_id_by_widget_id[widget.id]
        designer._widget_view._widget_id_by_canvas_item_id.pop(canvas_item_id)
        designer._widget_view.get_widget_id_from_canvas_item_id(canvas_item_id)
    finally:
        destroy_designer(designer)

def test_render_tk_widget_with_missing_tk_widget_mapping() -> None:
    designer = create_designer()

    try:
        widget = create_valid_widget()
        designer._widget_view.render_tk_widget_for(widget)
        canvas_item_id = designer._widget_view.get_canvas_item_id_from_widget_id(widget.id)
        designer._widget_view._tk_widget_by_canvas_item_id.pop(canvas_item_id)
        designer._widget_view._update_tk_widget(canvas_item_id, widget)
    finally:
        destroy_designer(designer)

def test_instantiate_widget_with_unsupported_type() -> None:
    designer = create_designer()

    try:
        designer._widget_view._instantiate_tk_widget("UNSUPPORTED_TYPE")
    finally:
        destroy_designer(designer)
