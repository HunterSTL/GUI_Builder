from commands import Command

class CommandStack:
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def execute(self, command: Command):
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """undo the last command and push it to the redo stack, returning False if the undo stack was empty"""
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """redo the last command and push it to the undo stack, returning False if the redo stack was empty"""
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return True

    def __repr__(self):
        """called automatically when printing this object"""
        undo = "\n".join(str(command) for command in reversed(self._undo_stack)) or "empty" #reversed order so newest command is at the top
        redo = "\n".join(str(command) for command in reversed(self._redo_stack)) or "empty"
        undo = "-" * 150 + "\n" + undo + "\n" + "-" * 150
        redo = "-" * 150 + "\n" + redo + "\n" + "-" * 150
        s = "-" * 150 + "\n" + f"Undo stack:\n{undo}\nRedo stack:\n{redo}"
        return s