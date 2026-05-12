from dataclasses import dataclass, field
from typing import List, Dict, Any
from model import GridConfig, IdCounters

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
        return {
            "version": self.version,
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "icon_path": self.icon_path,
            "grid": self.grid.to_dict(),
            "theme": self.theme,
            "widget_models": [
                model.to_dict(include_id=True)  #used to replace WidgetType enum with string for serialization
                for model in self.widget_models
            ],
            "id_counters": self.id_counters.to_dict()
        }

    @classmethod
    def from_json(cls, project_data: dict) -> "ProjectDocument":
        from model import BaseWidgetData

        return ProjectDocument(
            version=project_data.get("version", 1), #default to 1 if missing from data
            title=project_data.get("title", "Untitled Project"),
            width=int(project_data.get("width", 800)),
            height=int(project_data.get("height", 600)),
            icon_path=project_data.get("icon_path"),
            grid=GridConfig.from_dict(project_data.get("grid")),
            theme=project_data.get("theme", {}),
            widget_models=[
                BaseWidgetData.from_dict(model_data)
                for model_data in project_data.get("widget_models", [])
            ],
            id_counters=IdCounters.from_dict(project_data.get("id_counters"))
        )
