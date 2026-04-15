from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from model import IdCounters

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
    icon_path: str | None = None
    grid: GridConfig = field(default_factory=GridConfig)
    theme: Dict[str, Dict[str, str]] = field(default_factory=dict)
    widget_models: List[Any] = field(default_factory=list)
    id_counters: IdCounters = field(default_factory=IdCounters)

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "ProjectDocument":
        from model import BaseWidgetData

        grid_data = data.get("grid", {})
        grid = GridConfig(
            size=int(grid_data.get("size", 10)),
            color=grid_data.get("color", "#888888"),
            visible=bool(grid_data.get("visible", False))
        )

        project_document = ProjectDocument(
            version=data.get("version", 1),     #default to 1 if missing from data
            title=data.get("title", "Untitled Project"),
            width=int(data["width"]),
            height=int(data["height"]),
            icon_path=data.get("icon_path"),
            grid=grid,
            theme=data.get("theme", {})
        )

        max_label_id = 0
        max_entry_id = 0
        max_button_id = 0

        for model_data in data.get("widget_models", []):
            #create model from the model_data and add to the ProjectDocument
            project_document.widget_models.append(BaseWidgetData.from_dict(model_data))

            #record highest widget ID to update the IdCounters
            widget_id = model_data["id"]
            widget_type = model_data["type"]

            if widget_type == "Label":
                max_label_id = max(max_label_id, int(widget_id[5:]))
            elif widget_type == "Entry":
                max_entry_id = max(max_entry_id, int(widget_id[5:]))
            elif widget_type == "Button":
                max_button_id = max(max_button_id, int(widget_id[6:]))

        project_document.id_counters.set_next_label_id(max_label_id + 1)    #prevents ID collisions
        project_document.id_counters.set_next_entry_id(max_entry_id + 1)
        project_document.id_counters.set_next_button_id(max_button_id + 1)

        return project_document