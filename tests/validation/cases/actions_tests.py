from tests.validation.helpers import create_designer, destroy_designer

from utility.widget_type import WidgetType

def test_add_widget_with_unsupported_type() -> None:
    designer = create_designer()

    try:
        designer._action_groups.widget.add(
            widget_type="UNSUPPORTED_TYPE",
            coordinates=(100, 100),
            text="TEXT"
        )
    finally:
        destroy_designer(designer)

def test_add_widget_with_missing_coordinates() -> None:
    designer = create_designer()

    try:
        designer._action_groups.widget.add(
            widget_type=WidgetType.LABEL,
            coordinates=None,
            text="TEXT"
        )
    finally:
        destroy_designer(designer)

def test_add_label_with_missing_text() -> None:
    designer = create_designer()

    try:
        designer._action_groups.widget.add(
            widget_type=WidgetType.LABEL,
            coordinates=(100, 100),
            text=None
        )
    finally:
        destroy_designer(designer)

def test_add_button_with_missing_text() -> None:
    designer = create_designer()

    try:
        designer._action_groups.widget.add(
            widget_type=WidgetType.BUTTON,
            coordinates=(100, 100),
            text=None
        )
    finally:
        destroy_designer(designer)
