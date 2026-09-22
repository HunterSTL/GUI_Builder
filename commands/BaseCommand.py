from abc import ABC, abstractmethod


class Command(ABC):
    """Represents an undoable operation."""
    @abstractmethod
    def execute(
        self
    ) -> None:
        """Apply the command."""
        raise NotImplementedError

    @abstractmethod
    def undo(
        self
    ) -> None:
        """Reverse the command."""
        raise NotImplementedError
