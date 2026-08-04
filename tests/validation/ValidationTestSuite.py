import sys
from pathlib import Path
from ValidationFramework import ValidationTest, run_validation_tests, print_validation_test_results

sys.path.insert(0, str(Path(__file__).parent.parent.parent))    #GUI_Builder/

import tkinter as tk
from commands import EditWidget, MoveWidgetsTo
from events import EventBus
from model import ProjectDocument, LabelWidgetData, BaseWidgetData, IdCounters
from utility import WidgetType, Geometry, CONSTANTS
from AppState import AppState
from Designer import Designer
from Theme import USER_THEME, PROGRAM_THEME

FIRST_WIDGET_ID = 2

MINIMUM_CANVAS_WIDTH = CONSTANTS["canvas"]["min_width"]
MINIMUM_CANVAS_HEIGHT = CONSTANTS["canvas"]["min_height"]
MAXIMUM_CANVAS_WIDTH = CONSTANTS["canvas"]["max_width"]
MAXIMUM_CANVAS_HEIGHT = CONSTANTS["canvas"]["max_height"]

#Setup------------------------------------------------------------------------------------------------------------------
def _create_valid_model(**overrides) -> LabelWidgetData:
    model_data = {
        "id": "ID",
        "x": 50,
        "y": 50,
        "bg": "#000000",
        "fg": "#ffffff",
        "width": 100,
        "height": 20,
        "anchor": "sw",
        "text": "TEXT"
    }
    model_data.update(overrides)
    return LabelWidgetData(**model_data)

def setup_app_state() -> dict:
    return {
        "app_state": AppState(ProjectDocument())
    }

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

def setup_edit_widget_command() -> dict:
    return {
        "command": EditWidget(
            model=_create_valid_model(),
            app_state=AppState(ProjectDocument())
        )
    }

def setup_move_widgets_to_command() -> dict:
    return {
        "command": MoveWidgetsTo(
            models=(_create_valid_model(),),
            app_state=AppState(ProjectDocument())
        )
    }

def setup_event_bus() -> dict:
    return {
        "event_bus": EventBus()
    }

def setup_id_counters() -> dict:
    return {
        "id_counters": IdCounters()
    }

#Teardown---------------------------------------------------------------------------------------------------------------
def teardown_designer(designer: Designer) -> None:
    root = designer._parent
    root.destroy()

#AppState tests---------------------------------------------------------------------------------------------------------
def action_subscribe_uncallable_to_app_state(app_state: AppState) -> None:
    app_state.subscribe("UNCALLABLE")

def action_add_model_with_missing_id(app_state: AppState) -> None:
    model = _create_valid_model(id=None)
    app_state.add_model(model)

def action_add_model_with_duplicate_id(app_state: AppState) -> None:
    model_1 = _create_valid_model(id="DUPLICATE_ID")
    model_2 = _create_valid_model(id="DUPLICATE_ID")
    app_state.add_model(model_1)
    app_state.add_model(model_2)

def action_remove_model_with_unknown_id(app_state: AppState) -> None:
    model = _create_valid_model(id="UNKNOWN_ID")
    app_state.remove_model(model)

def action_update_model_position_absolute_with_unknown_id(app_state: AppState) -> None:
    model = _create_valid_model(id="UNKNOWN_ID")
    app_state.set_model_position(model, 100, 100)

def action_update_model_position_relative_with_unknown_id(app_state: AppState) -> None:
    model = _create_valid_model(id="UNKNOWN_ID")
    app_state.offset_model_position(model, 10, 10)

def action_update_model_attribute_with_unknown_id(app_state: AppState) -> None:
    model = _create_valid_model(id="UNKNOWN_ID")
    app_state.set_model_attribute(model, "x", 0)

def action_update_unknown_model_attribute(app_state: AppState) -> None:
    model = _create_valid_model()
    app_state.add_model(model)
    app_state.set_model_attribute(model, "UNKNOWN_ATTRIBUTE", "VALUE")

def action_select_model_with_unknown_id(app_state: AppState) -> None:
    app_state.selection_handle_click(model_id="UNKNOWN_ID", is_additive=False)

def action_look_up_model_with_unknown_id(app_state: AppState) -> None:
    app_state.get_model_from_model_id("UNKNOWN_ID")

def action_look_up_model_bounding_box_with_no_model_provided(app_state: AppState) -> None:
    app_state.get_model_bounding_box(None)

def action_look_up_model_group_bounding_box_with_no_models_provided(app_state: AppState) -> None:
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
def action_execute_edit_widget_command_without_recording_final_attribute_values(command: EditWidget) -> None:
    command.execute()

#MoveWidgetsTo command tests--------------------------------------------------------------------------------------------
def action_execute_move_widget_to_command_without_recording_final_positions(command: MoveWidgetsTo) -> None:
    command.execute()

#AttributesPanel tests--------------------------------------------------------------------------------------------------
def action_compute_spinbox_limits_for_unsupported_attribute(designer: Designer) -> None:
    designer._attributes_panel._compute_spinbox_limits(
        model=_create_valid_model(),
        attribute="UNSUPPORTED_ATTRIBUTE"
    )

def action_create_colorpicker_for_unsupported_attribute(designer: Designer) -> None:
    designer._attributes_panel._create_colorpicker(
        model=_create_valid_model(),
        attribute="UNSUPPORTED_ATTRIBUTE",
        row=0
    )

def action_create_combobox_for_unsupported_attribute(designer: Designer) -> None:
    designer._attributes_panel._create_combobox(
        model=_create_valid_model(),
        attribute="UNSUPPORTED_ATTRIBUTE",
        row=0
    )


#EventBus tests---------------------------------------------------------------------------------------------------------
def action_subscribe_uncallable_to_event_bus(event_bus: EventBus) -> None:
    event_bus.subscribe("EVENT", "UNCALLABLE")

def action_fail_handler_execution(event_bus: EventBus) -> None:
    def _handler() -> None:
        raise ValueError("ERROR")

    event_bus.subscribe("EVENT", _handler)
    event_bus.emit("EVENT")

#IdCounters tests-------------------------------------------------------------------------------------------------------
def action_generate_id_for_unsupported_type(id_counters: IdCounters) -> None:
    id_counters.generate_id("UNSUPPORTED_TYPE")

#ProjectDocument tests--------------------------------------------------------------------------------------------------
def action_deserialize_project_with_invalid_width() -> None:
    ProjectDocument.from_json({"width": "INVALID_WIDTH"})

def action_deserialize_project_with_invalid_height() -> None:
    ProjectDocument.from_json({"height": "INVALID_HEIGHT"})

def action_deserialize_project_with_width_below_minimum() -> None:
    ProjectDocument.from_json({"width": MINIMUM_CANVAS_WIDTH - 1})

def action_deserialize_project_with_height_below_minimum() -> None:
    ProjectDocument.from_json({"height": MINIMUM_CANVAS_HEIGHT - 1})

def action_deserialize_project_with_width_above_maximum() -> None:
    ProjectDocument.from_json({"width": MAXIMUM_CANVAS_WIDTH + 1})

def action_deserialize_project_with_height_above_maximum() -> None:
    ProjectDocument.from_json({"height": MAXIMUM_CANVAS_HEIGHT + 1})

#WidgetModel tests------------------------------------------------------------------------------------------------------
def action_instantiate_base_type() -> None:
    BaseWidgetData(
        id="ID",
        x=0,
        y=0,
        bg="",
        fg="",
        width=0,
        height=0
    )

def action_deserialize_widget_with_missing_type() -> None:
    BaseWidgetData.from_dict({})

def action_deserialize_widget_with_invalid_type() -> None:
    BaseWidgetData.from_dict({"type": "INVALID_TYPE"})

def action_deserialize_widget_with_unsupported_type() -> None:
    from model.WidgetModels import _WIDGET_CLASSES

    #temporarily remove Label from the dictionary mapping supported types
    label_type = _WIDGET_CLASSES.pop(WidgetType.LABEL, None)

    try:
        BaseWidgetData.from_dict({"type": "Label"})
    finally:
        #restore mapping so other tests are not affected
        _WIDGET_CLASSES[WidgetType.LABEL] = label_type

def action_deserialize_widget_with_invalid_attribute_set() -> None:
    BaseWidgetData.from_dict({"type": "Label", "INVALID_ATTRIBUTE": 0})

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
    model = _create_valid_model(x=None, y=None)
    designer._widget_view.update_widget_for(model)

def action_update_widget_with_unknown_widget_id(designer: Designer) -> None:
    model = _create_valid_model()
    designer._widget_view.update_widget_for(model)
    widget_id = designer._widget_view.get_widget_id_from_model_id(model.id)
    designer._widget_view.widget_map[widget_id] = None
    designer._widget_view.update_widget_for(model)

def action_instantiate_widget_with_unsupported_type(designer: Designer) -> None:
    designer._widget_view._instantiate_widget("UNSUPPORTED_TYPE")

def action_look_up_widget_with_unknown_widget_id(designer: Designer) -> None:
    model = _create_valid_model()
    designer._widget_view.update_widget_for(model)
    widget_id = designer._widget_view.get_widget_id_from_model_id(model.id)
    designer._widget_view.widget_map[widget_id] = None
    designer._widget_view.get_widget_from_model_id(model.id)

VALIDATION_TESTS = (
    ValidationTest(
        name="Subscribing uncallable to AppState",
        expected_error_message="AppState - subscription failed: subscriber must be callable",
        setup=setup_app_state,
        action=action_subscribe_uncallable_to_app_state
    ),
    ValidationTest(
        name="Adding model with missing ID to AppState",
        expected_error_message="AppState - model addition failed: missing ID",
        setup=setup_app_state,
        action=action_add_model_with_missing_id
    ),
    ValidationTest(
        name="Adding model with duplicate ID to AppState",
        expected_error_message="AppState - model addition failed: duplicate ID \"DUPLICATE_ID\"",
        setup=setup_app_state,
        action=action_add_model_with_duplicate_id
    ),
    ValidationTest(
        name="Removing model with unknown ID from AppState",
        expected_error_message="AppState - model removal failed: unknown ID \"UNKNOWN_ID\"",
        setup=setup_app_state,
        action=action_remove_model_with_unknown_id
    ),
    ValidationTest(
        name="Updating model position (absolute) with unknown ID",
        expected_error_message="AppState - model position update failed: unknown ID \"UNKNOWN_ID\"",
        setup=setup_app_state,
        action=action_update_model_position_absolute_with_unknown_id
    ),
    ValidationTest(
        name="Updating model position (relative) with unknown ID",
        expected_error_message="AppState - model position update failed: unknown ID \"UNKNOWN_ID\"",
        setup=setup_app_state,
        action=action_update_model_position_relative_with_unknown_id
    ),
    ValidationTest(
        name="Updating model attribute with unknown ID",
        expected_error_message="AppState - model attribute update failed: unknown ID \"UNKNOWN_ID\"",
        setup=setup_app_state,
        action=action_update_model_attribute_with_unknown_id
    ),
    ValidationTest(
        name="Updating unknown model attribute",
        expected_error_message="AppState - model attribute update failed: unknown attribute \"UNKNOWN_ATTRIBUTE\" [ID]",
        setup=setup_app_state,
        action=action_update_unknown_model_attribute
    ),
    ValidationTest(
        name="Selecting model with unknown ID",
        expected_error_message="AppState - model selection failed: unknown ID \"UNKNOWN_ID\"",
        setup=setup_app_state,
        action=action_select_model_with_unknown_id
    ),
    ValidationTest(
        name="Looking up model with unknown ID",
        expected_error_message="AppState - model lookup failed: unknown ID \"UNKNOWN_ID\"",
        setup=setup_app_state,
        action=action_look_up_model_with_unknown_id
    ),
    ValidationTest(
        name="Looking up model bounding box with no model provided",
        expected_error_message="AppState - model bounding box lookup failed: no model provided",
        setup=setup_app_state,
        action=action_look_up_model_bounding_box_with_no_model_provided
    ),
    ValidationTest(
        name="Looking up model group bounding box with no models provided",
        expected_error_message="AppState - model group bounding box lookup failed: no models provided",
        setup=setup_app_state,
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
        setup=setup_edit_widget_command,
        action=action_execute_edit_widget_command_without_recording_final_attribute_values
    ),
    ValidationTest(
        name="Executing MoveWidgetsTo command without recording final positions",
        expected_error_message="MoveWidgetsTo - execution failed: final positions were not recorded",
        setup=setup_move_widgets_to_command,
        action=action_execute_move_widget_to_command_without_recording_final_positions
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
        setup=setup_event_bus,
        action=action_subscribe_uncallable_to_event_bus
    ),
    ValidationTest(
        name="Failing handler execution",
        expected_error_message="EventBus - handler execution failed for event \"EVENT\": 1 handler raised an error:\n\t_handler: ERROR",
        setup=setup_event_bus,
        action=action_fail_handler_execution
    ),
    ValidationTest(
        name="Generating ID for an unsupported type",
        expected_error_message="IdCounters - ID generation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        setup=setup_id_counters,
        action=action_generate_id_for_unsupported_type
    ),
    ValidationTest(
        name="Deserializing project with invalid width",
        expected_error_message="ProjectDocument - deserialization failed: width must be an integer [got \"INVALID_WIDTH\"]",
        action=action_deserialize_project_with_invalid_width
    ),
    ValidationTest(
        name="Deserializing project with invalid height",
        expected_error_message="ProjectDocument - deserialization failed: height must be an integer [got \"INVALID_HEIGHT\"]",
        action=action_deserialize_project_with_invalid_height
    ),
    ValidationTest(
        name="Deserializing project with width below minimum",
        expected_error_message=f"ProjectDocument - deserialization failed: width below minimum of {MINIMUM_CANVAS_WIDTH} [got {MINIMUM_CANVAS_WIDTH - 1}]",
        action=action_deserialize_project_with_width_below_minimum
    ),
    ValidationTest(
        name="Deserializing project with height below minimum",
        expected_error_message=f"ProjectDocument - deserialization failed: height below minimum of {MINIMUM_CANVAS_HEIGHT} [got {MINIMUM_CANVAS_HEIGHT - 1}]",
        action=action_deserialize_project_with_height_below_minimum
    ),
    ValidationTest(
        name="Deserializing project with width above maximum",
        expected_error_message=f"ProjectDocument - deserialization failed: width above maximum of {MAXIMUM_CANVAS_WIDTH} [got {MAXIMUM_CANVAS_WIDTH + 1}]",
        action=action_deserialize_project_with_width_above_maximum
    ),
    ValidationTest(
        name="Deserializing project with height above maximum",
        expected_error_message=f"ProjectDocument - deserialization failed: height above maximum of {MAXIMUM_CANVAS_HEIGHT} [got {MAXIMUM_CANVAS_HEIGHT + 1}]",
        action=action_deserialize_project_with_height_above_maximum
    ),
    ValidationTest(
        name="Instantiating base type",
        expected_error_message="WidgetModels - model creation failed: base type (BaseWidgetData) cannot be instantiated directly",
        action=action_instantiate_base_type
    ),
    ValidationTest(
        name="Deserializing widget with missing type",
        expected_error_message="WidgetModels - model deserialization failed: missing required attribute \"type\"",
        action=action_deserialize_widget_with_missing_type
    ),
    ValidationTest(
        name="Deserializing widget with invalid type",
        expected_error_message="WidgetModels - model deserialization failed: invalid type \"INVALID_TYPE\"",
        action=action_deserialize_widget_with_invalid_type
    ),
    ValidationTest(
        name="Deserializing widget with unsupported type",
        expected_error_message="WidgetModels - model deserialization failed: unsupported type \"Label\"",
        action=action_deserialize_widget_with_unsupported_type
    ),
    ValidationTest(
        name="Deserializing widget with invalid attribute set",
        expected_error_message="WidgetModels - model deserialization failed: invalid attribute set for type \"Label\" [LabelWidgetData.__init__() got an unexpected keyword argument 'INVALID_ATTRIBUTE']",
        action=action_deserialize_widget_with_invalid_attribute_set
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
