from commands import CommandStack, AddWidget
from model import ProjectDocument, LabelWidget

from AppState import AppState

def create_project() -> tuple[ProjectDocument, AppState, CommandStack]:
    project_document = ProjectDocument()
    app_state = AppState(project_document=project_document)
    command_stack = CommandStack(update_window_title_callback=lambda: None)
    return project_document, app_state, command_stack

def create_project_with_widget() -> tuple[ProjectDocument, AppState, CommandStack]:
    project_document = ProjectDocument()
    app_state = AppState(project_document=project_document)
    command_stack = CommandStack(update_window_title_callback=lambda: None)

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
    return project_document, app_state, command_stack
