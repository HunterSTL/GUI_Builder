from abc import ABC, abstractmethod

#The ABC (abstract base class) "Command" defines which methods each derived command class needs
class Command(ABC):
    """
    A Command represents an undoable operation.
    Commands store operation parameters (IDs, movement deltas...) and snapshot relevant model state (original/final positions, clipboard) either during construction or finalization.
    The execute() method applies the stored operation or snapshotted final state, while the undo() method restores the snapshotted original state.
    """
    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @abstractmethod
    def undo(self):
        raise NotImplementedError