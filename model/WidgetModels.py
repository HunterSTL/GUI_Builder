from dataclasses import dataclass
from typing import Optional
from model import IdCounters

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

    def create_id(self, id_counters: IdCounters):
        self.id = id_counters.next_label_id()

@dataclass
class EntryWidgetData(BaseWidgetData):
    type: str = "Entry"

    def create_id(self, id_counters: IdCounters):
        self.id = id_counters.next_entry_id()

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = ""
    type: str = "Button"

    def create_id(self, id_counters: IdCounters):
        self.id = id_counters.next_button_id()