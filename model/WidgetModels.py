from dataclasses import dataclass
from typing import Optional
import copy
from model import IdCounters

@dataclass
class BaseWidgetData:
    id: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    bg: Optional[str] = None
    fg: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
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
        if "type" not in model_data:
            raise ValueError("Missing required attribute \"type\" in model data")

        widget_type = model_data["type"]

        if not widget_type in _WIDGET_CLASSES:
            raise ValueError(f"Unknown widget type \"{widget_type}\"")

        return _WIDGET_CLASSES[widget_type](**model_data)

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

_WIDGET_CLASSES = {
    "Label": LabelWidgetData,
    "Entry": EntryWidgetData,
    "Button": ButtonWidgetData
}
