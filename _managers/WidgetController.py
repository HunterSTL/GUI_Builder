from AppState import AppState
from _managers import WidgetView

class WidgetController:
    """
    Controller that manages widget rendering and propagates
    widget mutation (deletion, attribute changes through attributes panel) to the model.
    """
    def __init__(
        self,
        app_state: AppState,
        widget_view: WidgetView
    ):
        """store AppState (model) and WidgetView references"""
        self.app_state = app_state
        self.widget_view = widget_view

    #Widget rendering---------------------------------------------------------------------------------------------------
    def render_soft(self, model_id: str):
        """re-render an existing model"""
        model = self.app_state.get_model_from_model_id(model_id)
        self.widget_view.render_soft(model)

    def render_full(self):
        """rebuild all widgets from models"""
        models = self.app_state.project.widget_models
        self.widget_view.render_full(models)

    #Widget mutation----------------------------------------------------------------------------------------------------
    def delete_widget(self, model_id: str):
        """delete widget model from ProjectDocument, tk widget from canvas and remove widget from mappings"""
        model = self.app_state.get_model_from_model_id(model_id)

        #remove widget model from the ProjectDocument
        self.app_state.remove_widget(model)

        #delete tk widget from canvas and remove from mappings
        self.widget_view.delete_widget(model_id)

    def update_widget_attribute(self, model_id: str, attribute: str, value):
        """apply an attribute change from the AttributesPanel to the widget and model"""
        widget = self.widget_view.get_widget_from_model_id(model_id)
        if not widget:
            return

        #validate attribute name
        attribute = attribute.strip().lower()
        allowed_attributes = {"x", "y", "width", "height", "text", "bg", "fg", "anchor"}
        if attribute not in allowed_attributes:
            return

        model = self.app_state.get_model_from_model_id(model_id)

        #changing text should resize the widget
        if attribute == "text":
            #apply new text to the actual widget so tk recomputes geometry
            widget.config(text=value)
            widget.update_idletasks()

            #fetch new dimensions
            new_width, new_height = widget.winfo_reqwidth(), widget.winfo_reqheight()

            #update the model using batching (so only one notify happens)
            with self.app_state.batch():
                self.app_state.set_widget_attribute(model, "text", value)
                self.app_state.set_widget_attribute(model, "width", new_width)
                self.app_state.set_widget_attribute(model, "height", new_height)
        else:
            self.app_state.set_widget_attribute(model, attribute, value)