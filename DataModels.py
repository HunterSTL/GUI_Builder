from dataclasses import dataclass, field
from typing import List, Optional
from Theme import (BACKGROUND_COLOR, TEXT_COLOR)

class IdCounters:
    label = 1
    entry = 1
    button = 1

@dataclass
class BaseWidgetData:
    id: Optional[str] = None
    x: int = 0
    y: int = 0
    bg: str = BACKGROUND_COLOR
    fg: str = TEXT_COLOR
    anchor: str = "sw"

@dataclass
class LabelWidgetData(BaseWidgetData):
    text: str = "Label"

    def create_id(self):
        self.id = f"label{IdCounters.label}"
        IdCounters.label += 1

@dataclass
class EntryWidgetData(BaseWidgetData):
    def create_id(self):
        self.id = f"entry{IdCounters.entry}"
        IdCounters.entry += 1

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = "Button"

    def create_id(self):
        self.id = f"button{IdCounters.button}"
        IdCounters.button += 1

@dataclass
class GUIWindow:
    title: str
    width: int
    height: int
    bg_color: str
    widgets: List[BaseWidgetData] = field(default_factory=list)
    selected_widgets: List[BaseWidgetData] = field(default_factory=list)

    def add_widget(self, widget: BaseWidgetData):
        self.widgets.append(widget)