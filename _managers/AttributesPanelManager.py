import tkinter as tk
from Geometry import allowed_x_range, allowed_y_range

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

class AttributesPanelManager:
    def __init__(
        self,
        root: tk.Toplevel,
        frame: tk.Frame,
        canvas_width: int,
        canvas_height: int,
        panel_color: str,
        widget_color: str,
        text_color: str,
        selection_manager,
        callbacks: dict
    ):
        """initialize the attributes panel manager and build internal state"""
        self.root = root
        self.frame = frame
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.panel_color = panel_color
        self.widget_color = widget_color
        self.text_color = text_color
        self.selection_manager = selection_manager
        self.callbacks = callbacks

        self.frame.columnconfigure(0, minsize=50)
        self._spinboxes = {}
        self._variables = {}    #{attribute_name: tk.Variable}
        self._silent_update = False

    def refresh(self, model):
        """refresh the panel by repopulating it with model attributes"""
        self._clear_panel()
        self._populate(model)

    def clear(self):
        """clear the entire panel"""
        self._clear_panel()

    def update_variable_from_model(self, model, attributes=None):
        """update all variable values from the model"""
        self._silent_update = True
        for attribute, variable in self._variables.items():
            if attributes and attribute not in attributes:
                continue
            try:
                variable.set(getattr(model, attribute))
            except Exception:
                variable.set(str(getattr(model, attribute)))
        self._silent_update = False

    def update_spinbox_limits(self, model):
        """recompute allowed x/y ranges when size or anchor changes"""
        if "x" in self._spinboxes:
            new_min_value, new_max_value = allowed_x_range(self.canvas_width, model.width, model.anchor)
            self._spinboxes["x"].config(from_=new_min_value, to=new_max_value)
        if "y" in self._spinboxes:
            new_min_value, new_max_value = allowed_y_range(self.canvas_height, model.height, model.anchor)
            self._spinboxes["y"].config(from_=new_min_value, to=new_max_value)

    def _populate(self, model):
        """populate the panel with widgets representing model attributes"""
        #clear previous widgets
        self._clear_panel()

        row_index = 0

        for attribute, widget_type in ATTRIBUTE_CONFIG[model.type].items():
            #create displayname for each attribute
            self._create_displayname_label(attribute, row_index)
            #create the correct widget based on widget_type
            getattr(self, f"_create_{widget_type}")(model, attribute, row_index)
            row_index += 1

    def _clear_panel(self):
        """destroy all widgets in the attributes panel"""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self._variables.clear()
        self._spinboxes.clear()

    def _bind_variables(self, attribute: str, variable: tk.Variable):
        """bind a Tk variable so updates propagate into Designer callbacks"""
        def _on_write(*_):
            if self._silent_update:
                return

            value = variable.get()

            if attribute in ["x", "y", "width", "height"]:
                try:
                    value = int(value)
                except ValueError:
                    return

            #delegate the entire mutation to Designer
            model_id = self.selection_manager.last_selected_model_id()
            if not model_id:
                return

            self.callbacks["attribute_changed"](model_id, attribute, value)

        self._variables[attribute] = variable
        variable.trace_add("write", _on_write)

    def _create_displayname_label(self, attribute, row):
        """create the displayname label for an attribute row"""
        tk.Label(
            self.frame,
            text=DISPLAY_NAMES.get(attribute),
            bg=self.panel_color,
            fg=self.text_color,
            pady=3
        ).grid(column=0, row=row, sticky="W")

    def _create_label(self, model, attribute, row):
        """create a static text label for read-only attributes"""
        tk.Label(
            self.frame,
            text=getattr(model, attribute),
            bg=self.panel_color,
            fg=self.text_color
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(self, model, attribute, row):
        """create a text entry for string attributes"""
        variable = tk.StringVar(value=str(getattr(model, attribute)))
        entry = tk.Entry(
            self.frame,
            bg=self.widget_color,
            fg=self.text_color,
            width=18,
            textvariable=variable
        )
        entry.grid(column=1, row=row)
        self._bind_variables(attribute, variable)

    def _create_spinbox(self, model, attribute, row):
        """create a spinbox for numeric attributes with range validation"""
        min_value = 0
        max_value = 0

        if attribute == "x":
            min_value, max_value = allowed_x_range(self.canvas_width, model.width, model.anchor)
        elif attribute == "y":
            min_value, max_value = allowed_y_range(self.canvas_height, model.height, model.anchor)
        elif attribute == "width":
            min_value = 1
            max_value = self.canvas_width // 2
        elif attribute == "height":
            min_value = 1
            max_value = self.canvas_height // 2

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
        self._spinboxes[attribute] = spinbox

        self._bind_variables(attribute, variable)

    def _create_colorpicker(self, model, attribute, row):
        """create a color preview box for color attributes (not fully implemented)"""
        tk.Label(
            self.frame,
            bg=getattr(model, attribute),
            width=5,
            relief="raised"
        ).grid(column=1, row=row, sticky="W")

    def _create_combobox(self, model, attribute, row):
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