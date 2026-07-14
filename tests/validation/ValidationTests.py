import tkinter as tk
from model import ProjectDocument, LabelWidgetData, BaseWidgetData
from view import WidgetView
from controller import WidgetController
from components import AttributesPanel
from events import EventBus
from utility import WidgetType, Geometry
from AppState import AppState
from Designer import Designer
from Theme import USER_THEME, PROGRAM_THEME, CONSTANTS

#Setup------------------------------------------------------------------------------------------------------------------
width, height = 300, 200
root = tk.Tk()
root.withdraw()

project_document = ProjectDocument(
    width=width,
    height=height,
    theme=USER_THEME
)

designer = Designer(
    parent=root,
    project_document=project_document,
    program_theme=PROGRAM_THEME,
    constants=CONSTANTS,
    app_event_bus=EventBus()
)

app_state: AppState = designer.app_state
widget_view: WidgetView = designer.widget_view
widget_controller: WidgetController = designer.widget_controller
attributes_panel: AttributesPanel = designer.attributes_panel
event_bus = EventBus()

#AppState tests---------------------------------------------------------------------------------------------------------
def test_subscribe_uncallable_to_app_state():
    uncallable = "UNCALLABLE"

    #subscribe an uncallable to AppState
    app_state.subscribe(uncallable)

def test_add_model_with_missing_id():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)

    #add model with missing ID to AppState
    app_state.add_model(model)

def test_add_model_with_duplicate_id():
    model1 = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model2 = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model1.id = "label_1"
    model2.id = "label_1"

    try:
        app_state.add_model(model1)
        #add two models with duplicate ID to AppState
        app_state.add_model(model2)
    finally:
        #restore AppState so other tests are not affected
        app_state.remove_model(model1)

def test_remove_model_with_unknown_id():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model.id = "UNKNOWN_ID"

    #remove model with unknown ID from AppState
    app_state.remove_model(model)

def test_update_model_position_absolute_with_unknown_id():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model.id = "UNKNOWN_ID"

    #update model position with unknown ID (absolute)
    app_state.set_model_position(model, 10, 10)

def test_update_model_position_relative_with_unknown_id():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model.id = "UNKNOWN_ID"

    #update model position with unknown ID (relative)
    app_state.offset_model_position(model, 10, 10)

def test_update_unknown_model_attribute():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model.id = "label_1"

    try:
        app_state.add_model(model)
        #update unknown model attribute
        app_state.set_model_attribute(model, "UNKNOWN_ATTRIBUTE", 123)
    finally:
        #restore AppState so other tests are not affected
        app_state.remove_model(model)

def test_update_selection_with_unknown_id():
    #update selection with unknown ID
    app_state.selection_handle_click("UNKNOWN_ID", False)

def test_look_up_model_with_unknown_id():
    #look up model with unknown ID
    app_state.get_model_from_model_id("UNKNOWN_ID")

#WidgetActions tests---------------------------------------------------------------------------------------------------------
def test_create_widget_with_unsupported_type():
    #add widget with unsupported type
    designer.actions.widget.add(
        widget_type="UNSUPPORTED_TYPE",
        coordinates=(50, 50),
        text=None
    )

#AttributesPanel tests----------------------------------------------------------------------------------------
def test_render_attributes_panel_unsupported_type():
    model = LabelWidgetData()
    model.type = "UNSUPPORTED_TYPE"

    #render the panel for a model with unsupported type
    attributes_panel.set_selection(tuple([model]))

def test_compute_spinbox_limits_unsupported_attribute():
    model = LabelWidgetData()

    #compute spinbox limits for an unsupported attribute
    attributes_panel._compute_spinbox_limits(model, "UNSUPPORTED ATTRIBUTE")

#WidgetController tests-------------------------------------------------------------------------------------------------
def test_update_text_missing_widget():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model.id = "label_1"

    try:
        app_state.add_model(model)
        widget_view.delete_widget_for(model.id)
        #update the text of a widget that doesn't exist
        widget_controller.update_widget_attribute(model.id, "text", "value")
    finally:
        #restore AppState so other tests are not affected
        app_state.remove_model(model)

#EventBus tests---------------------------------------------------------------------------------------------------------
def test_subscribe_uncallable_to_event_bus():
    uncallable = "UNCALLABLE"

    #subscribe an uncallable to EventBus
    event_bus.subscribe("EVENT_TEST_UNCALLABLE", uncallable)

def test_fail_handler_execution():
    def fail():
        raise Exception("TEST_EXCEPTION")
    event_bus.subscribe("EVENT_TEST_HANDLER_FAILURE", fail)

    #fail handler execution
    event_bus.emit("EVENT_TEST_HANDLER_FAILURE")

#ProjectDocument tests--------------------------------------------------------------------------------------------------
def test_deserialize_project_invalid_width():
    data = {
        "width": "INVALID_WIDTH"
    }

    #deserialize project with invalid width
    ProjectDocument.from_json(data)

def test_deserialize_project_invalid_height():
    data = {
        "height": "INVALID_HEIGHT"
    }

    #deserialize project with invalid height
    ProjectDocument.from_json(data)

#WidgetModels tests-----------------------------------------------------------------------------------------------------
def test_instantiate_base_type():
    #instantiate base type
    BaseWidgetData(type=WidgetType.LABEL)

def test_deserialize_widget_missing_type():
    data = {
        "x": 10
    }

    #deserialize widget with missing type
    BaseWidgetData.from_dict(data)

def test_deserialize_widget_invalid_type():
    data = {
        "type": "INVALID_TYPE"
    }

    #deserialize widget with invalid type
    BaseWidgetData.from_dict(data)

def test_deserialize_widget_unsupported_type():
    from model.WidgetModels import _WIDGET_CLASSES

    #temporarily remove Label from the dictionary mapping supported types
    label_type = _WIDGET_CLASSES.pop(WidgetType.LABEL, None)

    try:
        data = {
            "type": "Label"
        }

        #deserialize widget with unsupported type
        BaseWidgetData.from_dict(data)
    finally:
        #restore mapping so other tests are not affected
        _WIDGET_CLASSES[WidgetType.LABEL] = label_type

def test_deserialize_widget_invalid_attribute_set():
    data = {
        "type": "Label",
        "x": 10,
        "y": 20,
        "INVALID_ATTRIBUTE": 123
    }

    #deserialize widget with invalid attribute set
    BaseWidgetData.from_dict(data)

#Geometry tests---------------------------------------------------------------------------------------------------------
def test_compute_bounding_box_missing_x():
    #compute bounding box with missing x coordinate
    Geometry.compute_model_bounding_box(None, 0, 50, 20, "sw")

def test_compute_bounding_box_missing_y():
    #compute bounding box with missing y coordinate
    Geometry.compute_model_bounding_box(0, None, 50, 20, "sw")

def test_compute_bounding_box_missing_width():
    #compute bounding box with missing width
    Geometry.compute_model_bounding_box(0, 0, None, 20, "sw")

def test_compute_bounding_box_missing_height():
    #compute bounding box with missing height
    Geometry.compute_model_bounding_box(0, 0, 50, None, "sw")

def test_compute_bounding_box_invalid_anchor():
    #compute bounding box with invalid anchor
    Geometry.compute_model_bounding_box(0, 0, 50, 20, "INVALID_ANCHOR")

#WidgetView tests-------------------------------------------------------------------------------------------------------
def test_create_widget_unsupported_type():
    model = LabelWidgetData(x=0, y=0, anchor="sw", width=50, height=20)
    model.type = "UNSUPPORTED_TYPE"

    #create widget with unsupported type
    widget_view.update_widget_for(model)

def test_update_widget_missing_position():
    model = LabelWidgetData()
    model.id = "label_1"

    #update a widget with missing position attributes
    widget_view.update_widget_for(model)

def test_update_widget_unknown_widget_id():
    model = LabelWidgetData(x=0, y=0)
    model.id = "label_1"

    try:
        widget_view.update_widget_for(model)
        widget_id = widget_view.get_widget_id_from_model_id(model.id)
        widget_view.widget_map[widget_id] = None
        #update widget with unknown widget ID (no entry in widget_map)
        widget_view.update_widget_for(model)
    finally:
        #restore WidgetView so other tests are not affected
        widget_view.delete_widget_for(model.id)

def test_look_up_widget_unknown_widget_id():
    model = LabelWidgetData(x=0, y=0)
    model.id = "label_1"

    try:
        widget_view.update_widget_for(model)
        widget_id = widget_view.get_widget_id_from_model_id(model.id)
        widget_view.widget_map[widget_id] = None
        #look up widget with unknown widget ID
        widget_view.get_widget_from_model_id(model.id)
    finally:
        #restore WidgetView so other tests are not affected
        widget_view.delete_widget_for(model.id)

#Testing----------------------------------------------------------------------------------------------------------------
def compute_max_test_case_name_length() -> int:
    max_test_case_length = 0
    for name, test_group in TEST_GROUPS.items():
        for test_case_name in test_group.keys():
            max_test_case_length = max(max_test_case_length, len(test_case_name))
    return max_test_case_length

def run_test(function):
    try:
        function()
    except ValueError as e:
        return "[OK]", str(e)
    except Exception as e:
        return "[FAIL]", f"Wrong exception: {e}"
    else:
        return "[FAIL]", "No error raised"

def run_test_group(test_group: dict, max_test_case_name_length: int):
    for test_case, function in test_group.items():
        success, result = run_test(function)
        print(success + "\t" + test_case + " " * (max_test_case_name_length - len(test_case)) + "\t\t" + result)
    print("-" * 200)

def run_all_test_groups():
    max_test_case_name_length = compute_max_test_case_name_length()

    print("-" * 200)
    print(f"Running validation tests")
    print("-" * 200)
    print("Status\tTest case" + " " * (max_test_case_name_length - 9) + "\t\t" + "Result")
    print("-" * 200)

    for name, test_group in TEST_GROUPS.items():
        run_test_group(test_group, max_test_case_name_length)

    print("Done")
    print("-" * 200)

APP_STATE_TESTS = {
    "Subscribing uncallable to AppState": test_subscribe_uncallable_to_app_state,
    "Adding model with missing ID to AppState": test_add_model_with_missing_id,
    "Adding model with duplicate ID to AppState": test_add_model_with_duplicate_id,
    "Removing model with unknown ID from AppState": test_remove_model_with_unknown_id,
    "Updating model position (absolute) with unknown ID": test_update_model_position_absolute_with_unknown_id,
    "Updating model position (relative) with unknown ID": test_update_model_position_relative_with_unknown_id,
    "Updating unknown model attribute": test_update_unknown_model_attribute,
    "Updating selection with unknown ID": test_update_selection_with_unknown_id,
    "Looking up model with unknown ID": test_look_up_model_with_unknown_id
}

WIDGET_ACTIONS_TESTS = {
    "Adding widget with unsupported type": test_create_widget_with_unsupported_type
}

ATTRIBUTES_PANEL_TESTS = {
    "Rendering attributes panel for a model with unsupported type": test_render_attributes_panel_unsupported_type,
    "Computing spinbox limits for an unsupported attribute": test_compute_spinbox_limits_unsupported_attribute
}

WIDGET_CONTROLLER_TESTS = {
    "Updating the text of a widget that doesn't exist": test_update_text_missing_widget
}

EVENT_BUS_TESTS = {
    "Subscribing uncallable to EventBus": test_subscribe_uncallable_to_event_bus,
    "Failing handler execution": test_fail_handler_execution
}

PROJECT_DOCUMENT_TESTS = {
    "Deserializing project with invalid width": test_deserialize_project_invalid_width,
    "Deserializing project with invalid height": test_deserialize_project_invalid_height
}

WIDGET_MODELS_TESTS = {
    "Instantiating base type": test_instantiate_base_type,
    "Deserializing widget with missing type": test_deserialize_widget_missing_type,
    "Deserializing widget with invalid type": test_deserialize_widget_invalid_type,
    "Deserializing widget with unsupported type": test_deserialize_widget_unsupported_type,
    "Deserializing widget with invalid attribute set": test_deserialize_widget_invalid_attribute_set
}

GEOMETRY_TESTS = {
    "Computing bounding box with missing x coordinate": test_compute_bounding_box_missing_x,
    "Computing bounding box with missing y coordinate": test_compute_bounding_box_missing_y,
    "Computing bounding box with missing width": test_compute_bounding_box_missing_width,
    "Computing bounding box with missing height": test_compute_bounding_box_missing_height,
    "Computing bounding box with invalid anchor": test_compute_bounding_box_invalid_anchor
}

WIDGET_VIEW_TESTS = {
    "Creating widget with unsupported type": test_create_widget_unsupported_type,
    "Updating widget with missing position": test_update_widget_missing_position,
    "Updating widget with unknown widget ID": test_update_widget_unknown_widget_id,
    "Looking up widget with unknown widget ID": test_look_up_widget_unknown_widget_id
}

TEST_GROUPS = {
    "AppState": APP_STATE_TESTS,
    "WidgetActions": WIDGET_ACTIONS_TESTS,
    "AttributesPanelController": ATTRIBUTES_PANEL_TESTS,
    "WidgetController": WIDGET_CONTROLLER_TESTS,
    "EventBus": EVENT_BUS_TESTS,
    "ProjectDocument": PROJECT_DOCUMENT_TESTS,
    "WidgetModels": WIDGET_MODELS_TESTS,
    "Geometry": GEOMETRY_TESTS,
    "WidgetView": WIDGET_VIEW_TESTS
}

run_all_test_groups()
