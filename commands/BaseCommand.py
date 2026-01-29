from abc import ABC, abstractmethod

#The ABC (abstract base class) "Command" defines which methods each derived command class needs
class Command(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @abstractmethod
    def undo(self):
        raise NotImplementedError