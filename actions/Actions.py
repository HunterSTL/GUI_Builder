from .EditActions import EditActions
from .GridActions import GridActions
from .PropertiesActions import PropertiesActions
from .WidgetActions import WidgetActions


class Actions:
    """Provides a single access point for editor action groups."""
    def __init__(
        self,
        edit_actions: EditActions,
        grid_actions: GridActions,
        properties_actions: PropertiesActions,
        widget_actions: WidgetActions
    ) -> None:
        self.edit: EditActions = edit_actions
        self.grid: GridActions = grid_actions
        self.properties: PropertiesActions = properties_actions
        self.widget: WidgetActions = widget_actions
