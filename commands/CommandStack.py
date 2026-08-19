from .BaseCommand import Command


class CommandStack:
    """Manages command history by maintaining an undo and redo stack."""
    def __init__(
        self
    ) -> None:
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(
        self,
        command: Command
    ) -> None:
        """Execute the given command, push it onto the undo stack and clear the redo stack."""
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(
        self
    ) -> None:
        """Undo the last executed command, pop it from the undo stack and push it onto the redo stack."""
        if not self._undo_stack:
            return

        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(
        self
    ) -> None:
        """Redo the last undone command, pop it from the redo stack and push it onto the undo stack."""
        if not self._redo_stack:
            return

        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)

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

        undo_section = "-" * 150 + "\n" + undo_contents + "\n" + "-" * 150
        redo_section = "-" * 150 + "\n" + redo_contents + "\n" + "-" * 150
        s = "-" * 150 + "\n" + f"Undo stack:\n{undo_section}\nRedo stack:\n{redo_section}"
        return s
