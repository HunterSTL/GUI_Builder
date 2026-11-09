from tests.validation.helpers import create_edit_widget_command, create_drag_widgets_command

def test_execute_edit_widget_command_without_recording_final_attribute_values() -> None:
    command = create_edit_widget_command()
    command.execute()

def test_check_drag_widgets_command_effect_without_recording_final_positions() -> None:
    command = create_drag_widgets_command()
    command.has_effect()

def test_execute_drag_widgets_command_without_recording_final_positions() -> None:
    command = create_drag_widgets_command()
    command.execute()
