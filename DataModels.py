from dataclasses import dataclass, field
from typing import List, Optional

class IdCounters:
    label = 1
    entry = 1
    button = 1

@dataclass
class BaseWidgetData:
    id: Optional[str] = None
    x: int = None
    y: int = None
    bg: str = None
    fg: str = None
    width: int = None
    height: int = None
    anchor: str = "sw"

@dataclass
class LabelWidgetData(BaseWidgetData):
    text: str = ""
    type: str = "Label"

    def create_id(self):
        self.id = f"label{IdCounters.label}"
        IdCounters.label += 1

@dataclass
class EntryWidgetData(BaseWidgetData):
    type: str = "Entry"

    def create_id(self):
        self.id = f"entry{IdCounters.entry}"
        IdCounters.entry += 1

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = ""
    type: str = "Button"

    def create_id(self):
        self.id = f"button{IdCounters.button}"
        IdCounters.button += 1