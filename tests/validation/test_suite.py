from tests.validation.cases.actions_tests import (
    test_add_button_with_missing_text,
    test_add_label_with_missing_text,
    test_add_widget_with_missing_coordinates,
    test_add_widget_with_unsupported_type
)
from tests.validation.cases.app_state_tests import (
    test_add_widget_with_duplicate_id,
    test_add_widget_with_missing_id,
    test_look_up_widget_bounding_box_with_no_widget_provided,
    test_look_up_widget_group_bounding_box_with_no_widgets_provided,
    test_look_up_widget_with_unknown_id,
    test_remove_widget_with_unknown_id,
    test_select_widget_with_unknown_id,
    test_subscribe_uncallable_to_app_state,
    test_update_unknown_widget_attribute,
    test_update_widget_attribute_with_unknown_id,
    test_update_widget_position_absolute_with_unknown_id,
    test_update_widget_position_relative_with_unknown_id
)
from tests.validation.cases.commands_tests import (
    test_check_drag_widgets_command_effect_without_recording_final_positions,
    test_execute_drag_widgets_command_without_recording_final_positions,
    test_execute_edit_widget_command_without_recording_final_attribute_values
)
from tests.validation.cases.components_tests import (
    test_compute_spinbox_limits_for_unsupported_attribute,
    test_create_combobox_for_unsupported_attribute
)
from tests.validation.cases.events_tests import (
    test_fail_handler_execution,
    test_subscribe_uncallable_to_event_bus
)
from tests.validation.cases.model_tests import (
    test_deserialize_grid_data_with_invalid_attribute_set,
    test_deserialize_grid_data_with_invalid_color,
    test_deserialize_grid_data_with_invalid_input_type,
    test_deserialize_grid_data_with_invalid_size,
    test_deserialize_grid_data_with_invalid_visibility,
    test_deserialize_grid_data_with_missing_required_attribute,
    test_deserialize_grid_data_with_size_outside_allowed_range,
    test_deserialize_id_counter_data_with_invalid_attribute_set,
    test_deserialize_id_counter_data_with_invalid_button_id_counter_value,
    test_deserialize_id_counter_data_with_invalid_entry_id_counter_value,
    test_deserialize_id_counter_data_with_invalid_input_type,
    test_deserialize_id_counter_data_with_invalid_label_id_counter_value,
    test_deserialize_id_counter_data_with_missing_required_attribute,
    test_deserialize_project_data_with_duplicate_widget_id,
    test_deserialize_project_data_with_height_outside_allowed_range,
    test_deserialize_project_data_with_invalid_attribute_set,
    test_deserialize_project_data_with_invalid_height,
    test_deserialize_project_data_with_invalid_icon_path,
    test_deserialize_project_data_with_invalid_input_type,
    test_deserialize_project_data_with_invalid_title,
    test_deserialize_project_data_with_invalid_version,
    test_deserialize_project_data_with_invalid_width,
    test_deserialize_project_data_with_invalid_widget_data_list_type,
    test_deserialize_project_data_with_missing_required_attribute,
    test_deserialize_project_data_with_unsupported_version,
    test_deserialize_project_data_with_widget_height_exceeding_canvas_height,
    test_deserialize_project_data_with_widget_width_exceeding_canvas_width,
    test_deserialize_project_data_with_widget_x_coordinate_outside_allowed_range,
    test_deserialize_project_data_with_widget_y_coordinate_outside_allowed_range,
    test_deserialize_project_data_with_width_outside_allowed_range,
    test_deserialize_theme_data_with_invalid_attribute_set,
    test_deserialize_theme_data_with_invalid_color,
    test_deserialize_theme_data_with_invalid_input_type,
    test_deserialize_theme_data_with_missing_required_attribute,
    test_deserialize_widget_data_with_invalid_anchor,
    test_deserialize_widget_data_with_invalid_attribute_set,
    test_deserialize_widget_data_with_invalid_background_color,
    test_deserialize_widget_data_with_invalid_foreground_color,
    test_deserialize_widget_data_with_invalid_height,
    test_deserialize_widget_data_with_invalid_input_type,
    test_deserialize_widget_data_with_invalid_text,
    test_deserialize_widget_data_with_invalid_type,
    test_deserialize_widget_data_with_invalid_width,
    test_deserialize_widget_data_with_invalid_x_coordinate,
    test_deserialize_widget_data_with_invalid_y_coordinate,
    test_deserialize_widget_data_with_missing_required_attribute,
    test_deserialize_widget_data_with_missing_type,
    test_generate_id_for_unsupported_type,
    test_instantiate_widget_base_type
)
from tests.validation.cases.utility_tests import (
    test_compute_bounding_box_with_invalid_anchor,
    test_compute_allowed_x_range_with_invalid_anchor,
    test_compute_allowed_x_range_with_widget_width_exceeding_canvas_width,
    test_compute_allowed_y_range_with_invalid_anchor,
    test_compute_allowed_y_range_with_widget_height_exceeding_canvas_height
)
from tests.validation.cases.view_tests import (
    test_delete_tk_widget_with_missing_tk_widget_mapping,
    test_instantiate_widget_with_unsupported_type,
    test_look_up_widget_with_unknown_canvas_item_id,
    test_render_tk_widget_with_missing_tk_widget_mapping
)
from tests.validation.framework import (
    print_validation_test_results,
    run_validation_tests,
    ValidationTest
)
from tests.validation.helpers import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    FIRST_CANVAS_ITEM_ID,
    WIDGET_HEIGHT,
    WIDGET_WIDTH
)
from utility.constants import (
    CANVAS_MAX_HEIGHT,
    CANVAS_MAX_WIDTH,
    CANVAS_MIN_HEIGHT,
    CANVAS_MIN_WIDTH,
    GRID_MAX_SIZE,
    GRID_MIN_SIZE
)

VALIDATION_TESTS = (
    ValidationTest(
        name="Subscribing uncallable to AppState",
        expected_error_message="AppState - subscription failed: subscriber must be callable",
        case=test_subscribe_uncallable_to_app_state
    ),
    ValidationTest(
        name="Adding widget with missing ID to AppState",
        expected_error_message="AppState - widget addition failed: missing widget ID",
        case=test_add_widget_with_missing_id
    ),
    ValidationTest(
        name="Adding widget with duplicate ID to AppState",
        expected_error_message="AppState - widget addition failed: duplicate widget ID \"DUPLICATE_ID\"",
        case=test_add_widget_with_duplicate_id
    ),
    ValidationTest(
        name="Removing widget with unknown ID from AppState",
        expected_error_message="AppState - widget removal failed: unknown widget ID \"UNKNOWN_ID\"",
        case=test_remove_widget_with_unknown_id
    ),
    ValidationTest(
        name="Updating widget position (absolute) with unknown ID",
        expected_error_message="AppState - widget position update failed: unknown widget ID \"UNKNOWN_ID\"",
        case=test_update_widget_position_absolute_with_unknown_id
    ),
    ValidationTest(
        name="Updating widget position (relative) with unknown ID",
        expected_error_message="AppState - widget position update failed: unknown widget ID \"UNKNOWN_ID\"",
        case=test_update_widget_position_relative_with_unknown_id
    ),
    ValidationTest(
        name="Updating widget attribute with unknown ID",
        expected_error_message="AppState - widget attribute update failed: unknown widget ID \"UNKNOWN_ID\"",
        case=test_update_widget_attribute_with_unknown_id
    ),
    ValidationTest(
        name="Updating unknown widget attribute",
        expected_error_message="AppState - widget attribute update failed: unknown attribute \"UNKNOWN_ATTRIBUTE\" [ID]",
        case=test_update_unknown_widget_attribute
    ),
    ValidationTest(
        name="Selecting widget with unknown ID",
        expected_error_message="AppState - widget selection failed: unknown widget ID \"UNKNOWN_ID\"",
        case=test_select_widget_with_unknown_id
    ),
    ValidationTest(
        name="Looking up widget with unknown ID",
        expected_error_message="AppState - widget lookup failed: unknown widget ID \"UNKNOWN_ID\"",
        case=test_look_up_widget_with_unknown_id
    ),
    ValidationTest(
        name="Looking up widget bounding box with no widget provided",
        expected_error_message="AppState - widget bounding box lookup failed: no widget provided",
        case=test_look_up_widget_bounding_box_with_no_widget_provided
    ),
    ValidationTest(
        name="Looking up widget group bounding box with no widgets provided",
        expected_error_message="AppState - widget group bounding box lookup failed: no widgets provided",
        case=test_look_up_widget_group_bounding_box_with_no_widgets_provided
    ),
    ValidationTest(
        name="Adding widget with unsupported type",
        expected_error_message="WidgetActions - widget creation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        case=test_add_widget_with_unsupported_type
    ),
    ValidationTest(
        name="Adding widget with missing coordinates",
        expected_error_message="WidgetActions - widget creation failed: missing coordinates",
        case=test_add_widget_with_missing_coordinates
    ),
    ValidationTest(
        name="Adding label with missing text",
        expected_error_message="WidgetActions - widget creation failed: missing text",
        case=test_add_label_with_missing_text
    ),
    ValidationTest(
        name="Adding button with missing text",
        expected_error_message="WidgetActions - widget creation failed: missing text",
        case=test_add_button_with_missing_text
    ),
    ValidationTest(
        name="Executing EditWidget command without recording final attribute values",
        expected_error_message="EditWidget - execution failed: final attribute values were not recorded",
        case=test_execute_edit_widget_command_without_recording_final_attribute_values
    ),
    ValidationTest(
        name="Checking DragWidgets command effect without recording final positions",
        expected_error_message="DragWidgets - effect check failed: final positions were not recorded",
        case=test_check_drag_widgets_command_effect_without_recording_final_positions
    ),
    ValidationTest(
        name="Executing DragWidgets command without recording final positions",
        expected_error_message="DragWidgets - execution failed: final positions were not recorded",
        case=test_execute_drag_widgets_command_without_recording_final_positions
    ),
    ValidationTest(
        name="Computing spinbox limits for an unsupported attribute",
        expected_error_message="AttributesPanel - spinbox limit computation failed: unsupported attribute \"UNSUPPORTED_ATTRIBUTE\"",
        case=test_compute_spinbox_limits_for_unsupported_attribute
    ),
    ValidationTest(
        name="Creating combobox for an unsupported attribute",
        expected_error_message="AttributesPanel - combobox creation failed: unsupported attribute \"UNSUPPORTED_ATTRIBUTE\"",
        case=test_create_combobox_for_unsupported_attribute
    ),
    ValidationTest(
        name="Subscribing uncallable to EventBus",
        expected_error_message="EventBus - subscription failed: handler must be callable [event: EVENT]",
        case=test_subscribe_uncallable_to_event_bus
    ),
    ValidationTest(
        name="Failing handler execution",
        expected_error_message="EventBus - handler execution failed for event \"EVENT\": ERROR",
        case=test_fail_handler_execution
    ),
    ValidationTest(
        name="Deserializing grid data with invalid input type",
        expected_error_message="GridConfig - grid data deserialization failed: grid data is not a dictionary",
        case=test_deserialize_grid_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing grid data with missing required attribute",
        expected_error_message="GridConfig - grid data deserialization failed: missing required attribute \"visible\"",
        case=test_deserialize_grid_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing grid data with invalid attribute set",
        expected_error_message="GridConfig - grid data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        case=test_deserialize_grid_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing grid data with invalid size",
        expected_error_message="GridConfig - grid data deserialization failed: invalid size \"INVALID_SIZE\"",
        case=test_deserialize_grid_data_with_invalid_size
    ),
    ValidationTest(
        name="Deserializing grid data with size outside allowed range",
        expected_error_message=f"GridConfig - grid data deserialization failed: size outside allowed range [expected {GRID_MIN_SIZE} - {GRID_MAX_SIZE}, got 1]",
        case=test_deserialize_grid_data_with_size_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing grid data with invalid color",
        expected_error_message="GridConfig - grid data deserialization failed: invalid color \"INVALID_COLOR\"",
        case=test_deserialize_grid_data_with_invalid_color
    ),
    ValidationTest(
        name="Deserializing grid data with invalid visibility",
        expected_error_message="GridConfig - grid data deserialization failed: invalid visibility \"INVALID_VISIBILITY\"",
        case=test_deserialize_grid_data_with_invalid_visibility
    ),
    ValidationTest(
        name="Generating ID for an unsupported type",
        expected_error_message="IdCounters - ID generation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        case=test_generate_id_for_unsupported_type
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid input type",
        expected_error_message="IdCounters - ID counter data deserialization failed: ID counter data is not a dictionary",
        case=test_deserialize_id_counter_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing ID counter data with missing required attribute",
        expected_error_message="IdCounters - ID counter data deserialization failed: missing required attribute \"button\"",
        case=test_deserialize_id_counter_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid attribute set",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        case=test_deserialize_id_counter_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid label ID counter value",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid label ID counter value \"INVALID_LABEL_ID_COUNTER_VALUE\"",
        case=test_deserialize_id_counter_data_with_invalid_label_id_counter_value
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid entry ID counter value",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid entry ID counter value \"INVALID_ENTRY_ID_COUNTER_VALUE\"",
        case=test_deserialize_id_counter_data_with_invalid_entry_id_counter_value
    ),
    ValidationTest(
        name="Deserializing ID counter data with invalid button ID counter value",
        expected_error_message="IdCounters - ID counter data deserialization failed: invalid button ID counter value \"INVALID_BUTTON_ID_COUNTER_VALUE\"",
        case=test_deserialize_id_counter_data_with_invalid_button_id_counter_value
    ),
    ValidationTest(
        name="Deserializing project data with invalid input type",
        expected_error_message="ProjectDocument - project data deserialization failed: project data is not a dictionary",
        case=test_deserialize_project_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing project data with missing required attribute",
        expected_error_message="ProjectDocument - project data deserialization failed: missing required attribute \"id_counters\"",
        case=test_deserialize_project_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing project data with invalid attribute set",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        case=test_deserialize_project_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing project data with invalid version",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid version \"INVALID_VERSION\"",
        case=test_deserialize_project_data_with_invalid_version
    ),
    ValidationTest(
        name="Deserializing project data with unsupported version",
        expected_error_message="ProjectDocument - project data deserialization failed: unsupported version \"2\"",
        case=test_deserialize_project_data_with_unsupported_version
    ),
    ValidationTest(
        name="Deserializing project data with invalid title",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid title \"None\"",
        case=test_deserialize_project_data_with_invalid_title
    ),
    ValidationTest(
        name="Deserializing project data with invalid width",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid width \"INVALID_WIDTH\"",
        case=test_deserialize_project_data_with_invalid_width
    ),
    ValidationTest(
        name="Deserializing project data with invalid height",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid height \"INVALID_HEIGHT\"",
        case=test_deserialize_project_data_with_invalid_height
    ),
    ValidationTest(
        name="Deserializing project data with width outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: width outside allowed range [expected {CANVAS_MIN_WIDTH} - {CANVAS_MAX_WIDTH}, got {CANVAS_MAX_WIDTH + 1}]",
        case=test_deserialize_project_data_with_width_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing project data with height outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: height outside allowed range [expected {CANVAS_MIN_HEIGHT} - {CANVAS_MAX_HEIGHT}, got {CANVAS_MAX_HEIGHT + 1}]",
        case=test_deserialize_project_data_with_height_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing project data with invalid icon path",
        expected_error_message="ProjectDocument - project data deserialization failed: invalid icon path \"1\"",
        case=test_deserialize_project_data_with_invalid_icon_path
    ),
    ValidationTest(
        name="Deserializing project data with invalid widget data list type",
        expected_error_message="ProjectDocument - project data deserialization failed: widget data is not a list",
        case=test_deserialize_project_data_with_invalid_widget_data_list_type
    ),
    ValidationTest(
        name="Deserializing project data with duplicate widget ID",
        expected_error_message="ProjectDocument - project data deserialization failed: duplicate widget ID \"DUPLICATE_ID\"",
        case=test_deserialize_project_data_with_duplicate_widget_id
    ),
    ValidationTest(
        name="Deserializing project data with widget width exceeding canvas width",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget width exceeds canvas width [{CANVAS_WIDTH + 1} > {CANVAS_WIDTH}, ID: \"ID\"]",
        case=test_deserialize_project_data_with_widget_width_exceeding_canvas_width
    ),
    ValidationTest(
        name="Deserializing project data with widget height exceeding canvas height",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget height exceeds canvas height [{CANVAS_HEIGHT + 1} > {CANVAS_HEIGHT}, ID: \"ID\"]",
        case=test_deserialize_project_data_with_widget_height_exceeding_canvas_height
    ),
    ValidationTest(
        name="Deserializing project data with widget X coordinate outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget X coordinate outside allowed range [expected 0 - {CANVAS_WIDTH - WIDGET_WIDTH}, got {CANVAS_WIDTH - WIDGET_WIDTH + 1}, ID: \"ID\"]",
        case=test_deserialize_project_data_with_widget_x_coordinate_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing project data with widget Y coordinate outside allowed range",
        expected_error_message=f"ProjectDocument - project data deserialization failed: widget Y coordinate outside allowed range [expected {WIDGET_HEIGHT} - {CANVAS_HEIGHT}, got {CANVAS_HEIGHT + 1}, ID: \"ID\"]",
        case=test_deserialize_project_data_with_widget_y_coordinate_outside_allowed_range
    ),
    ValidationTest(
        name="Deserializing theme data with invalid input type",
        expected_error_message="ProjectTheme - theme data deserialization failed: theme data is not a dictionary",
        case=test_deserialize_theme_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing theme data with missing required attribute",
        expected_error_message="ProjectTheme - theme data deserialization failed: missing required attribute \"button_text_color\"",
        case=test_deserialize_theme_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing theme data with invalid attribute set",
        expected_error_message="ProjectTheme - theme data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        case=test_deserialize_theme_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing theme data with invalid color",
        expected_error_message="ProjectTheme - theme data deserialization failed: invalid background color \"INVALID_COLOR\"",
        case=test_deserialize_theme_data_with_invalid_color
    ),
    ValidationTest(
        name="Instantiating widget base type",
        expected_error_message="Widgets - widget creation failed: base type \"Widget\" cannot be instantiated directly",
        case=test_instantiate_widget_base_type
    ),
    ValidationTest(
        name="Deserializing widget data with invalid input type",
        expected_error_message="Widgets - widget data deserialization failed: widget data is not a dictionary",
        case=test_deserialize_widget_data_with_invalid_input_type
    ),
    ValidationTest(
        name="Deserializing widget data with missing type",
        expected_error_message="Widgets - widget data deserialization failed: missing required attribute \"type\"",
        case=test_deserialize_widget_data_with_missing_type
    ),
    ValidationTest(
        name="Deserializing widget data with invalid type",
        expected_error_message="Widgets - widget data deserialization failed: invalid type \"INVALID_TYPE\"",
        case=test_deserialize_widget_data_with_invalid_type
    ),
    ValidationTest(
        name="Deserializing widget data with missing required attribute",
        expected_error_message="Widgets - widget data deserialization failed: missing required attribute \"text\"",
        case=test_deserialize_widget_data_with_missing_required_attribute
    ),
    ValidationTest(
        name="Deserializing widget data with invalid attribute set",
        expected_error_message="Widgets - widget data deserialization failed: invalid attribute set [got unexpected attribute \"UNEXPECTED_ATTRIBUTE\"]",
        case=test_deserialize_widget_data_with_invalid_attribute_set
    ),
    ValidationTest(
        name="Deserializing widget data with invalid X coordinate",
        expected_error_message="Widgets - widget data deserialization failed: invalid X coordinate \"INVALID_X_COORDINATE\"",
        case=test_deserialize_widget_data_with_invalid_x_coordinate
    ),
    ValidationTest(
        name="Deserializing widget data with invalid Y coordinate",
        expected_error_message="Widgets - widget data deserialization failed: invalid Y coordinate \"INVALID_Y_COORDINATE\"",
        case=test_deserialize_widget_data_with_invalid_y_coordinate
    ),
    ValidationTest(
        name="Deserializing widget data with invalid background color",
        expected_error_message="Widgets - widget data deserialization failed: invalid background color \"INVALID_BACKGROUND_COLOR\"",
        case=test_deserialize_widget_data_with_invalid_background_color
    ),
    ValidationTest(
        name="Deserializing widget data with invalid foreground color",
        expected_error_message="Widgets - widget data deserialization failed: invalid foreground color \"INVALID_FOREGROUND_COLOR\"",
        case=test_deserialize_widget_data_with_invalid_foreground_color
    ),
    ValidationTest(
        name="Deserializing widget data with invalid width",
        expected_error_message="Widgets - widget data deserialization failed: invalid width \"INVALID_WIDTH\"",
        case=test_deserialize_widget_data_with_invalid_width
    ),
    ValidationTest(
        name="Deserializing widget data with invalid height",
        expected_error_message="Widgets - widget data deserialization failed: invalid height \"INVALID_HEIGHT\"",
        case=test_deserialize_widget_data_with_invalid_height
    ),
    ValidationTest(
        name="Deserializing widget data with invalid anchor",
        expected_error_message="Widgets - widget data deserialization failed: invalid anchor \"INVALID_ANCHOR\"",
        case=test_deserialize_widget_data_with_invalid_anchor
    ),
    ValidationTest(
        name="Deserializing widget data with invalid text",
        expected_error_message="Widgets - widget data deserialization failed: invalid text \"None\"",
        case=test_deserialize_widget_data_with_invalid_text
    ),
    ValidationTest(
        name="Computing allowed X range with widget width exceeding canvas width",
        expected_error_message="Geometry - computation failed: widget width exceeds canvas width [200 > 100]",
        case=test_compute_allowed_x_range_with_widget_width_exceeding_canvas_width
    ),
    ValidationTest(
        name="Computing allowed X range with invalid anchor",
        expected_error_message="Geometry - computation failed: invalid anchor \"INVALID_ANCHOR\"",
        case=test_compute_allowed_x_range_with_invalid_anchor
    ),
    ValidationTest(
        name="Computing allowed Y range with widget height exceeding canvas height",
        expected_error_message="Geometry - computation failed: widget height exceeds canvas height [200 > 100]",
        case=test_compute_allowed_y_range_with_widget_height_exceeding_canvas_height
    ),
    ValidationTest(
        name="Computing allowed Y range with invalid anchor",
        expected_error_message="Geometry - computation failed: invalid anchor \"INVALID_ANCHOR\"",
        case=test_compute_allowed_y_range_with_invalid_anchor
    ),
    ValidationTest(
        name="Computing bounding box with invalid anchor",
        expected_error_message="Geometry - computation failed: invalid anchor \"INVALID_ANCHOR\"",
        case=test_compute_bounding_box_with_invalid_anchor
    ),
    ValidationTest(
        name="Deleting Tk widget with missing Tk widget mapping",
        expected_error_message=f"WidgetView - Tk widget deletion failed: missing Tk widget for canvas item \"{FIRST_CANVAS_ITEM_ID}\"",
        case=test_delete_tk_widget_with_missing_tk_widget_mapping
    ),
    ValidationTest(
        name="Looking up widget with unknown canvas item ID",
        expected_error_message=f"WidgetView - widget lookup failed: unknown canvas item ID \"{FIRST_CANVAS_ITEM_ID}\"",
        case=test_look_up_widget_with_unknown_canvas_item_id
    ),
    ValidationTest(
        name="Rendering Tk widget with missing Tk widget mapping",
        expected_error_message=f"WidgetView - Tk widget rendering failed: missing Tk widget for canvas item \"{FIRST_CANVAS_ITEM_ID}\"",
        case=test_render_tk_widget_with_missing_tk_widget_mapping
    ),
    ValidationTest(
        name="Instantiating widget with unsupported type",
        expected_error_message="WidgetView - Tk widget instantiation failed: unsupported type \"UNSUPPORTED_TYPE\"",
        case=test_instantiate_widget_with_unsupported_type
    )
)

def run() -> None:
    print("Running validation tests")
    test_results, execution_time_ms = run_validation_tests(VALIDATION_TESTS)
    print_validation_test_results(test_results, execution_time_ms)
