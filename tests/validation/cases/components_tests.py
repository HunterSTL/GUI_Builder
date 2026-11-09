from tests.validation.helpers import create_designer, destroy_designer, create_valid_widget

def test_compute_spinbox_limits_for_unsupported_attribute() -> None:
    designer = create_designer()

    try:
        designer._attributes_panel._compute_spinbox_limits(
            widget=create_valid_widget(),
            attribute="UNSUPPORTED_ATTRIBUTE"
        )
    finally:
        destroy_designer(designer)

def test_create_combobox_for_unsupported_attribute() -> None:
    designer = create_designer()

    try:
        designer._attributes_panel._create_combobox(
            widget=create_valid_widget(),
            attribute="UNSUPPORTED_ATTRIBUTE",
            row=0
        )
    finally:
        destroy_designer(designer)
