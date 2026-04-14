from view import AttributesPanelView
from utility import allowed_x_range, allowed_y_range

#attributes that can be shown in the attributes panel including the type of widget
#to display the value with (text field, numeric input, color picker, dropwodn etc.)
ATTRIBUTE_CONFIG = {
    "Label": {
        "type": "label",
        "id": "label",
        "x": "spinbox",
        "y": "spinbox",
        "width": "spinbox",
        "height": "spinbox",
        "text": "entry",
        "bg": "colorpicker",
        "fg": "colorpicker",
        "anchor": "combobox"
    },
    "Entry": {
        "type": "label",
        "id": "label",
        "x": "spinbox",
        "y": "spinbox",
        "width": "spinbox",
        "height": "spinbox",
        "bg": "colorpicker",
        "fg": "colorpicker",
        "anchor": "combobox"
    },
    "Button": {
        "type": "label",
        "id": "label",
        "x": "spinbox",
        "y": "spinbox",
        "width": "spinbox",
        "height": "spinbox",
        "text": "entry",
        "bg": "colorpicker",
        "fg": "colorpicker",
        "anchor": "combobox"
    }
}

class AttributesPanelController:
    """
    Controller that manages what appears in the Attributes Panel, computes
    valid ranges for numeric inputs, and instructs the view to rebuild UI
    elements whenever selection or model geometry changes.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        attribute_panel_view: AttributesPanelView,
        canvas_width: int,
        canvas_height: int
    ):
        """initialize controller state and references"""
        self.attribute_panel_view = attribute_panel_view
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    #Rendering API------------------------------------------------------------------------------------------------------
    def refresh(self, model):
        """rebuild the panel for the given model"""
        #set active model id so view knows which widget is selected (to propagate changes from the panel to the model)
        self.attribute_panel_view.set_active_model_id(model.id)

        #render the panel
        self._populate(model)

    def clear(self):
        """clear all UI widgets from the attributes panel"""
        self.attribute_panel_view.clear_panel()

    #Domain logic-------------------------------------------------------------------------------------------------------
    def _populate(self, model):
        """populate the panel with widgets representing model attributes"""
        #clear previous widgets
        self.attribute_panel_view.clear_panel()

        row_index = 0

        for attribute, widget_type in ATTRIBUTE_CONFIG[model.type].items():
            #create displayname for each attribute
            self.attribute_panel_view.create_display_name_label(attribute, row_index)

            #create the correct widget based on widget_type
            if widget_type == "spinbox":
                min_value, max_value = self._compute_spinbox_limits(attribute, model)
                self.attribute_panel_view.create_spinbox(model, attribute, row_index, min_value, max_value)
            else:
                getattr(self.attribute_panel_view, f"create_{widget_type}")(model, attribute, row_index)

            row_index += 1

    #Internals----------------------------------------------------------------------------------------------------------
    def _compute_spinbox_limits(self, attribute, model) -> tuple[int, int]:
        """return numeric min/max values of the spinbox for a given attribute"""
        if attribute == "x":
            return allowed_x_range(self.canvas_width, model.width, model.anchor)
        elif attribute == "y":
            return allowed_y_range(self.canvas_height, model.height, model.anchor)
        elif attribute == "width":
            return 1, self.canvas_width
        elif attribute == "height":
            return 1, self.canvas_height

    #Helpers------------------------------------------------------------------------------------------------------------
    def update_spinbox_limits(self, model):
        """refresh existing spinbox limits when size or anchor changes"""
        spinbox_limits = {}
        if "x" in self.attribute_panel_view.spinboxes:
            spinbox_limits["x"] = self._compute_spinbox_limits("x", model)
        if "y" in self.attribute_panel_view.spinboxes:
            spinbox_limits["y"] = self._compute_spinbox_limits("y", model)
        self.attribute_panel_view.apply_spinbox_limits(spinbox_limits)