from dataclasses import dataclass, field

from .GridConfig import GridConfig
from .IdCounters import IdCounters
from .Widgets import BaseWidget

from utility import allowed_x_range, allowed_y_range, is_positive_integer, is_non_empty_string
from utility.Constants import CANVAS_MIN_WIDTH, CANVAS_MIN_HEIGHT, CANVAS_MAX_WIDTH, CANVAS_MAX_HEIGHT


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
    widgets: list[BaseWidget] = field(default_factory=list)
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
                widget.to_dict()
                for widget in self.widgets
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

        widgets = cls._deserialize_widget_data_list(
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
            widgets=widgets,
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

        if not CANVAS_MIN_WIDTH <= canvas_width <= CANVAS_MAX_WIDTH:
            raise ValueError(f"ProjectDocument - project data deserialization failed: width outside allowed range [expected {CANVAS_MIN_WIDTH} - {CANVAS_MAX_WIDTH}, got {canvas_width}]")

        if not CANVAS_MIN_HEIGHT <= canvas_height <= CANVAS_MAX_HEIGHT:
            raise ValueError(f"ProjectDocument - project data deserialization failed: height outside allowed range [expected {CANVAS_MIN_HEIGHT} - {CANVAS_MAX_HEIGHT}, got {canvas_height}]")

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
    ) -> list[BaseWidget]:
        """Deserialize the list of widget data and validate ID uniqueness and widget geometry."""
        seen_ids = set()
        widgets = []

        for widget_data in widget_data_list:
            widget = BaseWidget.from_dict(widget_data)

            #validate ID uniqueness
            if widget.id in seen_ids:
                raise ValueError(f"ProjectDocument - project data deserialization failed: duplicate widget ID \"{widget.id}\"")
            seen_ids.add(widget.id)

            #validate widget geometry
            if widget.width > canvas_width:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget width exceeds canvas width [{widget.width} > {canvas_width}, ID: \"{widget.id}\"]")

            if widget.height > canvas_height:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget height exceeds canvas height [{widget.height} > {canvas_height}, ID: \"{widget.id}\"]")

            min_x, max_x = allowed_x_range(
                canvas_width=canvas_width,
                widget_width=widget.width,
                anchor=widget.anchor
            )

            min_y, max_y = allowed_y_range(
                canvas_height=canvas_height,
                widget_height=widget.height,
                anchor=widget.anchor
            )

            if not min_x <= widget.x <= max_x:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget X coordinate outside allowed range [expected {min_x} - {max_x}, got {widget.x}, ID: \"{widget.id}\"]")

            if not min_y <= widget.y <= max_y:
                raise ValueError(f"ProjectDocument - project data deserialization failed: widget Y coordinate outside allowed range [expected {min_y} - {max_y}, got {widget.y}, ID: \"{widget.id}\"]")

            widgets.append(widget)
        return widgets


_REQUIRED_ATTRIBUTES = {"version", "title", "width", "height", "grid", "theme", "widgets", "id_counters"}
_EXPECTED_ATTRIBUTES = _REQUIRED_ATTRIBUTES | {"icon_path"}
