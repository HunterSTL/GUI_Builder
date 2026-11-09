from tests.unit.helpers import create_project, create_project_with_widget
from tests.unit.framework import assert_equal
from utility.constants import GRID_DEFAULT_COLOR, GRID_DEFAULT_SIZE

from commands import (
    AddWidget,
    AlignWidgets,
    DeleteWidgets,
    DragWidgets,
    EditWidget,
    NudgeWidgets,
    PasteWidgetsFromClipboard,
    SetGridColor,
    SetGridSize,
    SetProjectTitle,
    SnapWidgetsToGrid,
    ToggleGrid
)

from model import LabelWidget
from utility import Edge

def test_add_widget() -> None:
    project_document, app_state, command_stack = create_project()

    widget = LabelWidget(
        x=100,
        y=50,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        text="test"
    )

    command_stack.execute(
        AddWidget(
            widget=widget,
            app_state=app_state
        )
    )
    assert_equal(
        actual=len(project_document.widgets),
        expected=1,
        message="Widget was not added to the project"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=2,
        message="IdCounter did not increment"
    )

    command_stack.undo()
    assert_equal(
        actual=len(project_document.widgets),
        expected=0,
        message="Widget addition was not undone"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=1,
        message="IdCounter did not decrement after undo"
    )

    command_stack.redo()
    assert_equal(
        actual=len(project_document.widgets),
        expected=1,
        message="Widget was not added to the project after redo"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=2,
        message="IdCounter did not increment after redo"
    )

def test_align_widgets() -> None:
    project_document, app_state, command_stack = create_project()

    widget_1 = LabelWidget(
        x=100,
        y=50,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        text="test"
    )

    command_stack.execute(
        AddWidget(
            widget=widget_1,
            app_state=app_state
        )
    )

    widget_2 = LabelWidget(
        x=200,
        y=50,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        text="test"
    )

    command_stack.execute(
        AddWidget(
            widget=widget_2,
            app_state=app_state
        )
    )

    widget_3 = LabelWidget(
        x=200,
        y=50,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        anchor="center",
        text="test"
    )

    command_stack.execute(
        AddWidget(
            widget=widget_3,
            app_state=app_state
        )
    )

    app_state.selection_clear()
    app_state.selection_handle_click(widget_id="label_3", is_additive=True)
    app_state.selection_handle_click(widget_id="label_2", is_additive=True)
    app_state.selection_handle_click(widget_id="label_1", is_additive=True)
    assert_equal(
        actual=app_state.get_last_selected_widget_id(),
        expected="label_1",
        message="The last clicked widget is not the last selected widget"
    )

    command_stack.execute(
        AlignWidgets(
            widgets=app_state.get_selected_widgets(),
            reference_widget_id=app_state.get_last_selected_widget_id(),
            edge=Edge.LEFT,
            app_state=app_state
        )
    )
    widget_1 = app_state.get_widget_from_widget_id("label_1")
    widget_2 = app_state.get_widget_from_widget_id("label_2")
    widget_3 = app_state.get_widget_from_widget_id("label_3")
    assert_equal(
        actual=widget_2.x,
        expected=widget_1.x,
        message="Widget \"label_2\" is not aligned with the reference widget"
    )
    assert_equal(
        actual=widget_3.x,
        expected=150,
        message="Widget \"label_3\" is not aligned with the reference widget"
    )

    command_stack.undo()
    assert_equal(
        actual=widget_1.x,
        expected=100,
        message="X-coordinate of widget \"label_1\" has not been restored correctly from undo"
    )
    assert_equal(
        actual=widget_2.x,
        expected=200,
        message="X-coordinate of widget \"label_2\" has not been restored correctly from undo"
    )
    assert_equal(
        actual=widget_3.x,
        expected=200,
        message="X-coordinate of widget \"label_3\" has not been restored correctly from undo"
    )

def test_delete_widgets() -> None:
    project_document, app_state, command_stack = create_project_with_widget()
    widget = app_state.get_widget_from_widget_id("label_1")
    command_stack.execute(
        DeleteWidgets(
            widgets=(widget,),
            app_state=app_state
        )
    )

    assert_equal(
        actual=len(project_document.widgets),
        expected=0,
        message="Widget was not removed from the project"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=2,
        message="IdCounter incorrectly decremented after widget deletion"
    )

    command_stack.undo()
    assert_equal(
        actual=len(project_document.widgets),
        expected=1,
        message="Widget deletion was not undone"
    )

    command_stack.redo()
    assert_equal(
        actual=len(project_document.widgets),
        expected=0,
        message="Widget deletion was not redone"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=2,
        message="IdCounter incorrectly decremented after redoing the widget deletion"
    )

def test_drag_widgets() -> None:
    project_document, app_state, command_stack = create_project_with_widget()
    widget = app_state.get_widget_from_widget_id("label_1")

    cmd = DragWidgets(
        widgets=(widget,),
        app_state=app_state
    )
    cmd.apply_drag_delta(dx=100, dy=50)
    cmd.record_final_positions()
    command_stack.execute(cmd)

    widget = app_state.get_widget_from_widget_id("label_1")
    assert_equal(
        actual=widget.x,
        expected=200,
        message="Drag delta has not been applied correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=100,
        message="Drag delta has not been applied correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=widget.x,
        expected=100,
        message="Drag delta has not been undone correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=50,
        message="Drag delta has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=widget.x,
        expected=200,
        message="Drag delta has not been redone correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=100,
        message="Drag delta has not been redone correctly"
    )

def test_edit_widget() -> None:
    project_document, app_state, command_stack = create_project_with_widget()
    widget = app_state.get_widget_from_widget_id("label_1")

    cmd = EditWidget(
        widget=widget,
        app_state=app_state
    )
    cmd.apply_attribute_changes(
        attribute_changes={
            "x": 200,
            "bg": "#FFFFFF",
            "anchor": "center"
        }
    )
    cmd.record_final_widget_data()
    command_stack.execute(cmd)

    widget = app_state.get_widget_from_widget_id("label_1")
    assert_equal(
        actual=widget.x,
        expected=200,
        message="X-Coordinate has not been applied correctly"
    )
    assert_equal(
        actual=widget.bg,
        expected="#FFFFFF",
        message="Background color has not been applied correctly"
    )
    assert_equal(
        actual=widget.anchor,
        expected="center",
        message="Anchor has not been applied correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=widget.x,
        expected=100,
        message="X-Coordinate has not been undone correctly"
    )
    assert_equal(
        actual=widget.bg,
        expected="#000000",
        message="Background color has not been undone correctly"
    )
    assert_equal(
        actual=widget.anchor,
        expected="sw",
        message="Anchor has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=widget.x,
        expected=200,
        message="X-Coordinate has not been redone correctly"
    )
    assert_equal(
        actual=widget.bg,
        expected="#FFFFFF",
        message="Background color has not been redone correctly"
    )
    assert_equal(
        actual=widget.anchor,
        expected="center",
        message="Anchor has not been redone correctly"
    )

def test_nudge_widgets() -> None:
    project_document, app_state, command_stack = create_project_with_widget()
    widget = app_state.get_widget_from_widget_id("label_1")

    command_stack.execute(
        NudgeWidgets(
            widgets=(widget,),
            dx=100,
            dy=50,
            app_state=app_state
        )
    )

    widget = app_state.get_widget_from_widget_id("label_1")
    assert_equal(
        actual=widget.x,
        expected=200,
        message="Nudge has not been applied correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=100,
        message="Nudge has not been applied correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=widget.x,
        expected=100,
        message="Nudge has not been undone correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=50,
        message="Nudge has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=widget.x,
        expected=200,
        message="Nudge has not been redone correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=100,
        message="Nudge has not been redone correctly"
    )

def test_paste_widgets_from_clipboard() -> None:
    project_document, app_state, command_stack = create_project()

    clipboard = [
        {
            'x': 100,
            'y': 50,
            'bg': '#000000',
            'fg': '#000000',
            'width': 100,
            'height': 20,
            'anchor': 'sw',
            'id': 'label_1',
            'text': 'test',
            'type': 'label'
        }
    ]

    command_stack.execute(
        PasteWidgetsFromClipboard(
            clipboard=clipboard,
            requested_x_offset=100,
            requested_y_offset=0,
            app_state=app_state
        )
    )

    widget = app_state.get_widget_from_widget_id("label_1")
    assert_equal(
        actual=len(project_document.widgets),
        expected=1,
        message="Widget was not added to the project"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=2,
        message="IdCounter did not increment"
    )
    assert_equal(
        actual=widget.x,
        expected=200,
        message="Requested offset has not been applied correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=len(project_document.widgets),
        expected=0,
        message="Widget addition was not undone"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=1,
        message="IdCounter did not decrement after undo"
    )

    command_stack.redo()
    assert_equal(
        actual=len(project_document.widgets),
        expected=1,
        message="Widget was not added to the project after redo"
    )
    assert_equal(
        actual=project_document.id_counters.label,
        expected=2,
        message="IdCounter did not increment after redo"
    )

    command_stack.execute(
        PasteWidgetsFromClipboard(
            clipboard=clipboard,
            requested_x_offset=800,
            requested_y_offset=0,
            app_state=app_state
        )
    )

    widget = app_state.get_widget_from_widget_id("label_2")
    assert_equal(
        actual=widget.x,
        expected=700,
        message="Requested X-offset was not clamped to the project bounds"
    )

def test_set_grid_color() -> None:
    project_document, app_state, command_stack = create_project()

    command_stack.execute(
        SetGridColor(
            new_color="#000000",
            app_state=app_state
        )
    )

    assert_equal(
        actual=app_state.project.grid.color,
        expected="#000000",
        message="Grid color has not been updated correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=app_state.project.grid.color,
        expected=GRID_DEFAULT_COLOR,
        message="Grid color has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=app_state.project.grid.color,
        expected="#000000",
        message="Grid color has not been redone correctly"
    )

def test_set_grid_size() -> None:
    project_document, app_state, command_stack = create_project()

    command_stack.execute(
        SetGridSize(
            new_size=100,
            app_state=app_state
        )
    )

    assert_equal(
        actual=app_state.project.grid.size,
        expected=100,
        message="Grid size has not been updated correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=app_state.project.grid.size,
        expected=GRID_DEFAULT_SIZE,
        message="Grid size has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=app_state.project.grid.size,
        expected=100,
        message="Grid size has not been redone correctly"
    )

def test_set_project_title() -> None:
    project_document, app_state, command_stack = create_project()

    command_stack.execute(
        SetProjectTitle(
            new_title="Title",
            app_state=app_state
        )
    )

    assert_equal(
        actual=app_state.project.title,
        expected="Title",
        message="Project title has not been updated correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=app_state.project.title,
        expected="Untitled Project",
        message="Project title has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=app_state.project.title,
        expected="Title",
        message="Project title has not been redone correctly"
    )

def test_snap_widgets_to_grid() -> None:
    project_document, app_state, command_stack = create_project()

    widget = LabelWidget(
        x=99,
        y=101,
        bg="#000000",
        fg="#000000",
        width=100,
        height=20,
        text="test"
    )

    command_stack.execute(
        AddWidget(
            widget=widget,
            app_state=app_state
        )
    )

    widget = app_state.get_widget_from_widget_id("label_1")

    command_stack.execute(
        SnapWidgetsToGrid(
            widgets=[widget],
            app_state=app_state
        )
    )
    assert_equal(
        actual=widget.x,
        expected=100,
        message="Widget has not been snapped to the grid"
    )
    assert_equal(
        actual=widget.y,
        expected=100,
        message="Widget has not been snapped to the grid"
    )

    command_stack.undo()
    assert_equal(
        actual=widget.x,
        expected=99,
        message="Grid snapping has not been undone correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=101,
        message="Grid snapping has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=widget.x,
        expected=100,
        message="Grid snapping has not been redone correctly"
    )
    assert_equal(
        actual=widget.y,
        expected=100,
        message="Grid snapping has not been redone correctly"
    )

def test_toggle_grid() -> None:
    project_document, app_state, command_stack = create_project()

    command_stack.execute(
        ToggleGrid(
            app_state=app_state
        )
    )

    assert_equal(
        actual=app_state.project.grid.visible,
        expected=True,
        message="Grid visibility has not been toggled correctly"
    )

    command_stack.undo()
    assert_equal(
        actual=app_state.project.grid.visible,
        expected=False,
        message="Grid visibility toggle has not been undone correctly"
    )

    command_stack.redo()
    assert_equal(
        actual=app_state.project.grid.visible,
        expected=True,
        message="Grid visibility toggle has not been redone correctly"
    )
