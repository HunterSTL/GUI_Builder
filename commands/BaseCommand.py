from abc import ABC, abstractmethod


class Command(ABC):
    """Represents an undoable operation."""
    @abstractmethod
    def execute(
        self
    ) -> None:
        """Apply the stored operation or snapshotted final state."""
        raise NotImplementedError

    @abstractmethod
    def undo(
        self
    ) -> None:
        """Restore the snapshotted original state."""
        raise NotImplementedError
