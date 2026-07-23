from commands import CommandStack, DeleteWidgets, PasteWidgetsFromClipboard
from AppState import AppState

class EditActions:
    """
    Encapsulates the editor's edit semantics: delete, copy, cut, paste, undo and redo.

    This class uses AppState for model access and mutation, a CommandStack
    for undo and redo support, a shared clipboard for copy and paste operations
    and an injected callback to handle delete confirmation.
    """
    def __init__(
        self,
        app_state: AppState,
        command_stack: CommandStack,
        clipboard: list,
        confirm_delete_callback,
        commit_active_attributes_panel_edit_callback
    ):
        self.app_state = app_state
        self.command_stack = command_stack
        self.clipboard = clipboard  #shared clipboard owned by Designer
        self.confirm_delete_callback = confirm_delete_callback
        self.commit_active_attributes_panel_edit_callback = commit_active_attributes_panel_edit_callback

        self._copy_origin_coordinates: tuple[int, int] | None = None

    def delete(self):
        """commit the active attributes panel edit, if one is in progress, then delete selected widgets after user confirmation"""
        selected_models = self.app_state.get_selected_models()
        if not selected_models:
            return

        if not self.confirm_delete_callback(count=len(selected_models)):
            return

        self.commit_active_attributes_panel_edit_callback()

        self.command_stack.execute(
            DeleteWidgets(
                models=selected_models,
                app_state=self.app_state
            )
        )

    def copy(self) -> None:
        """copy selected widgets to clipboard"""
        selected_models = self.app_state.get_selected_models()
        if not selected_models:
            return

        self.clipboard.clear()

        for model in selected_models:
            model_data = model.to_dict(include_id=False)    #exclude ID because pasting creates new IDs, except on redo
            self.clipboard.append(model_data)

        #store coordinates of the last selected model to compute the movement delta applied during paste
        last_selected_model = selected_models[-1]
        self._copy_origin_coordinates = last_selected_model.x, last_selected_model.y

    def paste(self, pointer_coordinates: tuple[int, int] | None) -> None:
        """paste widgets from clipboard, offsetting them so the last selected widget is positioned at the pointer (with clamping)"""
        if not self.clipboard:
            return

        if pointer_coordinates is None or self._copy_origin_coordinates is None:
            return

        dx = pointer_coordinates[0] - self._copy_origin_coordinates[0]
        dy = pointer_coordinates[1] - self._copy_origin_coordinates[1]

        self.command_stack.execute(
            PasteWidgetsFromClipboard(
                clipboard=self.clipboard,
                dx=dx,
                dy=dy,
                app_state=self.app_state
            )
        )

    def cut(self):
        """commit the active attributes panel edit, if one is in progress, then copy selected widgets to the clipboard and delete them"""
        selected_models = self.app_state.get_selected_models()
        if not selected_models:
            return

        self.commit_active_attributes_panel_edit_callback()
        self.copy()
        self.command_stack.execute(
            DeleteWidgets(
                models=selected_models,
                app_state=self.app_state
            )
        )

    def undo(self):
        """commit the active attributes panel edit, if one is in progress, then undo last command"""
        self.commit_active_attributes_panel_edit_callback()
        self.command_stack.undo()

    def redo(self):
        """commit the active attributes panel edit, if one is in progress, then redo last undone command"""
        self.commit_active_attributes_panel_edit_callback()
        self.command_stack.redo()
