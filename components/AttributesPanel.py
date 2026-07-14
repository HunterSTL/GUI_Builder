import tkinter as tk
from model import BaseWidgetData
from utility import allowed_x_range, allowed_y_range, WidgetType

class AttributesPanel:
    """
    Self contained component for displaying and editing the selected widget's attributes.

    The panel builds the appropriate editor widgets for a single selected model,
    clears itself when no or more than one widget is selected,
    updates displayed variables from the model when a single selected model changes
    and invokes a callback so user edits propagate to the model.
    """
    def __init__(
        self,
        parent: tk.Frame,
        canvas_width: int,
        canvas_height: int,
        panel_width: int,
        panel_color: str,
        widget_color: str,
        text_color: str,
        on_attribute_changed_callback
    ) -> None:
        """initialize the panel layout, styling and registries"""
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._panel_width = panel_width
        self._panel_color = panel_color
        self._widget_color = widget_color
        self._text_color = text_color
        self._on_attribute_changed_callback = on_attribute_changed_callback

        self._spinboxes: dict[str, tk.Spinbox] = {}
        self._variables: dict[str, tk.Variable] = {}
        self._active_model_id: str | None = None
        self._silent_model: bool = False

        self._frame = tk.Frame(
            parent,
            width=self._panel_width,
            bg=self._panel_color
        )
        self._frame.grid_propagate(False)   #fixed width
        self._frame.columnconfigure(0, minsize=50)

        self._attribute_config = {  #maps widget types to their respective attribute config
            WidgetType.LABEL: {     #defines which model attributes to show in the panel including the widget to display the value with
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
            WidgetType.ENTRY: {
                "id": "label",
                "x": "spinbox",
                "y": "spinbox",
                "width": "spinbox",
                "height": "spinbox",
                "bg": "colorpicker",
                "fg": "colorpicker",
                "anchor": "combobox"
            },
            WidgetType.BUTTON: {
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

        self._display_names = {     #maps internal attribute names to display names
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

    @property
    def frame(self) -> tk.Frame:
        return self._frame

    #Public API---------------------------------------------------------------------------------------------------------
    def set_selection(self, selection: tuple[BaseWidgetData, ...]) -> None:
        """build the panel when exactly one widget is selected, otherwise clear the panel"""
        if len(selection) == 1:
            model = selection[0]
            self._active_model_id = model.id
            self._build(model)
        else:
            self._active_model_id = None
            self._clear()

    def update_variables_from_model(self, model: BaseWidgetData) -> None:
        """update variable values from the model"""
        self._silent_model = True
        try:
            for attribute, variable in self._variables.items():
                try:
                    variable.set(getattr(model, attribute))
                except Exception:
                    variable.set(str(getattr(model, attribute)))
        finally:    #ensures silent mode is reset even if an error occurs
            self._silent_model = False

    def update_spinbox_limits_from_model(self, model: BaseWidgetData) -> None:
        """update spinbox limits from the model"""
        spinbox_limits = {}

        if "x" in self._spinboxes:
            spinbox_limits["x"] = self._compute_spinbox_limits(model, "x")
        if "y" in self._spinboxes:
            spinbox_limits["y"] = self._compute_spinbox_limits(model, "y")

        for attribute, (min_value, max_value) in spinbox_limits.items():
            self._spinboxes[attribute].config(  #tk normally clamps out of range values and the configuration of the spinbox causes the correction to propagate to the model
                from_=min_value,
                to=max_value
            )

            if min_value == max_value:          #tk does not clamp when the range collapses to a single value
                variable = self._variables[attribute]
                variable.set(min_value)

    #Internals----------------------------------------------------------------------------------------------------------
    def _build(self, model: BaseWidgetData) -> None:
        """build the panel with widgets representing model attributes"""
        self._clear()
        row_index = 0

        config = self._attribute_config.get(model.type)
        if not config:
            raise ValueError(f"AttributesPanel - rendering failed: unsupported type \"{model.type}\"")

        for attribute, widget_type in config.items():
            #create displayname and appropriate editor widget for the widget type
            self._create_display_name_label(attribute, row_index)
            getattr(self, f"_create_{widget_type}")(model, attribute, row_index)
            row_index += 1

    def _clear(self) -> None:
        """destroy all widgets inside the frame and clear variable and spinbox mappings"""
        for widget in self._frame.winfo_children():
            widget.destroy()
        self._variables.clear()
        self._spinboxes.clear()

    def _compute_spinbox_limits(self, model: BaseWidgetData, attribute: str) -> tuple[int, int]:
        """return numeric minimum and maximum values of the spinbox for a given attribute"""
        if attribute == "x":
            return allowed_x_range(self._canvas_width, model.width, model.anchor)
        elif attribute == "y":
            return allowed_y_range(self._canvas_height, model.height, model.anchor)
        elif attribute == "width":
            return 1, self._canvas_width
        elif attribute == "height":
            return 1, self._canvas_height

        raise ValueError(f"AttributesPanel - spinbox limit computation failed: unsupported attribute \"{attribute}\"")

    def _validate_spinbox_input(self, proposed_value: str, widget_name: str) -> bool:
        """validate spinbox input against the spinbox's current limits"""
        if proposed_value == "":    #allows empty values while editing
            return True

        if not proposed_value.isdigit():
            return False

        try:
            value = int(proposed_value)
        except ValueError:
            return False

        spinbox = self._frame.nametowidget(widget_name)
        min_value = spinbox.cget("from")
        max_value = spinbox.cget("to")
        return min_value <= value <= max_value

    #Widgets------------------------------------------------------------------------------------------------------------
    def _create_display_name_label(self, attribute: str, row: int) -> None:
        """create a display name label for an attribute in the left column"""
        tk.Label(
            self._frame,
            text=self._display_names.get(attribute),
            bg=self._panel_color,
            fg=self._text_color,
            pady=3
        ).grid(column=0, row=row, sticky="W")

    def _create_label(self, model: BaseWidgetData, attribute: str, row: int) -> None:
        """create a static text label for read-only attributes"""
        tk.Label(
            self._frame,
            text=getattr(model, attribute),
            bg=self._panel_color,
            fg=self._text_color
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(self, model: BaseWidgetData, attribute: str, row: int) -> None:
        """create a text entry for string attributes"""
        variable = tk.StringVar(value=str(getattr(model, attribute)))
        tk.Entry(
            self._frame,
            bg=self._widget_color,
            fg=self._text_color,
            width=18,
            textvariable=variable
        ).grid(column=1, row=row)

        self._bind_variable(attribute, variable)

    def _create_spinbox(self, model: BaseWidgetData, attribute: str, row: int) -> None:
        """create a spinbox for numeric attributes with range validation"""
        variable = tk.StringVar(value=str(getattr(model, attribute)))
        min_value, max_value = self._compute_spinbox_limits(model, attribute)

        validation_command = (
            self._frame.register(self._validate_spinbox_input),
            "%P",   #proposed value
            "%W"    #widget name
        )

        spinbox = tk.Spinbox(
            self._frame,
            from_=min_value,
            to=max_value,
            width=5,
            bg=self._widget_color,
            fg=self._text_color,
            buttonbackground=self._widget_color,
            increment=1,
            textvariable=variable,
            validate="key",
            validatecommand=validation_command,
            wrap=False
        )
        spinbox.grid(column=1, row=row, sticky="W")

        self._spinboxes[attribute] = spinbox    #store spinbox so the limits can be adjusted later if size or anchor change
        self._bind_variable(attribute, variable)

    def _create_colorpicker(self, model: BaseWidgetData, attribute: str, row: int) -> None:
        """create a color preview box for color attributes (not fully implemented)"""
        tk.Label(
            self._frame,
            bg=getattr(model, attribute),
            width=5,
            relief="raised"
        ).grid(column=1, row=row, sticky="W")

    def _create_combobox(self, model: BaseWidgetData, attribute: str, row: int) -> None:
        """create a combobox for enumerated attributes"""
        if attribute == "anchor":
            variable = tk.StringVar(value=str(getattr(model, attribute)))
            spinbox = tk.Spinbox(
                self._frame,
                values=("n", "ne", "e", "se", "s", "sw", "w", "nw", "center"),
                width=6,
                bg=self._widget_color,
                fg=self._text_color,
                buttonbackground=self._widget_color,
                textvariable=variable
            )
            spinbox.grid(column=1, row=row, sticky="W")

            self._bind_variable(attribute, variable)

    #Propagation--------------------------------------------------------------------------------------------------------
    def _bind_variable(self, attribute: str, variable: tk.Variable) -> None:
        """bind tk.Variable writes to a callback so attribute changes can propagate to the model"""
        def _on_write(*_):
            if self._silent_model:
                return

            value = variable.get()

            if attribute in ["x", "y", "width", "height"]:
                try:
                    value = int(value)
                except ValueError:
                    return

            #invoke callback to forward attribute changes
            self._on_attribute_changed_callback(self._active_model_id, attribute, value)

        self._variables[attribute] = variable
        variable.trace_add("write", _on_write)
