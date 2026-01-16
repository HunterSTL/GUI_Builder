import tkinter as tk
from ProjectDocument import ProjectDocument

#attributes that can be shown in the attributes panel including the type of widget
#to display the value with (text field, numeric input, color picker, dropwodn etc.)
ATTRIBUTE_CONFIG = {
    "Label": {
        "type": "label",
        "id": "entry",
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
        "id": "entry",
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
        "id": "entry",
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
    "id": "Widget Name:",
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
    def __init__(self, root, frame, project_document: ProjectDocument, window_height, panel_width, panel_height, selection_manager, widget_manager):
        self.root = root
        self.frame = frame
        self.project_document = project_document
        self.window_height = window_height
        self.panel_width = panel_width
        self.panel_height = panel_height
        self.selection_manager = selection_manager
        self.widget_manager = widget_manager

        self._visible = False
        self.frame.columnconfigure(0, minsize=50)
        self._spinboxes = {}
        self._variables = {}    #{attribute_name: tk.Variable}
        self._silent_update = False

    def show(self, model):
        if self._visible:
            #already visible → refresh contents
            self._populate(model)
            return

        #resize window
        if self.panel_height > self.window_height:
            self.root.geometry(f"{self.project_document.width + self.panel_width}x{self.panel_height}")
        else:
            self.root.geometry(f"{self.project_document.width + self.panel_width}x{self.window_height}")

        #pack attributes panel
        self.frame.pack(side="right", fill="y")

        self._populate(model)
        self._visible = True

    def hide(self):
        if not self._visible:
            #already hidden → do nothing
            return

        #resize window
        self.root.geometry(f"{self.project_document.width}x{self.window_height}")

        #remove attributes panel
        self.frame.pack_forget()

        #clear panel contents
        self._clear_panel()

        self._visible = False

    def _populate(self, model):
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
        for widget in self.frame.winfo_children():
            widget.destroy()
        self._variables.clear()
        self._spinboxes.clear()

    def _bind_variables(self, attribute: str, variable: tk.Variable, model):
        def _on_write(*_):
            if self._silent_update:
                return

            value = variable.get()

            if attribute in ["x", "y", "width", "height"]:
                try:
                    value = int(value)
                except ValueError:
                    return

            #update widget
            item_id = self.selection_manager.last_selected_id()
            self.widget_manager.update_widget_attribute(item_id, attribute, value)

            #update model
            setattr(model, attribute, value)

            #update max_value for spinboxes
            if attribute in ["anchor", "width", "height"]:
                self._update_spinbox_limits(model)

            #refresh outline
            self.selection_manager.refresh(item_id)

        self._variables[attribute] = variable
        variable.trace_add("write", _on_write)

    def update_variable_from_model(self, model, attributes=None):
        self._silent_update = True
        for attribute, variable in self._variables.items():
            if attributes and attribute not in attributes:
                continue
            try:
                variable.set(getattr(model, attribute))
            except Exception:
                variable.set(str(getattr(model, attribute)))
        self._silent_update = False

    def _create_displayname_label(self, attribute, row):
        tk.Label(
            self.frame,
            text=DISPLAY_NAMES.get(attribute),
            bg=self.project_document.theme["attributes_panel"]["color"],
            fg=self.project_document.theme["label"]["fg"],
            pady=3
        ).grid(column=0, row=row, sticky="W")

    def _create_label(self, model, attribute, row):
        tk.Label(
            self.frame,
            text=getattr(model, attribute),
            bg=self.project_document.theme["attributes_panel"]["color"],
            fg=self.project_document.theme["label"]["fg"]
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(self, model, attribute, row):
        variable = tk.StringVar(value=str(getattr(model, attribute)))
        entry = tk.Entry(
            self.frame,
            bg=self.project_document.theme["entry"]["bg"],
            fg=self.project_document.theme["entry"]["fg"],
            width=18,
            textvariable=variable
        )
        entry.grid(column=1, row=row)
        self._bind_variables(attribute, variable, model)

    def _create_spinbox(self, model, attribute, row):
        min_value = 0
        max_value = 0

        if attribute == "x":
            min_value = self._compute_minimum_x(model)
            max_value = self._compute_maximum_x(model)
        elif attribute == "y":
            min_value = self._compute_minimum_y(model)
            max_value = self._compute_maximum_y(model)
        elif attribute == "width":
            min_value = 1
            max_value = self.project_document.width // 2
        elif attribute == "height":
            min_value = 1
            max_value = self.project_document.height // 2

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
            bg=self.project_document.theme["entry"]["bg"],
            fg=self.project_document.theme["entry"]["fg"],
            buttonbackground=self.project_document.theme["entry"]["bg"],
            increment=1,
            textvariable=variable,
            validate="key",
            validatecommand=validation_command,
            wrap=False
        )
        spinbox.grid(column=1, row=row, sticky="W")

        #store spinbox so the max value can be adjusted later if size or anchor change
        self._spinboxes[attribute] = spinbox

        self._bind_variables(attribute, variable, model)

    def _create_colorpicker(self, model, attribute, row):
        tk.Label(
            self.frame,
            bg=getattr(model, attribute),
            width=5,
            relief="raised"
        ).grid(column=1, row=row, sticky="W")

    def _create_combobox(self, model, attribute, row):
        if attribute == "anchor":
            variable = tk.StringVar(value=str(getattr(model, attribute)))
            spinbox = tk.Spinbox(
                self.frame,
                values=("n", "ne", "e", "se", "s", "sw", "w", "nw", "center"),
                width=6,
                bg=self.project_document.theme["entry"]["bg"],
                fg=self.project_document.theme["entry"]["fg"],
                buttonbackground=self.project_document.theme["entry"]["bg"],
                textvariable=variable
            )
            spinbox.grid(column=1, row=row, sticky="W")

            #force-sync after widget exists
            self._silent_update = True
            variable.set(str(getattr(model, attribute)))
            self._silent_update = False

            self._bind_variables(attribute, variable, model)

    def _compute_maximum_x(self, model):
        if model.anchor in ["sw", "w", "nw"]:
            return self.project_document.width - model.width
        elif model.anchor in ["ne", "e", "se"]:
            return self.project_document.width
        elif model.anchor in ["n", "s", "center"]:
            return self.project_document.width - (model.width // 2)
        return self.project_document.width

    @staticmethod
    def _compute_minimum_x(model):
        if model.anchor in ["sw", "w", "nw"]:
            return 0
        elif model.anchor in ["ne", "e", "se"]:
            return model.width
        elif model.anchor in ["n", "s", "center"]:
            return model.width // 2
        return 0

    def _compute_maximum_y(self, model):
        if model.anchor in ["sw", "s", "se"]:
            return self.project_document.height
        elif model.anchor in ["nw", "n", "ne"]:
            return self.project_document.height - model.height
        elif model.anchor in ["w", "e", "center"]:
            return self.project_document.height - (model.height // 2)
        return self.project_document.height

    @staticmethod
    def _compute_minimum_y(model):
        if model.anchor in ["sw", "s", "se"]:
            return model.height
        elif model.anchor in ["nw", "n", "ne"]:
            return 0
        elif model.anchor in ["w", "e", "center"]:
            return model.height // 2
        return 0

    def _update_spinbox_limits(self, model):
        if "x" in self._spinboxes:
            new_min_value = self._compute_minimum_x(model)
            new_max_value = self._compute_maximum_x(model)
            self._spinboxes["x"].config(from_=new_min_value, to=new_max_value)
        if "y" in self._spinboxes:
            new_min_value = self._compute_minimum_y(model)
            new_max_value = self._compute_maximum_y(model)
            self._spinboxes["y"].config(from_=new_min_value, to=new_max_value)