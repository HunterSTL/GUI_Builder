import sys
from pathlib import Path
from ValidationFramework import ValidationTest, run_validation_tests, print_validation_test_results

sys.path.insert(0, str(Path(__file__).parent.parent.parent))    #GUI_Builder/

import tkinter as tk
from commands import DragWidgets, EditWidget
from events import EventBus
from model import GridConfig, IdCounters, ProjectDocument, LabelWidgetData, BaseWidgetData
from utility import WidgetType, Geometry, CONSTANTS
from AppState import AppState
from Designer import Designer
from Theme import USER_THEME, PROGRAM_THEME

FIRST_WIDGET_ID = 2

MINIMUM_CANVAS_WIDTH = CONSTANTS["canvas"]["min_width"]
MINIMUM_CANVAS_HEIGHT = CONSTANTS["canvas"]["min_height"]
MAXIMUM_CANVAS_WIDTH = CONSTANTS["canvas"]["max_width"]
MAXIMUM_CANVAS_HEIGHT = CONSTANTS["canvas"]["max_height"]

MINIMUM_GRID_SIZE = CONSTANTS["grid"]["min_size"]
MAXIMUM_GRID_SIZE = CONSTANTS["grid"]["max_size"]

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

WIDGET_WIDTH = 100
WIDGET_HEIGHT = 20

#Lifecycle management---------------------------------------------------------------------------------------------------
def setup_designer() -> dict:
    def _init_and_withdraw(self, *args, **kwargs):
        """executes the original __init__ and self.withdraw()"""
        original_init(self, *args, **kwargs)
        self.withdraw()

    root = tk.Tk()
    root.withdraw()

    #withdraw Toplevel after __init__ to prevent the window from showing up during tests
    original_init = tk.Toplevel.__init__
    tk.Toplevel.__init__ = _init_and_withdraw

    try:
        designer = Designer(
            parent=root,
            project_document=ProjectDocument(theme=USER_THEME),
            program_theme=PROGRAM_THEME,
            app_event_bus=EventBus()
        )
    except Exception:
        root.destroy()
        raise
    finally:
        tk.Toplevel.__init__ = original_init

    return {
        "designer": designer
    }

def teardown_designer(designer: Designer) -> None:
    root = designer._parent
    root.destroy()

#Helpers----------------------------------------------------------------------------------------------------------------
def _create_valid_project_data(**overrides) -> dict[str, object]:
    project_data = {
        "version": 1,
        "title": "TITLE",
        "width": CANVAS_WIDTH,
        "height": CANVAS_HEIGHT,
        "grid": {
            "size": 10,
            "color": "#ffffff",
            "visible": False
        },
        "theme": {},
        "widgets": [],
        "id_counters": {
            "label": 1,
            "entry": 1,
            "button": 1
        }
    }
    project_data.update(overrides)
    return project_data

def _create_valid_widget_data(**overrides) -> dict[str, object]:
    widget_data = {
        "type": "Label",
        "id": "ID",
        "x": 100,
        "y": 100,
        "bg": "#000000",
        "fg": "#ffffff",
        "width": WIDGET_WIDTH,
        "height": WIDGET_HEIGHT,
        "anchor": "sw",
        "text": "TEXT"
    }
    widget_data.update(overrides)
    return widget_data

def _create_valid_widget_model(**overrides) -> LabelWidgetData:
    widget_data = _create_valid_widget_data(**overrides)
    widget_data.pop("type")
    return LabelWidgetData(**widget_data)

def _create_edit_widget_command() -> EditWidget:
    return EditWidget(
        model=_create_valid_widget_model(),
        app_state=AppState(ProjectDocument())
    )

def _create_drag_widgets_command() -> DragWidgets:
    return DragWidgets(
        models=(_create_valid_widget_model(),),
        app_state=AppState(ProjectDocument())
    )

#AppState tests---------------------------------------------------------------------------------------------------------
def action_subscribe_uncallable_to_app_state() -> None:
    app_state = AppState(ProjectDocument())
    app_state.subscribe("UNCALLABLE")

def action_add_model_with_missing_id() -> None:
    app_state = AppState(ProjectDocument())
    model = _create_valid_widget_model(id=None)
    app_state.add_model(model)

def action_add_model_with_duplicate_id() -> None:
    app_state = AppState(ProjectDocument())
    model_1 = _create_valid_widget_model(id="DUPLICATE_ID")
    model_2 = _create_valid_widget_model(id="DUPLICATE_ID")
    app_state.add_model(model_1)
    app_state.add_model(model_2)

def action_remove_model_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    model = _create_valid_widget_model(id="UNKNOWN_ID")
    app_state.remove_model(model)

def action_update_model_position_absolute_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    model = _create_valid_widget_model(id="UNKNOWN_ID")
    app_state.set_model_position(model, 100, 100)

def action_update_model_position_relative_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    model = _create_valid_widget_model(id="UNKNOWN_ID")
    app_state.offset_model_position(model, 10, 10)

def action_update_model_attribute_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    model = _create_valid_widget_model(id="UNKNOWN_ID")
    app_state.set_model_attribute(model, "x", 0)

def action_update_unknown_model_attribute() -> None:
    app_state = AppState(ProjectDocument())
    model = _create_valid_widget_model()
    app_state.add_model(model)
    app_state.set_model_attribute(model, "UNKNOWN_ATTRIBUTE", "VALUE")

def action_select_model_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    app_state.selection_handle_click(model_id="UNKNOWN_ID", is_additive=False)

def action_look_up_model_with_unknown_id() -> None:
    app_state = AppState(ProjectDocument())
    app_state.get_model_from_model_id("UNKNOWN_ID")

def action_look_up_model_bounding_box_with_no_model_provided() -> None:
    app_state = AppState(ProjectDocument())
    app_state.get_model_bounding_box(None)

def action_look_up_model_group_bounding_box_with_no_models_provided() -> None:
    app_state = AppState(ProjectDocument())
    app_state.get_model_group_bounding_box([])

#Designer tests---------------------------------------------------------------------------------------------------------
def action_handle_unsupported_attributes_panel_edit_phase(designer: Designer) -> None:
    designer._handle_attribute_panel_edit_phase("UNSUPPORTED_PHASE")

#WidgetActions tests----------------------------------------------------------------------------------------------------
def action_add_widget_with_missing_coordinates(designer: Designer) -> None:
    designer._actions.widget.add(
        widget_type=WidgetType.LABEL,
        coordinates=None,
        text="TEXT"
    )

def action_add_label_with_missing_text(designer: Designer) -> None:
    designer._actions.widget.add(
        widget_type=WidgetType.LABEL,
        coordinates=(100, 100),
        text=None
    )

def action_add_button_with_missing_text(designer: Designer) -> None:
    designer._actions.widget.add(
        widget_type=WidgetType.BUTTON,
        coordinates=(100, 100),
        text=None
    )

def action_add_widget_with_unsupported_type(designer: Designer) -> None:
    designer._actions.widget.add(
        widget_type="UNSUPPORTED_TYPE",
        coordinates=(100, 100),
        text="TEXT"
    )

#EditWidget command tests-----------------------------------------------------------------------------------------------
def action_execute_edit_widget_command_without_recording_final_attribute_values() -> None:
    command = _create_edit_widget_command()
    command.execute()

#DragWidgets command tests----------------------------------------------------------------------------------------------
def action_execute_drag_widgets_command_without_recording_final_positions() -> None:
    command = _create_drag_widgets_command()
    command.execute()

#AttributesPanel tests--------------------------------------------------------------------------------------------------
def action_compute_spinbox_limits_for_unsupported_attribute(designer: Designer) -> None:
    designer._attributes_panel._compute_spinbox_limits(
        model=_create_valid_widget_model(),
        attribute="UNSUPPORTED_ATTRIBUTE"
    )

def action_create_colorpicker_for_unsupported_attribute(designer: Designer) -> None:
    designer._attributes_panel._create_colorpicker(
        model=_create_valid_widget_model(),
        attribute="UNSUPPORTED_ATTRIBUTE",
        row=0
    )

def action_create_combobox_for_unsupported_attribute(designer: Designer) -> None:
    designer._attributes_panel._create_combobox(
        model=_create_valid_widget_model(),
        attribute="UNSUPPORTED_ATTRIBUTE",
        row=0
    )

#EventBus tests---------------------------------------------------------------------------------------------------------
def action_subscribe_uncallable_to_event_bus() -> None:
    event_bus = EventBus()
    event_bus.subscribe("EVENT", "UNCALLABLE")

def action_fail_handler_execution() -> None:
    def _handler() -> None:
        raise ValueError("ERROR")

    event_bus = EventBus()
    event_bus.subscribe("EVENT", _handler)
    event_bus.emit("EVENT")

#GridConfig tests-------------------------------------------------------------------------------------------------------
def action_deserialize_grid_data_with_invalid_input_type() -> None:
    GridConfig.from_dict(grid_data=[])

def action_deserialize_grid_data_with_missing_required_attribute() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "#ffffff"
        }
    )

def action_deserialize_grid_data_with_invalid_attribute_set() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "#ffffff",
            "visible": False,
            "UNEXPECTED_ATTRIBUTE": "value"
        }
    )

def action_deserialize_grid_data_with_invalid_size() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": "INVALID_SIZE",
            "color": "#ffffff",
            "visible": False
        }
    )

def action_deserialize_grid_data_with_size_outside_allowed_range() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 1,
            "color": "#ffffff",
            "visible": False
        }
    )

def action_deserialize_grid_data_with_invalid_color() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "INVALID_COLOR",
            "visible": False
        }
    )

def action_deserialize_grid_data_with_invalid_visibility() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "#ffffff",
            "visible": "INVALID_VISIBILITY"
        }
    )

#IdCounters tests-------------------------------------------------------------------------------------------------------
def action_generate_id_for_unsupported_type() -> None:
    id_counters = IdCounters()
    id_counters.generate_id(widget_type="UNSUPPORTED_TYPE")

def action_deserialize_id_counter_data_with_invalid_input_type() -> None:
    IdCounters.from_dict(id_counter_data=[])

def action_deserialize_id_counter_data_with_missing_required_attribute() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": 1
        }
    )

def action_deserialize_id_counter_data_with_invalid_attribute_set() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": 1,
            "button": 1,
            "UNEXPECTED_ATTRIBUTE": "value"
        }
    )

def action_deserialize_id_counter_data_with_invalid_label_id_counter_value() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": "INVALID_LABEL_ID_COUNTER_VALUE",
            "entry": 1,
            "button": 1
        }
    )

def action_deserialize_id_counter_data_with_invalid_entry_id_counter_value() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": "INVALID_ENTRY_ID_COUNTER_VALUE",
            "button": 1
        }
    )

def action_deserialize_id_counter_data_with_invalid_button_id_counter_value() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": 1,
            "button": "INVALID_BUTTON_ID_COUNTER_VALUE"
        }
    )

#ProjectDocument tests--------------------------------------------------------------------------------------------------
def action_deserialize_project_data_with_invalid_input_type() -> None:
    ProjectDocument.from_json([])

def action_deserialize_project_data_with_missing_required_attribute() -> None:
    project_data = _create_valid_project_data()
    project_data.pop("id_counters")
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_attribute_set() -> None:
    project_data = _create_valid_project_data()
    project_data["UNEXPECTED_ATTRIBUTE"] = "value"
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_version() -> None:
    project_data = _create_valid_project_data(version="INVALID_VERSION")
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_unsupported_version() -> None:
    project_data = _create_valid_project_data(version=2)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_title() -> None:
    project_data = _create_valid_project_data(title=None)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_width() -> None:
    project_data = _create_valid_project_data(width="INVALID_WIDTH")
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_height() -> None:
    project_data = _create_valid_project_data(height="INVALID_HEIGHT")
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_width_outside_allowed_range() -> None:
    project_data = _create_valid_project_data(width=MAXIMUM_CANVAS_WIDTH + 1)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_height_outside_allowed_range() -> None:
    project_data = _create_valid_project_data(height=MAXIMUM_CANVAS_HEIGHT + 1)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_icon_path() -> None:
    project_data = _create_valid_project_data(icon_path=1)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_theme_type() -> None:
    project_data = _create_valid_project_data(theme=[])
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_invalid_widget_data_list_type() -> None:
    project_data = _create_valid_project_data(widgets={})
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_duplicate_widget_id() -> None:
    widget_data_list = [
        _create_valid_widget_data(id="DUPLICATE_ID"),
        _create_valid_widget_data(id="DUPLICATE_ID")
    ]
    project_data = _create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_widget_width_exceeding_canvas_width() -> None:
    widget_data_list = [
        _create_valid_widget_data(width=CANVAS_WIDTH + 1)
    ]
    project_data = _create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_widget_height_exceeding_canvas_height() -> None:
    widget_data_list = [
        _create_valid_widget_data(height=CANVAS_HEIGHT + 1)
    ]
    project_data = _create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_widget_x_coordinate_outside_allowed_range() -> None:
    invalid_x = CANVAS_WIDTH - WIDGET_WIDTH + 1
    widget_data_list = [
        _create_valid_widget_data(x=invalid_x)
    ]
    project_data = _create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def action_deserialize_project_data_with_widget_y_coordinate_outside_allowed_range() -> None:
    invalid_y = CANVAS_HEIGHT + 1
    widget_data_list = [
        _create_valid_widget_data(y=invalid_y)
    ]
    project_data = _create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

#WidgetModel tests------------------------------------------------------------------------------------------------------
def action_instantiate_widget_model_base_type() -> None:
    widget_data = _create_valid_widget_data()
    widget_data.pop("type")
    widget_data.pop("text")
    BaseWidgetData(**widget_data)

def action_deserialize_widget_data_with_invalid_input_type() -> None:
    BaseWidgetData.from_dict(widget_data=[])

def action_deserialize_widget_data_with_missing_type() -> None:
    widget_data = _create_valid_widget_data()
    widget_data.pop("type")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_type() -> None:
    widget_data = _create_valid_widget_data(type="INVALID_TYPE")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_missing_required_attribute() -> None:
    widget_data = _create_valid_widget_data()
    widget_data.pop("text")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_attribute_set() -> None:
    widget_data = _create_valid_widget_data()
    widget_data["UNEXPECTED_ATTRIBUTE"] = "value"
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_id() -> None:
    widget_data = _create_valid_widget_data(id=None)
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_x_coordinate() -> None:
    widget_data = _create_valid_widget_data(x="INVALID_X_COORDINATE")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_y_coordinate() -> None:
    widget_data = _create_valid_widget_data(y="INVALID_Y_COORDINATE")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_background_color() -> None:
    widget_data = _create_valid_widget_data(bg="INVALID_BACKGROUND_COLOR")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_foreground_color() -> None:
    widget_data = _create_valid_widget_data(fg="INVALID_FOREGROUND_COLOR")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_width() -> None:
    widget_data = _create_valid_widget_data(width="INVALID_WIDTH")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_height() -> None:
    widget_data = _create_valid_widget_data(height="INVALID_HEIGHT")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_anchor() -> None:
    widget_data = _create_valid_widget_data(anchor="INVALID_ANCHOR")
    BaseWidgetData.from_dict(widget_data)

def action_deserialize_widget_data_with_invalid_text() -> None:
    widget_data = _create_valid_widget_data(text=None)
    BaseWidgetData.from_dict(widget_data)

#Geometry tests---------------------------------------------------------------------------------------------------------
def action_compute_allowed_x_range_with_widget_width_exceeding_canvas_width() -> None:
    Geometry.allowed_x_range(
        canvas_width=100,
        widget_width=200,
        anchor="SW"
    )

def action_compute_allowed_x_range_with_invalid_anchor() -> None:
    Geometry.allowed_x_range(
        canvas_width=200,
        widget_width=100,
        anchor="INVALID_ANCHOR"
    )

def action_compute_allowed_y_range_with_widget_height_exceeding_canvas_height() -> None:
    Geometry.allowed_y_range(
        canvas_height=100,
        widget_height=200,
        anchor="SW"
    )

def action_compute_allowed_y_range_with_invalid_anchor() -> None:
    Geometry.allowed_y_range(
        canvas_height=200,
        widget_height=100,
        anchor="INVALID_ANCHOR"
    )

def action_compute_bounding_box_with_invalid_anchor() -> None:
    Geometry.compute_model_bounding_box(
        x=0,
        y=0,
        width=50,
        height=20,
        anchor="INVALID_ANCHOR"
    )

#WidgetView tests-------------------------------------------------------------------------------------------------------
def action_update_widget_with_missing_position(designer: Designer) -> None:
    model = _create_valid_widget_model(x=None, y=None)
    designer._widget_view.update_widget_for(model)

def action_update_widget_with_unknown_widget_id(designer: Designer) -> None:
    model = _create_valid_widget_model()
    designer._widget_view.update_widget_for(model)
    widget_id = designer._widget_view.get_widget_id_from_model_id(model.id)
    designer._widget_view.widget_map[widget_id] = None
    designer._widget_view.update_widget_for(model)

def action_instantiate_widget_with_unsupported_type(designer: Designer) -> None:
    designer._widget_view._instantiate_widget("UNSUPPORTED_TYPE")

def action_look_up_widget_with_unknown_widget_id(designer: Designer) -> None:
    model = _create_valid_widget_model()
    designer._widget_view.update_widget_for(model)
    widget_id = designer._widget_view.get_widget_id_from_model_id(model.id)
    designer._widget_view.widget_map[widget_id] = None
    designer._widget_view.get_widget_from_model_id(model.id)

VALIDATION_TESTS = (
    ValidationTest(
        name="Subscribing uncallable to AppState",
        expected_error_message="AppState - subscription failed: subscriber must be callable",
        action=action_subscribe_uncallable_to_app_state
    ),
    ValidationTest(
        name="Adding model with missing ID to AppState",
        expected_error_message="AppState - model addition failed: missing ID",
        action=action_add_model_with_missing_id
    ),
    ValidationTest(
        name="Adding model with duplicate ID to AppState",
        expected_error_message="AppState - model addition failed: duplicate ID \"DUPLICATE_ID\"",
        action=action_add_model_with_duplicate_id
    ),
    ValidationTest(
        name="Removing model with unknown ID from AppState",
        expected_error_message="AppState - model removal failed: unknown ID \"UNKNOWN_ID\"",
        action=action_remove_model_with_unknown_id
    ),
    ValidationTest(
        name="Updating model position (absolute) with unknown ID",
        expected_error_message="AppState - model position update failed: unknown ID \"UNKNOWN_ID\"",
        action=action_update_model_position_absolute_with_unknown_id
    ),
    ValidationTest(
        name="Updating model position (relative) with unknown ID",
        expected_error_message="AppState - model position update failed: unknown ID \"UNKNOWN_ID\"",
        action=action_update_model_position_relative_with_unknown_id
    ),
    ValidationTest(
        name="Updating model attribute with unknown ID",
        expected_error_message="AppState - model attribute update failed: unknown ID \"UNKNOWN_ID\"",
        action=action_update_model_attribute_with_unknown_id
    ),
    ValidationTest(
        name="Updating unknown model attribute",
        expected_error_message="AppState - model attribute update failed: unknown attribute \"UNKNOWN_ATTRIBUTE\" [ID]",
        action=action_update_unknown_model_attribute
    ),
    ValidationTest(
        name="Selecting model with unknown ID",
        expected_error_message="AppState - model selection failed: unknown ID \"UNKNOWN_ID\"",
        action=action_select_model_with_unknown_id
    ),
    ValidationTest(
        name="Looking up model with unknown ID",
        expected_error_message="AppState - model lookup failed: unknown ID \"UNKNOWN_ID\"",
        action=action_look_up_model_with_unknown_id
    ),
    ValidationTest(
        name="Looking up model bounding box with no model provided",
        expected_error_message="AppState - model bounding box lookup failed: no model provided",
        action=action_look_up_model_bounding_box_with_no_model_provided
    ),
    ValidationTest(
        name="Looking up model group bounding box with no models provided",
        expected_error_message="AppState - model group bounding box lookup failed: no models provided",
        action=action_look_up_model_group_bounding_box_with_no_models_provided
    ),
    ValidationTest(
        name="Handling unsupported attributes panel edit phase",
        expected_error_message="Designer - attributes panel edit failed: unsupported edit phase \"UNSUPPORTED_PHASE\"",
        setup=setup_designer,
        action=action_handle_unsupported_attributes_panel_edit_phase,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Adding widget with unsupported type",
        expected_error_message="WidgetActions - widget creation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        setup=setup_designer,
        action=action_add_widget_with_unsupported_type,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Adding widget with missing coordinates",
        expected_error_message="WidgetActions - widget creation failed: missing coordinates",
        setup=setup_designer,
        action=action_add_widget_with_missing_coordinates,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Adding label with missing text",
        expected_error_message="WidgetActions - widget creation failed: missing text",
        setup=setup_designer,
        action=action_add_label_with_missing_text,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Adding button with missing text",
        expected_error_message="WidgetActions - widget creation failed: missing text",
        setup=setup_designer,
        action=action_add_button_with_missing_text,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Executing EditWidget command without recording final attribute values",
        expected_error_message="EditWidget - execution failed: final attribute values were not recorded",
        action=action_execute_edit_widget_command_without_recording_final_attribute_values
    ),
    ValidationTest(
        name="Executing DragWidgets command without recording final positions",
        expected_error_message="DragWidgets - execution failed: final positions were not recorded",
        action=action_execute_drag_widgets_command_without_recording_final_positions
    ),
    ValidationTest(
        name="Computing spinbox limits for an unsupported attribute",
        expected_error_message="AttributesPanel - spinbox limit computation failed: unsupported attribute \"UNSUPPORTED_ATTRIBUTE\"",
        setup=setup_designer,
        action=action_compute_spinbox_limits_for_unsupported_attribute,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Creating colorpicker for an unsupported attribute",
        expected_error_message="AttributesPanel - colorpicker creation failed: unsupported attribute \"UNSUPPORTED_ATTRIBUTE\"",
        setup=setup_designer,
        action=action_create_colorpicker_for_unsupported_attribute,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Creating combobox for an unsupported attribute",
        expected_error_message="AttributesPanel - combobox creation failed: unsupported attribute \"UNSUPPORTED_ATTRIBUTE\"",
        setup=setup_designer,
        action=action_create_combobox_for_unsupported_attribute,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Subscribing uncallable to EventBus",
        expected_error_message="EventBus - subscription failed: subscriber must be callable [event: EVENT]",
        action=action_subscribe_uncallable_to_event_bus
    ),
    ValidationTest(
        name="Failing handler execution",
        expected_error_message="EventBus - handler execution failed for event \"EVENT\": 1 handler raised an error:\n\t_handler: ERROR",
        action=action_fail_handler_execution
    ),
    ValidationTest(
        name="Deserializing grid data with invalid input type",
        expected_error_message="GridConfig - grid data deserialization failed: grid data is not a dictionary",
        action=action_deserialize_grid_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing grid data with missing required attribute",
        expected_error_message="GridConfig - grid data deserialization failed: missing required attribute \"visible\"",
        action=action_deserialize_grid_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing grid data with invalid attribute set",
        expected_error_message="GridConfig - grid data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        action=action_deserialize_grid_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing grid data with invalid size",
        expected_error_message="GridConfig - grid data deserialization failed: invalid size \"INVALID_SIZE\"",
        action=action_deserialize_grid_data_with_invalid_size
    ),
    ValidationTest(
        name="Deserializing grid data with size outside allowed range",
        expected_error_message=f"GridConfig - grid data deserialization failed: size outside allowed range [expected {MINIMUM_GRID_SIZE} - {MAXIMUM_GRID_SIZE}, got 1]",
        action=action_deserialize_grid_data_with_size_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing grid data with invalid color",
        expected_error_message="GridConfig - grid data deserialization failed: invalid color \"INVALID_COLOR\"",
        action=action_deserialize_grid_data_with_invalid_color
    ),
    ValidationTest(
        name="Deserializing grid data with invalid visibility",
        expected_error_message="GridConfig - grid data deserialization failed: invalid visibility \"INVALID_VISIBILITY\"",
        action=action_deserialize_grid_data_with_invalid_visibility
    ),
    ValidationTest(
        name="Generating ID for an unsupported type",
        expected_error_message="IdCounters - ID generation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        action=action_generate_id_for_unsupported_type
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid input type",
        expected_error_message="IdCounters - ID counter data deserialization failed: ID counter data is not a dictionary",
        action=action_deserialize_id_counter_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing ID counter data with missing required attribute",
        expected_error_message="IdCounters - ID counter data deserialization failed: missing required attribute \"button\"",
        action=action_deserialize_id_counter_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid attribute set",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        action=action_deserialize_id_counter_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid label ID counter value",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid label ID counter value \"INVALID_LABEL_ID_COUNTER_VALUE\"",
        action=action_deserialize_id_counter_data_with_invalid_label_id_counter_value
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid entry ID counter value",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid entry ID counter value \"INVALID_ENTRY_ID_COUNTER_VALUE\"",
        action=action_deserialize_id_counter_data_with_invalid_entry_id_counter_value
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid button ID counter value",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid button ID counter value \"INVALID_BUTTON_ID_COUNTER_VALUE\"",
        action=action_deserialize_id_counter_data_with_invalid_button_id_counter_value
    ),
    ValidationTest(
        name="Deserializing project data with invalid input type",
        expected_error_message="ProjectDocument - project data deserialization failed: project data is not a dictionary",
        action=action_deserialize_project_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing project data with missing required attribute",
        expected_error_message="ProjectDocument - project data deserialization failed: missing required attribute \"id_counters\"",
        action=action_deserialize_project_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing project data with invalid attribute set",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        action=action_deserialize_project_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing project data with invalid version",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid version \"INVALID_VERSION\"",
        action=action_deserialize_project_data_with_invalid_version
    ),
    ValidationTest(
        name="Deserializing project data with unsupported version",
        expected_error_message="ProjectDocument - project data deserialization failed: unsupported version \"2\"",
        action=action_deserialize_project_data_with_unsupported_version
    ),
    ValidationTest(
        name="Deserializing project data with invalid title",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid title \"None\"",
        action=action_deserialize_project_data_with_invalid_title
    ),
    ValidationTest(
        name="Deserializing project data with invalid width",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid width \"INVALID_WIDTH\"",
        action=action_deserialize_project_data_with_invalid_width
    ),
    ValidationTest(
        name="Deserializing project data with invalid height",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid height \"INVALID_HEIGHT\"",
        action=action_deserialize_project_data_with_invalid_height
    ),
    ValidationTest(
        name="Deserializing project data with width outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: width outside allowed range [expected {MINIMUM_CANVAS_WIDTH} - {MAXIMUM_CANVAS_WIDTH}, got {MAXIMUM_CANVAS_WIDTH + 1}]",
        action=action_deserialize_project_data_with_width_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing project data with height outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: height outside allowed range [expected {MINIMUM_CANVAS_HEIGHT} - {MAXIMUM_CANVAS_HEIGHT}, got {MAXIMUM_CANVAS_HEIGHT + 1}]",
        action=action_deserialize_project_data_with_height_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing project data with invalid icon path",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid icon path \"1\"",
        action=action_deserialize_project_data_with_invalid_icon_path
    ),
    ValidationTest(
        name="Deserializing project data with invalid theme type",
        expected_error_message="ProjectDocument - project data deserialization failed: theme is not a dictionary",
        action=action_deserialize_project_data_with_invalid_theme_type
    ),
    ValidationTest(
        name="Deserializing project data with invalid widget data list type",
        expected_error_message="ProjectDocument - project data deserialization failed: widget data is not a list",
        action=action_deserialize_project_data_with_invalid_widget_data_list_type
    ),
    ValidationTest(
        name="Deserializing project data with duplicate widget ID",
        expected_error_message="ProjectDocument - project data deserialization failed: duplicate widget ID \"DUPLICATE_ID\"",
        action=action_deserialize_project_data_with_duplicate_widget_id
    ),
    ValidationTest(
        name="Deserializing project data with widget width exceeding canvas width",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget width exceeds canvas width [{CANVAS_WIDTH + 1} > {CANVAS_WIDTH}, ID: \"ID\"]",
        action=action_deserialize_project_data_with_widget_width_exceeding_canvas_width
    ),
    ValidationTest(
        name="Deserializing project data with widget height exceeding canvas height",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget height exceeds canvas height [{CANVAS_HEIGHT + 1} > {CANVAS_HEIGHT}, ID: \"ID\"]",
        action=action_deserialize_project_data_with_widget_height_exceeding_canvas_height
    ),
    ValidationTest(
        name="Deserializing project data with widget X coordinate outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget X coordinate outside allowed range [expected 0 - {CANVAS_WIDTH - WIDGET_WIDTH}, got {CANVAS_WIDTH - WIDGET_WIDTH + 1}, ID: \"ID\"]",
        action=action_deserialize_project_data_with_widget_x_coordinate_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing project data with widget Y coordinate outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget Y coordinate outside allowed range [expected {WIDGET_HEIGHT} - {CANVAS_HEIGHT}, got {CANVAS_HEIGHT + 1}, ID: \"ID\"]",
        action=action_deserialize_project_data_with_widget_y_coordinate_outside_allowed_range
    ),
    ValidationTest(
        name="Instantiating widget model base type",
        expected_error_message="WidgetModels - widget model creation failed: base type (BaseWidgetData) cannot be instantiated directly",
        action=action_instantiate_widget_model_base_type
    ),
    ValidationTest(
        name="Deserializing widget data with invalid input type",
        expected_error_message="WidgetModels - widget data deserialization failed: widget data is not a dictionary",
        action=action_deserialize_widget_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing widget data with missing type",
        expected_error_message="WidgetModels - widget data deserialization failed: missing required attribute \"type\"",
        action=action_deserialize_widget_data_with_missing_type
    ),
    ValidationTest(
        name="Deserializing widget data with invalid type",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid type \"INVALID_TYPE\"",
        action=action_deserialize_widget_data_with_invalid_type
    ),
    ValidationTest(
        name="Deserializing widget data with missing required attribute",
        expected_error_message="WidgetModels - widget data deserialization failed: missing required attribute \"text\"",
        action=action_deserialize_widget_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing widget data with invalid attribute set",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        action=action_deserialize_widget_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing widget data with invalid ID",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid ID \"None\"",
        action=action_deserialize_widget_data_with_invalid_id
    ),
    ValidationTest(
        name="Deserializing widget data with invalid X coordinate",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid X coordinate \"INVALID_X_COORDINATE\"",
        action=action_deserialize_widget_data_with_invalid_x_coordinate
    ),
    ValidationTest(
        name="Deserializing widget data with invalid Y coordinate",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid Y coordinate \"INVALID_Y_COORDINATE\"",
        action=action_deserialize_widget_data_with_invalid_y_coordinate
    ),
    ValidationTest(
        name="Deserializing widget data with invalid background color",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid background color \"INVALID_BACKGROUND_COLOR\"",
        action=action_deserialize_widget_data_with_invalid_background_color
    ),
    ValidationTest(
        name="Deserializing widget data with invalid foreground color",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid foreground color \"INVALID_FOREGROUND_COLOR\"",
        action=action_deserialize_widget_data_with_invalid_foreground_color
    ),
    ValidationTest(
        name="Deserializing widget data with invalid width",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid width \"INVALID_WIDTH\"",
        action=action_deserialize_widget_data_with_invalid_width
    ),
    ValidationTest(
        name="Deserializing widget data with invalid height",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid height \"INVALID_HEIGHT\"",
        action=action_deserialize_widget_data_with_invalid_height
    ),
    ValidationTest(
        name="Deserializing widget data with invalid anchor",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid anchor \"INVALID_ANCHOR\"",
        action=action_deserialize_widget_data_with_invalid_anchor
    ),
    ValidationTest(
        name="Deserializing widget data with invalid text",
        expected_error_message="WidgetModels - widget data deserialization failed: invalid text \"None\"",
        action=action_deserialize_widget_data_with_invalid_text
    ),
    ValidationTest(
        name="Computing allowed X range with widget width exceeding canvas width",
        expected_error_message="Geometry - computation failed: widget width exceeds canvas width [200 > 100]",
        action=action_compute_allowed_x_range_with_widget_width_exceeding_canvas_width
    ),
    ValidationTest(
        name="Computing allowed X range with invalid anchor",
        expected_error_message="Geometry - computation failed: invalid anchor \"INVALID_ANCHOR\"",
        action=action_compute_allowed_x_range_with_invalid_anchor
    ),
    ValidationTest(
        name="Computing allowed Y range with widget height exceeding canvas height",
        expected_error_message="Geometry - computation failed: widget height exceeds canvas height [200 > 100]",
        action=action_compute_allowed_y_range_with_widget_height_exceeding_canvas_height
    ),
    ValidationTest(
        name="Computing allowed Y range with invalid anchor",
        expected_error_message="Geometry - computation failed: invalid anchor \"INVALID_ANCHOR\"",
        action=action_compute_allowed_y_range_with_invalid_anchor
    ),
    ValidationTest(
        name="Computing bounding box with invalid anchor",
        expected_error_message="Geometry - computation failed: invalid anchor \"INVALID_ANCHOR\"",
        action=action_compute_bounding_box_with_invalid_anchor
    ),
    ValidationTest(
        name="Updating widget with missing position",
        expected_error_message="WidgetView - widget update failed: missing position for model \"ID\"",
        setup=setup_designer,
        action=action_update_widget_with_missing_position,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Updating widget with unknown widget ID",
        expected_error_message=f"WidgetView - widget update failed: unknown widget ID \"{FIRST_WIDGET_ID}\"",
        setup=setup_designer,
        action=action_update_widget_with_unknown_widget_id,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Instantiating widget with unsupported type",
        expected_error_message="WidgetView - widget instantiation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        setup=setup_designer,
        action=action_instantiate_widget_with_unsupported_type,
        teardown=teardown_designer
    ),
    ValidationTest(
        name="Looking up widget with unknown widget ID",
        expected_error_message=f"WidgetView - widget lookup failed: unknown widget ID \"{FIRST_WIDGET_ID}\"",
        setup=setup_designer,
        action=action_look_up_widget_with_unknown_widget_id,
        teardown=teardown_designer
    )
)

if __name__ == "__main__":
    test_results, execution_time_ms = run_validation_tests(VALIDATION_TESTS)
    print_validation_test_results(test_results, execution_time_ms)
