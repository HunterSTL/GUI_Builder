from enum import Enum, auto

class Edge(Enum):
    """
    Represents a geometric edge used as a reference for widget alignment.
    """
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()