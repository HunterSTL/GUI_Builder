from actions import EditActions, WidgetActions

class Actions:
    """
    Provides a single access point for all editor action groups.

    An action group is a class that provides methods that implement a set
    of related editor actions (e.g. EditActions provides delete, copy, undo etc.)
    """
    def __init__(
        self,
        edit_actions: EditActions,
        widget_actions: WidgetActions
    ):
        self.edit = edit_actions
        self.widget = widget_actions
