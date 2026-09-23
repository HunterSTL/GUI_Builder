from commands import CommandStack, SetProjectTitle

from AppState import AppState


class PropertiesActions:
    """Encapsulates changes to project properties."""
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack
    ) -> None:
        self._app_state: AppState = app_state
        self._command_stack: CommandStack = command_stack

    def change_title(
        self,
        new_title: str
    ) -> None:
        """Change the project title if the requested title differs from the current title."""
        cmd = SetProjectTitle(
            app_state=self._app_state,
            new_title=new_title
        )

        if not cmd.has_effect():
            return

        self._command_stack.execute(cmd)
