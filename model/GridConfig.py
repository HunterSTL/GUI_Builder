from dataclasses import dataclass

@dataclass
class GridConfig:
    size: int = 10
    color: str = "#888888"
    visible: bool = False

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "color": self.color,
            "visible": self.visible
        }

    @classmethod
    def from_dict(cls, grid_data) -> "GridConfig":
        grid_data = grid_data or {} #fallback to default values if empty
        return GridConfig(
            size=grid_data.get("size", 10),
            color=grid_data.get("color", "#888888"),
            visible=grid_data.get("visible", False)
        )
