from tests.validation.helpers import create_valid_widget

from model import ProjectDocument

from app_state import AppState

def test_subscribe_uncallable_to_app_state() -> None:
    app_state = AppState(ProjectDocument())
    app_state.subscribe("UNCALLABLE")

def test_add_widget_with_missing_id() -> None:
    app_state = AppState(ProjectDocument())
    widget = create_valid_widget(id=None)
    app_state.add_widget(widget)

def test_add_widget_with_duplicate_id() -> None:
    app_state = AppState(ProjectDocument())
    widget_1 = create_valid_widget(id="DUPLICATE_ID")
    widget_2 = create_valid_widget(id="DUPLICATE_ID")
    app_state.add_widget(widget_1)
    app_state.add_widget(widget_2)

def test_remove_widget_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    widget = create_valid_widget(id="UNKNOWN_ID")
    app_state.remove_widget(widget)

def test_update_widget_position_absolute_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    widget = create_valid_widget(id="UNKNOWN_ID")
    app_state.set_widget_position(widget, 100, 100)

def test_update_widget_position_relative_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    widget = create_valid_widget(id="UNKNOWN_ID")
    app_state.offset_widget_position(widget, 10, 10)

def test_update_widget_attribute_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    widget = create_valid_widget(id="UNKNOWN_ID")
    app_state.set_widget_attribute(widget, "x", 0)

def test_update_unknown_widget_attribute() -> None:
    app_state = AppState(ProjectDocument())
    widget = create_valid_widget()
    app_state.add_widget(widget)
    app_state.set_widget_attribute(widget, "UNKNOWN_ATTRIBUTE", "VALUE")

def test_select_widget_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    app_state.selection_handle_click(widget_id="UNKNOWN_ID", is_additive=False)

def test_look_up_widget_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    app_state.get_widget_from_widget_id("UNKNOWN_ID")

def test_look_up_widget_bounding_box_with_no_widget_provided() -> None:
    app_state = AppState(ProjectDocument())
    app_state.get_widget_bounding_box(None)

def test_look_up_widget_group_bounding_box_with_no_widgets_provided() -> None:
    app_state = AppState(ProjectDocument())
    app_state.get_widget_group_bounding_box([])
