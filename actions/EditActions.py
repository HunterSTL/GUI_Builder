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
        confirm_delete_callback
    ):
        self.app_state = app_state
        self.command_stack = command_stack
        self.clipboard = clipboard  #shared clipboard owned by Designer
        self.confirm_delete_callback = confirm_delete_callback

    def delete(self):
        """delete selected widgets after user confirmation"""
        #query selection
        selected_models = self.app_state.get_selected_models()
        if not selected_models:
            return

        #prompt user to confirm the deletion
        if not self.confirm_delete_callback(count=len(selected_models)):
            return

        #delete models from ProjectDocument
        self.command_stack.execute(
            DeleteWidgets(
                models=selected_models,
                app_state=self.app_state
            )
        )

        #clear selection
        self.app_state.selection_clear()

    def copy(self):
        """copy selected widgets to clipboard"""
        #query selection
        selected_models = self.app_state.get_selected_models()
        if not selected_models:
            return

        #clear clipboard
        self.clipboard.clear()

        #serialize the model of selected widgets into model_data and append it to the clipboard
        for model in selected_models:
            model_data = model.to_dict(include_id=False)    #exclude ID because pasting creates new IDs, except on redo
            self.clipboard.append(model_data)

    def paste(self):
        """paste widgets from clipboard"""
        if not self.clipboard:
            return

        self.command_stack.execute(
            PasteWidgetsFromClipboard(
                clipboard=self.clipboard,
                app_state=self.app_state
            )
        )

    def cut(self):
        """copy selected widgets to clipboard then delete them"""
        #query selection
        selected_models = self.app_state.get_selected_models()
        if not selected_models:
            return

        #copy models to clipboard
        self.copy()

        #delete models from ProjectDocument
        self.command_stack.execute(
            DeleteWidgets(
                models=selected_models,
                app_state=self.app_state
            )
        )

        #clear selection
        self.app_state.selection_clear()

    def undo(self):
        """undo last command"""
        self.command_stack.undo()

    def redo(self):
        """redo last undone command"""
        self.command_stack.redo()
