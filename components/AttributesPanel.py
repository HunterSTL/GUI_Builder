import tkinter as tk
from tkinter import colorchooser
from model import BaseWidget
from utility import allowed_x_range, allowed_y_range, WidgetType
from utility.AppTheme import ATTRIBUTES_PANEL_COLOR, ATTRIBUTES_PANEL_WIDGET_COLOR, ATTRIBUTES_PANEL_TEXT_COLOR
from utility.Constants import ATTRIBUTES_PANEL_WIDTH

class AttributesPanel:
    """
    Self contained component for displaying and editing the selected widget's attributes.

    The panel builds the appropriate editor widgets for a single selected widget,
    clears itself when no or more than one widget is selected,
    updates displayed variables from the widget when a single selected widget changes
    and invokes a callback so user edits propagate to the widget.
    """
    def __init__(
        self,
        parent: tk.Frame,
        canvas_width: int,
        canvas_height: int,
        on_attribute_panel_edit_callback
    ) -> None:
        """initialize the panel layout, styling and registries"""
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._on_attribute_panel_edit_callback = on_attribute_panel_edit_callback

        self._variables: dict[str, tk.Variable] = {}
        self._spinboxes: dict[str, tk.Spinbox] = {}
        self._colorpickers: dict[str, tk.Button] = {}
        self._silent_mode: bool = False
        self._edit_in_progress: bool = False

        self._frame = tk.Frame(
            parent,
            width=ATTRIBUTES_PANEL_WIDTH,
            bg=ATTRIBUTES_PANEL_COLOR
        )
        self._frame.grid_propagate(False)   #fixed width
        self._frame.columnconfigure(0, minsize=50)

        self._attribute_config = {  #maps widget types to their respective attribute config
            WidgetType.LABEL: {     #defines which widget attributes to show in the panel including the editor widget to display the value with
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
    def set_selection(self, selection: tuple[BaseWidget, ...]) -> None:
        """build the panel when exactly one widget is selected, otherwise clear the panel"""
        if len(selection) == 1:
            widget = selection[0]
            self._build(widget)
        else:
            self._clear()

    def refresh_from_widget(self, widget: BaseWidget) -> None:
        """refresh the panel from the widget by updating variable values, spinbox limits and colorpicker previews without producing user edit events"""
        self._silent_mode = True
        try:
            self._update_variables_from_widget(widget)
            self._update_spinbox_limits_from_widget(widget)
            self._update_colorpicker_previews_from_widget(widget)
        finally:    #ensures silent mode is reset even if an error occurs
            self._silent_mode = False

    def commit_active_edit(self) -> None:
        """commit the active attribute edit if one is in progress"""
        self._end_attribute_edit()

    #Internals----------------------------------------------------------------------------------------------------------
    def _build(self, widget: BaseWidget) -> None:
        """build the panel with editor widgets representing widget attributes"""
        self._clear()
        row_index = 0

        config = self._attribute_config[widget.type]

        for attribute, widget_type in config.items():
            #create displayname and appropriate editor widget for the widget type
            self._create_display_name_label(attribute, row_index)
            getattr(self, f"_create_{widget_type}")(widget, attribute, row_index)
            row_index += 1

    def _clear(self) -> None:
        """end the active edit, destroy all editor widgets inside the frame and clear editor mappings"""
        self._end_attribute_edit()

        for editor_widget in self._frame.winfo_children():
            editor_widget.destroy()

        self._variables.clear()
        self._spinboxes.clear()
        self._colorpickers.clear()

    def _update_variables_from_widget(self, widget: BaseWidget) -> None:
        """update variable values from the widget"""
        for attribute, variable in self._variables.items():
            variable.set(str(getattr(widget, attribute)))

    def _update_spinbox_limits_from_widget(self, widget: BaseWidget) -> None:
        """update spinbox limits from the widget"""
        spinbox_limits = {}

        if "x" in self._spinboxes:
            spinbox_limits["x"] = self._compute_spinbox_limits(widget, "x")
        if "y" in self._spinboxes:
            spinbox_limits["y"] = self._compute_spinbox_limits(widget, "y")

        for attribute, (min_value, max_value) in spinbox_limits.items():
            self._spinboxes[attribute].config(
                from_=min_value,
                to=max_value
            )

            if min_value == max_value:  #Tk does not clamp when the range collapses to a single value
                variable = self._variables[attribute]
                variable.set(str(min_value))

    def _update_colorpicker_previews_from_widget(self, widget: BaseWidget) -> None:
        """update the colorpicker previews from the widget"""
        for attribute, colorpicker in self._colorpickers.items():
            colorpicker.config(bg=getattr(widget, attribute))

    def _compute_spinbox_limits(self, widget: BaseWidget, attribute: str) -> tuple[int, int]:
        """return numeric minimum and maximum values of the spinbox for a given attribute"""
        if attribute == "x":
            return allowed_x_range(self._canvas_width, widget.width, widget.anchor)
        elif attribute == "y":
            return allowed_y_range(self._canvas_height, widget.height, widget.anchor)
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

    def _change_color(self, variable: tk.Variable) -> None:
        """prompt for a color then apply it as a complete edit"""
        _, color = colorchooser.askcolor(
            color=variable.get(),
            parent=self._frame.winfo_toplevel() #disables interaction with the designer while the dialog is shown
        )

        if color is None:
            return

        self._apply_complete_edit(variable, color)

    #Widgets------------------------------------------------------------------------------------------------------------
    def _create_display_name_label(self, attribute: str, row: int) -> None:
        """create a display name label for an attribute in the left column"""
        tk.Label(
            self._frame,
            text=self._display_names.get(attribute),
            bg=ATTRIBUTES_PANEL_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR,
            pady=3
        ).grid(column=0, row=row, sticky="W")

    def _create_label(self, widget: BaseWidget, attribute: str, row: int) -> None:
        """create a static text label for read only attributes"""
        tk.Label(
            self._frame,
            text=getattr(widget, attribute),
            bg=ATTRIBUTES_PANEL_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(self, widget: BaseWidget, attribute: str, row: int) -> None:
        """create a text entry for string attributes"""
        variable = tk.StringVar(value=str(getattr(widget, attribute)))
        entry = tk.Entry(
            self._frame,
            bg=ATTRIBUTES_PANEL_WIDGET_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR,
            width=18,
            textvariable=variable
        )
        entry.grid(column=1, row=row)
        entry.bind("<FocusOut>", lambda *_: self._end_attribute_edit())

        self._bind_variable(attribute, variable)

    def _create_spinbox(self, widget: BaseWidget, attribute: str, row: int) -> None:
        """create a spinbox for numeric attributes with range validation"""
        variable = tk.StringVar(value=str(getattr(widget, attribute)))
        min_value, max_value = self._compute_spinbox_limits(widget, attribute)

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
            bg=ATTRIBUTES_PANEL_WIDGET_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR,
            buttonbackground=ATTRIBUTES_PANEL_WIDGET_COLOR,
            increment=1,
            textvariable=variable,
            validate="key",
            validatecommand=validation_command,
            wrap=False
        )
        spinbox.grid(column=1, row=row, sticky="W")
        spinbox.bind("<FocusOut>", lambda *_: self._end_attribute_edit())
        spinbox.bind("<Leave>", lambda *_: self._end_attribute_edit())  #arrow button clicks do not trigger focus events

        self._spinboxes[attribute] = spinbox    #store spinbox so its limits can be adjusted when size or anchor change
        self._bind_variable(attribute, variable)

    def _create_colorpicker(self, widget: BaseWidget, attribute: str, row: int) -> None:
        """create a button with color preview for color attributes"""
        if attribute in ["bg", "fg"]:
            variable = tk.StringVar(value=str(getattr(widget, attribute)))
            colorpicker = tk.Button(
                self._frame,
                bg=getattr(widget, attribute),
                relief="raised",
                width=3,
                command=lambda: self._change_color(variable)
            )
            colorpicker.grid(column=1, row=row, pady=2, sticky="W")

            self._colorpickers[attribute] = colorpicker #store colorpicker so its preview can be updated
            self._bind_variable(attribute, variable)
        else:
            raise ValueError(f"AttributesPanel - colorpicker creation failed: unsupported attribute \"{attribute}\"")

    def _create_combobox(self, widget: BaseWidget, attribute: str, row: int) -> None:
        """create a menu based selector for enumerated attributes"""
        if attribute == "anchor":
            variable = tk.StringVar(value=str(getattr(widget, attribute)))
            menu_button = tk.Menubutton(
                self._frame,
                textvariable=variable,
                bg=ATTRIBUTES_PANEL_WIDGET_COLOR,
                fg=ATTRIBUTES_PANEL_TEXT_COLOR,
                relief="raised",
                width=5
            )
            menu = tk.Menu(
                menu_button,
                bg=ATTRIBUTES_PANEL_WIDGET_COLOR,
                fg=ATTRIBUTES_PANEL_TEXT_COLOR,
                tearoff=0
            )
            menu_button.config(menu=menu)
            menu_button.grid(column=1, row=row, pady=2, sticky="W")

            for anchor in ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"]:
                menu.add_command(
                    label=anchor,
                    command=lambda value=anchor: self._apply_complete_edit(
                        variable=variable,
                        value=value
                    )
                )

            self._bind_variable(attribute, variable)
        else:
            raise ValueError(f"AttributesPanel - combobox creation failed: unsupported attribute \"{attribute}\"")

    #Propagation--------------------------------------------------------------------------------------------------------
    def _bind_variable(self, attribute: str, variable: tk.Variable) -> None:
        """bind Tk.Variable writes to a callback so attribute changes can propagate to the widget"""
        def handle_write(_name: str, _index: str, _mode: str) -> None:
            self._handle_attribute_edit(attribute, variable)

        self._variables[attribute] = variable
        variable.trace_add("write", handle_write)

    def _start_attribute_edit(self) -> None:
        """start an edit if one is not already in progress"""
        if self._edit_in_progress:
            return

        self._edit_in_progress = True
        self._on_attribute_panel_edit_callback(
            phase="start"
        )

    def _handle_attribute_edit(self, attribute: str, variable: tk.Variable) -> None:
        """propagate live changes to the widget"""
        if self._silent_mode:           #prevents propagating variable writes back to the widget when refreshing the panel from the widget
            return

        self._start_attribute_edit()

        value = variable.get()

        if attribute in ["x", "y", "width", "height"]:
            try:
                value = int(value)
            except ValueError:
                return

        self._on_attribute_panel_edit_callback(
            phase="apply_change",
            attribute=attribute,
            value=value
        )

    def _end_attribute_edit(self) -> None:
        """commit the active attribute edit if one is in progress"""
        if not self._edit_in_progress:
            return

        self._edit_in_progress = False
        self._on_attribute_panel_edit_callback(
            phase="commit"
        )

    def _apply_complete_edit(self, variable: tk.Variable, value: str) -> None:
        """apply a value using the complete edit lifecycle"""
        if value == variable.get():
            return

        self._start_attribute_edit()
        variable.set(value)
        self._end_attribute_edit()
