from model import BaseWidgetData
from view import WidgetView
from AppState import AppState

class WidgetController:
    """
    Controller that manages widget rendering and propagates
    widget mutation (deletion, attribute changes through attributes panel) to the model.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        app_state: AppState,
        widget_view: WidgetView
    ):
        """store AppState (model) and WidgetView references"""
        self.app_state = app_state
        self.widget_view = widget_view

    #Rendering API------------------------------------------------------------------------------------------------------
    def render_soft(self, model_id: str):
        """re-render an existing model"""
        model = self.app_state.get_model_from_model_id(model_id)
        self.widget_view.render_soft(model)

    def render_full(self):
        """rebuild all widgets from models"""
        models = self.app_state.project.widget_models
        self.widget_view.render_full(models)

    #Domain logic-------------------------------------------------------------------------------------------------------
    def update_widget_attribute(self, model_id: str, attribute: str, value):
        """apply an attribute change to the model, handling special cases that require widget measurement"""
        model = self.app_state.get_model_from_model_id(model_id)
        attribute = attribute.strip().lower()

        if attribute == "text":
            self._update_widget_text_with_measurement(model, value) #text updates require measurement to update model dimensions
        else:
            self.app_state.set_model_attribute(model, attribute, value)

    #Internals----------------------------------------------------------------------------------------------------------
    def _update_widget_text_with_measurement(self, model: BaseWidgetData, text: str):
        """update the text of the model and recompute model dimensions based on widget measurement"""
        widget = self.widget_view.get_widget_from_model_id(model.id)
        if not widget:
            raise ValueError(f"WidgetController - text update failed: missing widget for model \"{model.id}\"")

        #apply new text to the widget
        widget.config(text=text)

        #let Tk recompute the geometry
        widget.update_idletasks()

        #measure new dimensions
        new_width, new_height = widget.winfo_reqwidth(), widget.winfo_reqheight()

        #update the model using batching (so only one notify happens)
        with self.app_state.batch():
            self.app_state.set_model_attribute(model, "text", text)
            self.app_state.set_model_attribute(model, "width", new_width)
            self.app_state.set_model_attribute(model, "height", new_height)
