from collections.abc import Callable

from commands import CommandStack, DeleteWidgets, PasteWidgetsFromClipboard

from AppState import AppState


class EditActions:
    """Encapsulates standard edit actions."""
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack,
        clipboard: list[dict[str, str | int | None]],
        confirm_delete_callback: Callable[[int], bool],
        commit_active_attributes_panel_edit_callback: Callable[[], None]
    ) -> None:
        self._app_state: AppState = app_state
        self._command_stack: CommandStack = command_stack
        self._clipboard: list[dict[str, str | int | None]] = clipboard   #shared clipboard owned by Designer
        self._confirm_delete_callback: Callable[[int], bool] = confirm_delete_callback
        self._commit_active_attributes_panel_edit_callback: Callable[[], None] = commit_active_attributes_panel_edit_callback

        self._copy_origin_coordinates: tuple[int, int] | None = None

    def delete(
        self
    ) -> None:
        """Delete selected widgets after user confirmation."""
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        if not self._confirm_delete_callback(len(selected_models)):
            return

        self._commit_active_attributes_panel_edit_callback()

        self._command_stack.execute(
            DeleteWidgets(
                models=selected_models,
                app_state=self._app_state
            )
        )

    def copy(
        self
    ) -> None:
        """Copy selected widgets to clipboard."""
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        self._clipboard.clear()

        for model in selected_models:
            model_data = model.to_dict()
            self._clipboard.append(model_data)

        last_selected_model = selected_models[-1]
        self._copy_origin_coordinates = last_selected_model.x, last_selected_model.y    #used to compute the movement delta applied during paste

    def paste(
        self,
        pointer_coordinates: tuple[int, int] | None
    ) -> None:
        """Paste widgets from clipboard, offsetting them so the last selected widget is positioned at the pointer."""
        if not self._clipboard:
            return

        if pointer_coordinates is None or self._copy_origin_coordinates is None:
            return

        dx = pointer_coordinates[0] - self._copy_origin_coordinates[0]
        dy = pointer_coordinates[1] - self._copy_origin_coordinates[1]

        self._command_stack.execute(
            PasteWidgetsFromClipboard(
                clipboard=self._clipboard,
                dx=dx,
                dy=dy,
                app_state=self._app_state
            )
        )

    def cut(
        self
    ) -> None:
        """Copy selected widgets to clipboard and delete them."""
        selected_models = self._app_state.get_selected_models()
        if not selected_models:
            return

        self._commit_active_attributes_panel_edit_callback()
        self.copy()
        self._command_stack.execute(
            DeleteWidgets(
                models=selected_models,
                app_state=self._app_state
            )
        )

    def undo(
        self
    ) -> None:
        """Undo the most recently executed command."""
        self._commit_active_attributes_panel_edit_callback()
        self._command_stack.undo()

    def redo(
        self
    ) -> None:
        """Redo the most recently undone command."""
        self._commit_active_attributes_panel_edit_callback()
        self._command_stack.redo()
