from tests.validation.Helpers import (
    create_valid_project_data,
    create_valid_widget_data,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    WIDGET_WIDTH
)

from model import GridConfig, IdCounters, ProjectDocument, ProjectTheme, BaseWidget
from utility.Constants import CANVAS_MAX_WIDTH, CANVAS_MAX_HEIGHT

def test_deserialize_grid_data_with_invalid_input_type() -> None:
    GridConfig.from_dict(grid_data=[])

def test_deserialize_grid_data_with_missing_required_attribute() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "#ffffff"
        }
    )

def test_deserialize_grid_data_with_invalid_attribute_set() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "#ffffff",
            "visible": False,
            "UNEXPECTED_ATTRIBUTE": "value"
        }
    )

def test_deserialize_grid_data_with_invalid_size() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": "INVALID_SIZE",
            "color": "#ffffff",
            "visible": False
        }
    )

def test_deserialize_grid_data_with_size_outside_allowed_range() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 1,
            "color": "#ffffff",
            "visible": False
        }
    )

def test_deserialize_grid_data_with_invalid_color() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "INVALID_COLOR",
            "visible": False
        }
    )

def test_deserialize_grid_data_with_invalid_visibility() -> None:
    GridConfig.from_dict(
        grid_data={
            "size": 10,
            "color": "#ffffff",
            "visible": "INVALID_VISIBILITY"
        }
    )

#IdCounters tests-------------------------------------------------------------------------------------------------------
def test_generate_id_for_unsupported_type() -> None:
    id_counters = IdCounters()
    id_counters.generate_id(widget_type="UNSUPPORTED_TYPE")

def test_deserialize_id_counter_data_with_invalid_input_type() -> None:
    IdCounters.from_dict(id_counter_data=[])

def test_deserialize_id_counter_data_with_missing_required_attribute() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": 1
        }
    )

def test_deserialize_id_counter_data_with_invalid_attribute_set() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": 1,
            "button": 1,
            "UNEXPECTED_ATTRIBUTE": "value"
        }
    )

def test_deserialize_id_counter_data_with_invalid_label_id_counter_value() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": "INVALID_LABEL_ID_COUNTER_VALUE",
            "entry": 1,
            "button": 1
        }
    )

def test_deserialize_id_counter_data_with_invalid_entry_id_counter_value() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": "INVALID_ENTRY_ID_COUNTER_VALUE",
            "button": 1
        }
    )

def test_deserialize_id_counter_data_with_invalid_button_id_counter_value() -> None:
    IdCounters.from_dict(
        id_counter_data={
            "label": 1,
            "entry": 1,
            "button": "INVALID_BUTTON_ID_COUNTER_VALUE"
        }
    )

#ProjectDocument tests--------------------------------------------------------------------------------------------------
def test_deserialize_project_data_with_invalid_input_type() -> None:
    ProjectDocument.from_json([])

def test_deserialize_project_data_with_missing_required_attribute() -> None:
    project_data = create_valid_project_data()
    project_data.pop("id_counters")
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_attribute_set() -> None:
    project_data = create_valid_project_data()
    project_data["UNEXPECTED_ATTRIBUTE"] = "value"
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_version() -> None:
    project_data = create_valid_project_data(version="INVALID_VERSION")
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_unsupported_version() -> None:
    project_data = create_valid_project_data(version=2)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_title() -> None:
    project_data = create_valid_project_data(title=None)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_width() -> None:
    project_data = create_valid_project_data(width="INVALID_WIDTH")
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_height() -> None:
    project_data = create_valid_project_data(height="INVALID_HEIGHT")
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_width_outside_allowed_range() -> None:
    project_data = create_valid_project_data(width=CANVAS_MAX_WIDTH + 1)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_height_outside_allowed_range() -> None:
    project_data = create_valid_project_data(height=CANVAS_MAX_HEIGHT + 1)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_icon_path() -> None:
    project_data = create_valid_project_data(icon_path=1)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_invalid_widget_data_list_type() -> None:
    project_data = create_valid_project_data(widgets={})
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_duplicate_widget_id() -> None:
    widget_data_list = [
        create_valid_widget_data(id="DUPLICATE_ID"),
        create_valid_widget_data(id="DUPLICATE_ID")
    ]
    project_data = create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_widget_width_exceeding_canvas_width() -> None:
    widget_data_list = [
        create_valid_widget_data(width=CANVAS_WIDTH + 1)
    ]
    project_data = create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_widget_height_exceeding_canvas_height() -> None:
    widget_data_list = [
        create_valid_widget_data(height=CANVAS_HEIGHT + 1)
    ]
    project_data = create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_widget_x_coordinate_outside_allowed_range() -> None:
    invalid_x = CANVAS_WIDTH - WIDGET_WIDTH + 1
    widget_data_list = [
        create_valid_widget_data(x=invalid_x)
    ]
    project_data = create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

def test_deserialize_project_data_with_widget_y_coordinate_outside_allowed_range() -> None:
    invalid_y = CANVAS_HEIGHT + 1
    widget_data_list = [
        create_valid_widget_data(y=invalid_y)
    ]
    project_data = create_valid_project_data(widgets=widget_data_list)
    ProjectDocument.from_json(project_data)

#ProjectTheme tests-----------------------------------------------------------------------------------------------------
def test_deserialize_theme_data_with_invalid_input_type() -> None:
    ProjectTheme.from_dict([])

def test_deserialize_theme_data_with_missing_required_attribute() -> None:
    ProjectTheme.from_dict(
        theme_data={
            "background_color": "#000000",
            "label_color": "#000000",
            "label_text_color": "#000000",
            "entry_color": "#000000",
            "entry_text_color": "#000000",
            "button_color": "#000000"
        }
    )

def test_deserialize_theme_data_with_invalid_attribute_set() -> None:
    ProjectTheme.from_dict(
        theme_data={
            "background_color": "#000000",
            "label_color": "#000000",
            "label_text_color": "#000000",
            "entry_color": "#000000",
            "entry_text_color": "#000000",
            "button_color": "#000000",
            "button_text_color": "#000000",
            "UNEXPECTED_ATTRIBUTE": "value"
        }
    )

def test_deserialize_theme_data_with_invalid_color() -> None:
    ProjectTheme.from_dict(
        theme_data={
            "background_color": "INVALID_COLOR",
            "label_color": "#000000",
            "label_text_color": "#000000",
            "entry_color": "#000000",
            "entry_text_color": "#000000",
            "button_color": "#000000",
            "button_text_color": "#000000"
        }
    )

#Widget tests-----------------------------------------------------------------------------------------------------------
def test_instantiate_widget_base_type() -> None:
    widget_data = create_valid_widget_data()
    widget_data.pop("type")
    widget_data.pop("text")
    BaseWidget(**widget_data)

def test_deserialize_widget_data_with_invalid_input_type() -> None:
    BaseWidget.from_dict(widget_data=[])

def test_deserialize_widget_data_with_missing_type() -> None:
    widget_data = create_valid_widget_data()
    widget_data.pop("type")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_type() -> None:
    widget_data = create_valid_widget_data(type="INVALID_TYPE")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_missing_required_attribute() -> None:
    widget_data = create_valid_widget_data()
    widget_data.pop("text")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_attribute_set() -> None:
    widget_data = create_valid_widget_data()
    widget_data["UNEXPECTED_ATTRIBUTE"] = "value"
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_x_coordinate() -> None:
    widget_data = create_valid_widget_data(x="INVALID_X_COORDINATE")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_y_coordinate() -> None:
    widget_data = create_valid_widget_data(y="INVALID_Y_COORDINATE")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_background_color() -> None:
    widget_data = create_valid_widget_data(bg="INVALID_BACKGROUND_COLOR")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_foreground_color() -> None:
    widget_data = create_valid_widget_data(fg="INVALID_FOREGROUND_COLOR")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_width() -> None:
    widget_data = create_valid_widget_data(width="INVALID_WIDTH")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_height() -> None:
    widget_data = create_valid_widget_data(height="INVALID_HEIGHT")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_anchor() -> None:
    widget_data = create_valid_widget_data(anchor="INVALID_ANCHOR")
    BaseWidget.from_dict(widget_data)

def test_deserialize_widget_data_with_invalid_text() -> None:
    widget_data = create_valid_widget_data(text=None)
    BaseWidget.from_dict(widget_data)
