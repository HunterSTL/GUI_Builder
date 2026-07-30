from dataclasses import dataclass
from utility import WidgetType

@dataclass
class BaseWidgetData:
    id: str
    x: int
    y: int
    bg: str
    fg: str
    width: int
    height: int
    anchor: str = "sw"

    @property
    def type(self) -> WidgetType:
        raise NotImplementedError

    def __post_init__(self):
        if type(self) is BaseWidgetData:
            raise ValueError("WidgetModels - model creation failed: base type (BaseWidgetData) cannot be instantiated directly")

    def to_dict(self) -> dict:
        """return a copied dictionary of the model's attributes"""
        #copy model attributes
        model_data = self.__dict__.copy()       #shallow copy is safe because models are flat

        #convert WidgetType to string
        model_data["type"] = self.type.value

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
        model_data.pop("type")

        try:
            return _WIDGET_CLASSES[widget_type](**model_data)
        except TypeError as e:
            raise ValueError(f"WidgetModels - model deserialization failed: invalid attribute set for type \"{widget_type.value}\" [{e}]")

@dataclass
class LabelWidgetData(BaseWidgetData):
    text: str = ""

    @property
    def type(self) -> WidgetType:
        return WidgetType.LABEL

@dataclass
class EntryWidgetData(BaseWidgetData):
    @property
    def type(self) -> WidgetType:
        return WidgetType.ENTRY

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = ""

    @property
    def type(self) -> WidgetType:
        return WidgetType.BUTTON

_WIDGET_CLASSES = { #maps WidgetType to the corresponding model class for deserialization
    WidgetType.LABEL: LabelWidgetData,
    WidgetType.ENTRY: EntryWidgetData,
    WidgetType.BUTTON: ButtonWidgetData
}
