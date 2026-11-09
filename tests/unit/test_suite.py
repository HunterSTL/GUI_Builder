from tests.unit.framework import (
    UnitTest,
    run_unit_tests,
    print_unit_test_results
)

from tests.unit.cases.model_tests import (
    test_project_document_roundtrip
)

from tests.unit.cases.commands_tests import (
    test_add_widget,
    test_align_widgets,
    test_delete_widgets,
    test_drag_widgets,
    test_edit_widget,
    test_nudge_widgets,
    test_paste_widgets_from_clipboard,
    test_set_grid_color,
    test_set_grid_size,
    test_set_project_title,
    test_snap_widgets_to_grid,
    test_toggle_grid
)

UNIT_TESTS = (
    UnitTest(
        name="ProjectDocument roundtrip",
        case=test_project_document_roundtrip
    ),
    UnitTest(
        name="AddWidget",
        case=test_add_widget
    ),
    UnitTest(
        name="AlignWidgets",
        case=test_align_widgets
    ),
    UnitTest(
        name="DeleteWidgets",
        case=test_delete_widgets
    ),
    UnitTest(
        name="DragWidgets",
        case=test_drag_widgets
    ),
    UnitTest(
        name="EditWidget",
        case=test_edit_widget
    ),
    UnitTest(
        name="NudgeWidgets",
        case=test_nudge_widgets
    ),
    UnitTest(
        name="PasteWidgetsFromClipboard",
        case=test_paste_widgets_from_clipboard
    ),
    UnitTest(
        name="SetGridColor",
        case=test_set_grid_color
    ),
    UnitTest(
        name="SetGridSize",
        case=test_set_grid_size
    ),
    UnitTest(
        name="SetProjectTitle",
        case=test_set_project_title
    ),
    UnitTest(
        name="SnapWidgetsToGrid",
        case=test_snap_widgets_to_grid
    ),
    UnitTest(
        name="ToggleGrid",
        case=test_toggle_grid
    )
)

def run() -> None:
    print("Running unit tests")
    test_results, execution_time_ms = run_unit_tests(UNIT_TESTS)
    print_unit_test_results(test_results, execution_time_ms)
