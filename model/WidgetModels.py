from dataclasses import dataclass
from typing import Optional
import copy
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

    def to_dict(self, include_id: bool) -> dict:
        """return a deep-copied dictionary of the model's attributes, optionally without the ID (suitable for clipboard use)"""
        #deepcopy the dictionary of attributes from this model
        model_data = copy.deepcopy(self.__dict__)

        if not include_id:
            #strip the ID attribute
            model_data.pop("id", None)

        return model_data

    @classmethod
    def from_dict(cls, model_data: dict) -> "BaseWidgetData":
        widget_type = model_data["type"]
        if widget_type == "Label":
            return LabelWidgetData(**model_data)
        elif widget_type == "Entry":
            return EntryWidgetData(**model_data)
        elif widget_type == "Button":
            return ButtonWidgetData(**model_data)

@dataclass
class LabelWidgetData(BaseWidgetData):
    text: str = ""
    type: str = "Label"

    def create_id(self, id_counters: IdCounters) -> str:
        self.id = id_counters.next_label_id()
        return self.id

@dataclass
class EntryWidgetData(BaseWidgetData):
    type: str = "Entry"

    def create_id(self, id_counters: IdCounters) -> str:
        self.id = id_counters.next_entry_id()
        return self.id

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = ""
    type: str = "Button"

    def create_id(self, id_counters: IdCounters) -> str:
        self.id = id_counters.next_button_id()
        return self.id