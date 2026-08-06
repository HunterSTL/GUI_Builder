from dataclasses import dataclass, field

from .GridConfig import GridConfig
from .IdCounters import IdCounters
from .WidgetModels import BaseWidgetData

from utility import CONSTANTS, allowed_x_range, allowed_y_range, is_positive_integer, is_non_empty_string


@dataclass
class ProjectDocument:
    """Stores project data."""
    version: int = 1
    title: str = "Untitled Project"
    width: int = 800
    height: int = 600
    icon_path: str | None = None
    grid: GridConfig = field(default_factory=GridConfig)
    theme: dict[str, dict[str, str]] = field(default_factory=dict)
    widget_models: list[BaseWidgetData] = field(default_factory=list)
    id_counters: IdCounters = field(default_factory=IdCounters)

    def to_json(
        self
    ) -> dict[str, object]:
        """Serialize the project document to project data."""
        return {
            "version": self.version,
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "icon_path": self.icon_path,
            "grid": self.grid.to_dict(),
            "theme": self.theme,
            "widgets": [
                model.to_dict()
                for model in self.widget_models
            ],
            "id_counters": self.id_counters.to_dict()
        }

    @classmethod
    def from_json(
        cls,
        project_data: dict
    ) -> "ProjectDocument":
        """Validate and deserialize project data into a project document."""
        cls._validate_project_data(project_data)

        widget_models = cls._deserialize_widget_data_list(
            widget_data_list=project_data["widgets"],
            canvas_width=project_data["width"],
            canvas_height=project_data["height"]
        )
        grid_config = GridConfig.from_dict(project_data["grid"])
        id_counters = IdCounters.from_dict(project_data["id_counters"])

        return cls(
            version=project_data["version"],
            title=project_data["title"],
            width=project_data["width"],
            height=project_data["height"],
            icon_path=project_data.get("icon_path"),
            grid=grid_config,
            theme=project_data["theme"],
            widget_models=widget_models,
            id_counters=id_counters
        )

    @classmethod
    def _validate_project_data(
        cls,
        project_data: dict
    ) -> None:
        """Validate the schema and attribute values of the project data."""
        #validate schema
        if not isinstance(project_data, dict):
            raise ValueError("ProjectDocument - project data deserialization failed: project data is not a dictionary")

        for attribute in _REQUIRED_ATTRIBUTES:
            if attribute not in project_data:
                raise ValueError(f"ProjectDocument - project data deserialization failed: missing required attribute \"{attribute}\"")

        for attribute in project_data:
            if attribute not in _EXPECTED_ATTRIBUTES:
                raise ValueError(f"ProjectDocument - project data deserialization failed: invalid attribute set [got unexpected attribute \"{attribute}\"]")

        #validate attribute values
        version = project_data["version"]
        title = project_data["title"]
        canvas_width = project_data["width"]
        canvas_height = project_data["height"]
        min_width = CONSTANTS["canvas"]["min_width"]
        min_height = CONSTANTS["canvas"]["min_height"]
        max_width = CONSTANTS["canvas"]["max_width"]
        max_height = CONSTANTS["canvas"]["max_height"]
        icon_path = project_data.get("icon_path")
        theme = project_data["theme"]
        widget_data_list = project_data["widgets"]

        if not is_positive_integer(version):
            raise ValueError(f"ProjectDocument - project data deserialization failed: invalid version \"{version}\"")

        if version != 1:
            raise ValueError(f"ProjectDocument - project data deserialization failed: unsupported version \"{version}\"")

        if not is_non_empty_string(title):
            raise ValueError(f"ProjectDocument - project data deserialization failed: invalid title \"{title}\"")

        if not is_positive_integer(canvas_width):
            raise ValueError(f"ProjectDocument - project data deserialization failed: invalid width \"{canvas_width}\"")

        if not is_positive_integer(canvas_height):
            raise ValueError(f"ProjectDocument - project data deserialization failed: invalid height \"{canvas_height}\"")

        if not min_width <= canvas_width <= max_width:
            raise ValueError(f"ProjectDocument - project data deserialization failed: width outside allowed range [expected {min_width} - {max_width}, got {canvas_width}]")

        if not min_height <= canvas_height <= max_height:
            raise ValueError(f"ProjectDocument - project data deserialization failed: height outside allowed range [expected {min_height} - {max_height}, got {canvas_height}]")

        if icon_path is not None and not isinstance(icon_path, str):
            raise ValueError(f"ProjectDocument - project data deserialization failed: invalid icon path \"{icon_path}\"")

        if not isinstance(theme, dict):
            raise ValueError("ProjectDocument - project data deserialization failed: theme is not a dictionary")

        if not isinstance(widget_data_list, list):
            raise ValueError("ProjectDocument - project data deserialization failed: widget data is not a list")

    @classmethod
    def _deserialize_widget_data_list(
        cls,
        widget_data_list: list[dict],
        canvas_width: int,
        canvas_height: int
    ) -> list[BaseWidgetData]:
        """Deserialize the list of widget data and validate ID uniqueness and widget geometry."""
        seen_ids = set()
        widget_models = []

        for widget_data in widget_data_list:
            widget_model = BaseWidgetData.from_dict(widget_data)

            #validate ID uniqueness
            if widget_model.id in seen_ids:
                raise ValueError(f"ProjectDocument - project data deserialization failed: duplicate widget ID \"{widget_model.id}\"")
            seen_ids.add(widget_model.id)

            #validate widget geometry
            if widget_model.width > canvas_width:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget width exceeds canvas width [{widget_model.width} > {canvas_width}, ID: \"{widget_model.id}\"]")

            if widget_model.height > canvas_height:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget height exceeds canvas height [{widget_model.height} > {canvas_height}, ID: \"{widget_model.id}\"]")

            min_x, max_x = allowed_x_range(
                canvas_width=canvas_width,
                widget_width=widget_model.width,
                anchor=widget_model.anchor
            )

            min_y, max_y = allowed_y_range(
                canvas_height=canvas_height,
                widget_height=widget_model.height,
                anchor=widget_model.anchor
            )

            if not min_x <= widget_model.x <= max_x:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget X coordinate outside allowed range [expected {min_x} - {max_x}, got {widget_model.x}, ID: \"{widget_model.id}\"]")

            if not min_y <= widget_model.y <= max_y:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget Y coordinate outside allowed range [expected {min_y} - {max_y}, got {widget_model.y}, ID: \"{widget_model.id}\"]")

            widget_models.append(widget_model)
        return widget_models


_REQUIRED_ATTRIBUTES = {"version", "title", "width", "height", "grid", "theme", "widgets", "id_counters"}
_EXPECTED_ATTRIBUTES = _REQUIRED_ATTRIBUTES | {"icon_path"}
