from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from DataModels import LabelWidgetData, EntryWidgetData, ButtonWidgetData, IdCounters

@dataclass
class GridConfig:
    size: int = 10
    color: str = "#888888"
    visible: bool = False

@dataclass
class ProjectDocument:
    version: int = 1
    title: str = "Untitled Project"
    width: int = 800
    height: int = 600
    grid: GridConfig = field(default_factory=GridConfig)
    theme: Dict[str, Dict[str, str]] = field(default_factory=dict)
    widget_models: List[Any] = field(default_factory=list)

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "ProjectDocument":
        grid_data = data.get("grid", {})
        grid = GridConfig(
            size=int(grid_data.get("size", 10)),
            color=grid_data.get("color", "#888888"),
            visible=bool(grid_data.get("visible", False))
        )

        project_doc = ProjectDocument(
            version=data.get("version", 1),     #default to 1 if missing from data
            title=data.get("title", "Untitled Project"),
            width=int(data["width"]),
            height=int(data["height"]),
            grid=grid,
            theme=data.get("theme", {})
        )

        max_label_id = 0
        max_entry_id = 0
        max_button_id = 0

        for widget_model in data.get("widget_models", []):
            widget_id = widget_model["id"]
            if widget_model["type"] == "Label":
                project_doc.widget_models.append(LabelWidgetData(**widget_model))
                max_label_id = max(max_label_id, int(widget_id[5:]))
            elif widget_model["type"] == "Entry":
                project_doc.widget_models.append(EntryWidgetData(**widget_model))
                max_entry_id = max(max_entry_id, int(widget_id[5:]))
            elif widget_model["type"] == "Button":
                project_doc.widget_models.append(ButtonWidgetData(**widget_model))
                max_button_id = max(max_button_id, int(widget_id[6:]))

        IdCounters.entry = max(IdCounters.entry, max_entry_id + 1)
        IdCounters.label = max(IdCounters.label, max_label_id + 1)
        IdCounters.button = max(IdCounters.button, max_button_id + 1)

        return project_doc