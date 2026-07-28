from dataclasses import dataclass
from utility import WidgetType

@dataclass
class BaseWidgetData:
    type: WidgetType
    id: str | None = None
    x: int | None = None
    y: int | None = None
    bg: str | None = None
    fg: str | None = None
    width: int | None = None
    height: int | None = None
    anchor: str = "sw"

    def __post_init__(self):
        if type(self) is BaseWidgetData:
            raise ValueError("WidgetModels - model creation failed: base type (BaseWidgetData) cannot be instantiated directly")

    def to_dict(self, include_id: bool) -> dict:
        """return a copied dictionary of the model's attributes, optionally without the ID (suitable for clipboard use)"""
        #copy model attributes
        model_data = self.__dict__.copy()       #shallow copy is safe because models are flat

        #convert WidgetType to string
        model_data["type"] = self.type.value

        if not include_id:
            #strip the ID attribute
            model_data.pop("id", None)

        return model_data

    @classmethod
    def from_dict(cls, model_data: dict) -> "BaseWidgetData":
        #ensure type attribute is present
        if "type" not in model_data:
            raise ValueError("WidgetModels - model deserialization failed: missing required attribute \"type\"")

        raw_type = model_data["type"]

        #validate that the serialized type maps to a WidgetType
        try:
            widget_type = WidgetType(raw_type)
        except ValueError:
            raise ValueError(f"WidgetModels - model deserialization failed: invalid type \"{raw_type}\"")               #raw type doesn't map to any WidgetType → invalid

        #validate that a model class exists for this widget type
        if widget_type not in _WIDGET_CLASSES:
            raise ValueError(f"WidgetModels - model deserialization failed: unsupported type \"{widget_type.value}\"")  #WidgetType doesn't map to any WidgetData class → unsupported

        #replace string type with WidgetType
        model_data = model_data.copy() #copy to prevent mutating input data
        model_data["type"] = widget_type

        try:
            return _WIDGET_CLASSES[widget_type](**model_data)
        except TypeError as e:
            raise ValueError(f"WidgetModels - model deserialization failed: invalid attribute set for type \"{widget_type.value}\" [{e}]")

@dataclass
class LabelWidgetData(BaseWidgetData):
    text: str = ""
    type: WidgetType = WidgetType.LABEL

@dataclass
class EntryWidgetData(BaseWidgetData):
    type: WidgetType = WidgetType.ENTRY

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = ""
    type: WidgetType = WidgetType.BUTTON

_WIDGET_CLASSES = { #maps WidgetType to the corresponding model class for deserialization
    WidgetType.LABEL: LabelWidgetData,
    WidgetType.ENTRY: EntryWidgetData,
    WidgetType.BUTTON: ButtonWidgetData
}
