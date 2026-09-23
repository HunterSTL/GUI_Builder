from collections.abc import Callable

from utility import format_field

from .BaseCommand import Command


class CommandStack:
    """Manages command history by maintaining an undo and redo stack."""
    def __init__(
        self,
        update_window_title_callback: Callable[[], None]
    ) -> None:
        self._update_window_title_callback: Callable[[], None] = update_window_title_callback

        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []
        self._clean_history_position: int | None = 0

    @property
    def is_dirty(
        self
    ) -> bool:
        """Return whether the project contains unsaved changes."""
        return self._clean_history_position != len(self._undo_stack)

    def execute(
        self,
        command: Command
    ) -> None:
        """Execute the given command, push it onto the undo stack and clear the redo stack."""
        command.execute()

        if self._clean_history_position is not None and self._clean_history_position > len(self._undo_stack):
            self._clean_history_position = None     #history branching makes the saved position unreachable

        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._update_window_title_callback()

    def undo(
        self
    ) -> None:
        """Undo the last executed command, pop it from the undo stack and push it onto the redo stack."""
        if not self._undo_stack:
            return

        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        self._update_window_title_callback()

    def redo(
        self
    ) -> None:
        """Redo the last undone command, pop it from the redo stack and push it onto the undo stack."""
        if not self._redo_stack:
            return

        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        self._update_window_title_callback()

    def mark_clean(
        self
    ) -> None:
        """Mark the current command history as clean and update the window title."""
        self._clean_history_position = len(self._undo_stack)
        self._update_window_title_callback()

    def __repr__(
        self
    ) -> str:
        """Return a debug representation of the command stacks."""
        undo_contents = "\n\n".join(
            str(command)
            for command in reversed(self._undo_stack)   #reversed order so newest command is at the top
        ) or "empty"

        redo_contents = "\n\n".join(
            str(command)
            for command in reversed(self._redo_stack)
        ) or "empty"

        lines = [
            format_field(
                label="Clean history position",
                value=self._clean_history_position
            ),
            format_field(
                label="Current history position",
                value=len(self._undo_stack)
            )
        ]
        s = "\n".join(lines)

        undo_section = "-" * 150 + "\n" + undo_contents + "\n" + "-" * 150
        redo_section = "-" * 150 + "\n" + redo_contents + "\n" + "-" * 150
        s += "\n" + "-" * 150 + "\n" + f"Undo stack:\n{undo_section}\nRedo stack:\n{redo_section}"
        return s
