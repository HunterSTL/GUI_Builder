import tkinter as tk
from Theme import *

class AttributesPanelManager:
    def __init__(self, root, frame, theme, canvas_width, canvas_height, panel_width, selection_manager, widget_manager):
        self.root = root
        self.frame = frame
        self.theme = theme
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.panel_width = panel_width
        self.selection_manager = selection_manager
        self.widget_manager = widget_manager
        self._visible = False
        self.frame.columnconfigure(0, minsize=50)
        self._variables = {}    #{attribute_name: tk.Variable}
        self._silent_update = False

    def show(self, model):
        if self._visible:
            #already visible → refresh contents
            self._populate(model)
            return

        self.root.update_idletasks()

        #resize window
        self.root.geometry(f"{self.canvas_width + self.panel_width}x{self.canvas_height}")

        #pack attributes panel
        self.frame.pack(side="right", fill="y")

        self._populate(model)
        self._visible = True

    def hide(self):
        if not self._visible:
            #already hidden → do nothing
            return

        #resize window
        self.root.geometry(f"{self.canvas_width}x{self.canvas_height}")

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

    def _bind_variables(self, attribute: str, variable: tk.Variable, model):
        def _on_write(*_):
            if self._silent_update:
                return

            value = variable.get()

            if attribute in ("x", "y", "width", "height"):
                try:
                    value = int(value)
                except ValueError:
                    return

            #update widget
            item_id = self.selection_manager.last_selected_id()
            self.widget_manager.update_widget_attribute(item_id, attribute, value)

            #update model
            setattr(model, attribute, value)

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
            bg=self.theme.get("background_color"),
            fg=self.theme.get("text_color"),
            pady=3
        ).grid(column=0, row=row, sticky="E")

    def _create_label(self, model, attribute, row):
        tk.Label(
            self.frame,
            text=getattr(model, attribute),
            bg=self.theme.get("background_color"),
            fg=self.theme.get("text_color")
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(self, model, attribute, row):
        variable = tk.StringVar(value=str(getattr(model, attribute)))
        entry = tk.Entry(
            self.frame,
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            width=18,
            textvariable=variable
        )
        entry.grid(column=1, row=row)
        self._bind_variables(attribute, variable, model)

    def _create_spinbox(self, model, attribute, row):
        if attribute == "x":
            max_value = self.canvas_width
        elif attribute == "y":
            max_value = self.canvas_height
        elif attribute == "width":
            max_value = self.canvas_width // 2
        elif attribute == "height":
            max_value = self.canvas_height // 2
        else:
            max_value = 0

        variable = tk.IntVar(value=getattr(model, attribute))
        spinbox = tk.Spinbox(
            self.frame,
            from_=0,
            to=max_value,
            width=5,
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            buttonbackground=ENTRY_COLOR,
            increment=1,
            textvariable=variable
        )
        spinbox.grid(column=1, row=row, sticky="W")
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
                bg=ENTRY_COLOR,
                fg=TEXT_COLOR,
                buttonbackground=ENTRY_COLOR,
                textvariable=variable
            )
            spinbox.grid(column=1, row=row, sticky="W")
            self._bind_variables(attribute, variable, model)