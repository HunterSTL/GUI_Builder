from dataclasses import dataclass

from utility import CONSTANTS, is_valid_integer, is_valid_hex_color_code


@dataclass
class GridConfig:
    """Stores grid settings."""
    size: int = 10
    color: str = "#888888"
    visible: bool = False

    def to_dict(
        self
    ) -> dict[str, int | str | bool]:
        """Serialize the grid config to grid data."""
        return {
            "size": self.size,
            "color": self.color,
            "visible": self.visible
        }

    @classmethod
    def from_dict(
        cls,
        grid_data: dict
    ) -> "GridConfig":
        """Validate and deserialize grid data into a grid config."""
        cls._validate_grid_data(grid_data)
        return cls(
            size=grid_data["size"],
            color=grid_data["color"],
            visible=grid_data["visible"]
        )

    @classmethod
    def _validate_grid_data(
        cls,
        grid_data: dict
    ) -> None:
        """Validate the schema and attribute values of the grid data."""
        #validate schema
        if not isinstance(grid_data, dict):
            raise ValueError("GridConfig - grid data deserialization failed: grid data is not a dictionary")

        for attribute in _REQUIRED_ATTRIBUTES:
            if attribute not in grid_data:
                raise ValueError(f"GridConfig - grid data deserialization failed: missing required attribute \"{attribute}\"")

        for attribute in grid_data:
            if attribute not in _EXPECTED_ATTRIBUTES:
                raise ValueError(f"GridConfig - grid data deserialization failed: invalid attribute set [got unexpected attribute \"{attribute}\"]")

        #validate attribute values
        size = grid_data["size"]
        color = grid_data["color"]
        visible = grid_data["visible"]
        min_size = CONSTANTS["grid"]["min_size"]
        max_size = CONSTANTS["grid"]["max_size"]

        if not is_valid_integer(size):
            raise ValueError(f"GridConfig - grid data deserialization failed: invalid size \"{size}\"")

        if not min_size <= size <= max_size:
            raise ValueError(f"GridConfig - grid data deserialization failed: size outside allowed range [expected {min_size} - {max_size}, got {size}]")

        if not is_valid_hex_color_code(color):
            raise ValueError(f"GridConfig - grid data deserialization failed: invalid color \"{color}\"")

        if not isinstance(visible, bool):
            raise ValueError(f"GridConfig - grid data deserialization failed: invalid visibility \"{visible}\"")


_REQUIRED_ATTRIBUTES = {"size", "color", "visible"}
_EXPECTED_ATTRIBUTES = _REQUIRED_ATTRIBUTES
