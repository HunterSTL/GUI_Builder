from enum import Enum


class Edge(Enum):
    """Represents a geometric edge used as a reference for widget alignment."""
    LEFT = "left"   #string values for command repr
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
