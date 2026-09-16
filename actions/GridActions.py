from commands import CommandStack, ToggleGrid, SetGridColor, SetGridSize

from AppState import AppState


class GridActions:
    """Encapsulates grid configuration changes."""
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack
    ) -> None:
        self._app_state: AppState = app_state
        self._command_stack: CommandStack = command_stack

    def toggle(
        self
    ) -> None:
        """Toggle grid visibility."""
        self._command_stack.execute(
            ToggleGrid(
                app_state=self._app_state
            )
        )

    def change_color(
        self,
        new_color: str
    ) -> None:
        """Change the grid color if the requested color differs from the current color."""
        cmd = SetGridColor(
            app_state=self._app_state,
            new_color=new_color
        )

        if not cmd.has_effect():
            return

        self._command_stack.execute(cmd)

    def change_size(
        self,
        new_size: int
    ) -> None:
        """Change the grid size if the requested size differs from the current size."""
        cmd = SetGridSize(
            app_state=self._app_state,
            new_size=new_size
        )

        if not cmd.has_effect():
            return

        self._command_stack.execute(cmd)
