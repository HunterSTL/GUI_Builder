import tkinter as tk

#mapping internal attribute names to display names for the attribute panel
DISPLAY_NAMES = {
    "type": "Widget Type:",
    "id": "Widget ID:",
    "x": "X Position:",
    "y": "Y Position:",
    "width": "Width:",
    "height": "Height:",
    "text": "Text:",
    "bg": "BG Color:",
    "fg": "FG Color:",
    "anchor": "Anchor:"
}

class AttributesPanelView:
    """
    Tk‑only view responsible for rendering/editing widget attributes, binding
    tk variables to controller callbacks and synchronizing displayed values.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        frame: tk.Frame,
        panel_color: str,
        widget_color: str,
        text_color: str,
        on_attribute_changed_callback
    ):
        """initialize the panel layout, styling and registries"""
        self.frame = frame
        self.frame.columnconfigure(0, minsize=50)
        self.panel_color = panel_color
        self.widget_color = widget_color
        self.text_color = text_color

        self.active_model_id = None     #model_id of the currently selected widget

        self.spinboxes = {}             #{attribute_name: tk.Spinbox}
        self._variables = {}            #{attribute_name: tk.Variable}

        self._silent_update = False

        #call Designer._on_attribute_changed() to apply changes from the attributes panel to the model
        self.on_attribute_changed_callback = on_attribute_changed_callback

    #Rendering API------------------------------------------------------------------------------------------------------
    def clear_panel(self):
        """destroy all widgets inside the attributes panel frame"""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self._variables.clear()
        self.spinboxes.clear()

    def create_display_name_label(self, attribute, row):
        """create a display name label for an attribute in the left column"""
        tk.Label(
            self.frame,
            text=DISPLAY_NAMES.get(attribute),
            bg=self.panel_color,
            fg=self.text_color,
            pady=3
        ).grid(column=0, row=row, sticky="W")

    def create_label(self, model, attribute, row):
        """create a static text label for read-only attributes"""
        tk.Label(
            self.frame,
            text=getattr(model, attribute),
            bg=self.panel_color,
            fg=self.text_color
        ).grid(column=1, row=row, sticky="W")

    def create_entry(self, model, attribute, row):
        """create a text entry for string attributes"""
        variable = tk.StringVar(value=str(getattr(model, attribute)))
        tk.Entry(
            self.frame,
            bg=self.widget_color,
            fg=self.text_color,
            width=18,
            textvariable=variable
        ).grid(column=1, row=row)
        self._bind_variables(attribute, variable)

    def create_spinbox(self, model, attribute, row, min_value, max_value):
        """create a spinbox for numeric attributes with range validation"""
        variable = tk.StringVar(value=str(getattr(model, attribute)))

        #validate user input so spinbox limits are enforced even with manual input
        def _validate_spinbox(proposed: str):
            #allow empty during editing
            if proposed == "":
                return True
            #only allow digits
            if not proposed.isdigit():
                return False
            #only allow in range of the spinbox limit
            try:
                value = int(proposed)
            except ValueError:
                return False
            return min_value <= value <= max_value

        validation_command = (self.frame.register(_validate_spinbox), "%P")

        spinbox = tk.Spinbox(
            self.frame,
            from_=min_value,
            to=max_value,
            width=5,
            bg=self.widget_color,
            fg=self.text_color,
            buttonbackground=self.widget_color,
            increment=1,
            textvariable=variable,
            validate="key",
            validatecommand=validation_command,
            wrap=False
        )
        spinbox.grid(column=1, row=row, sticky="W")

        #store spinbox so the max value can be adjusted later if size or anchor change
        self.spinboxes[attribute] = spinbox

        self._bind_variables(attribute, variable)

    def create_colorpicker(self, model, attribute, row):
        """create a color preview box for color attributes (not fully implemented)"""
        tk.Label(
            self.frame,
            bg=getattr(model, attribute),
            width=5,
            relief="raised"
        ).grid(column=1, row=row, sticky="W")

    def create_combobox(self, model, attribute, row):
        """create a combobox for enumerated attributes (e.g., anchor)"""
        if attribute == "anchor":
            variable = tk.StringVar(value=str(getattr(model, attribute)))
            spinbox = tk.Spinbox(
                self.frame,
                values=("n", "ne", "e", "se", "s", "sw", "w", "nw", "center"),
                width=6,
                bg=self.widget_color,
                fg=self.text_color,
                buttonbackground=self.widget_color,
                textvariable=variable
            )
            spinbox.grid(column=1, row=row, sticky="W")

            #force-sync after widget exists
            self._silent_update = True
            variable.set(str(getattr(model, attribute)))
            self._silent_update = False

            self._bind_variables(attribute, variable)

    #Internals----------------------------------------------------------------------------------------------------------
    def _bind_variables(self, attribute: str, variable: tk.Variable):
        """bind tk variable changes to the update callback (applies changes to the model)"""
        def _on_write(*_):
            if self._silent_update:
                return

            value = variable.get()

            if attribute in ["x", "y", "width", "height"]:
                try:
                    value = int(value)
                except ValueError:
                    return

            self.on_attribute_changed_callback(self.active_model_id, attribute, value)

        self._variables[attribute] = variable
        variable.trace_add("write", _on_write)

    #Helpers------------------------------------------------------------------------------------------------------------
    def update_variables_from_model(self, model, attributes=None):
        """sync tk.Variable values with current model state (silent update)"""
        self._silent_update = True
        for attribute, variable in self._variables.items():
            if attributes and attribute not in attributes:
                continue
            try:
                variable.set(getattr(model, attribute))
            except Exception:
                variable.set(str(getattr(model, attribute)))
        self._silent_update = False

    def apply_spinbox_limits(self, spinbox_limits: dict):
        """update the min/max values of existing spinboxes"""
        for attribute, (min_value, max_value) in spinbox_limits.items():
            self.spinboxes[attribute].config(from_=min_value, to=max_value)

    def set_active_model_id(self, model_id):
        """store the model_id of the currently displayed widget"""
        self.active_model_id = model_id