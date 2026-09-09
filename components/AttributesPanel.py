import tkinter as tk
from tkinter import colorchooser
from collections.abc import Callable

from model import BaseWidget
from utility import allowed_x_range, allowed_y_range, WidgetType
from utility.AppTheme import ATTRIBUTES_PANEL_COLOR, ATTRIBUTES_PANEL_WIDGET_COLOR, ATTRIBUTES_PANEL_TEXT_COLOR
from utility.Constants import ATTRIBUTES_PANEL_WIDTH

_DISPLAYED_ATTRIBUTES_BY_WIDGET_TYPE = {
    WidgetType.LABEL: ("id", "x", "y", "width", "height", "text", "bg", "fg", "anchor"),
    WidgetType.ENTRY: ("id", "x", "y", "width", "height", "bg", "fg", "anchor"),
    WidgetType.BUTTON: ("id", "x", "y", "width", "height", "text", "bg", "fg", "anchor")
}

_DISPLAY_NAME_BY_ATTRIBUTE = {
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

_EDITOR_WIDGET_TYPE_BY_ATTRIBUTE = {
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


class AttributesPanel:
    """Displays and edits the attributes of the single selected widget through the widget edit lifecycle."""
    def __init__(
        self,
        parent: tk.Frame,
        canvas_width: int,
        canvas_height: int,
        on_edit_start: Callable[[], None],
        on_edit_change: Callable[[str, str | int], None],
        on_edit_commit: Callable[[], None]
    ) -> None:
        self._canvas_width: int = canvas_width
        self._canvas_height: int = canvas_height
        self._on_edit_start: Callable[[], None] = on_edit_start
        self._on_edit_change: Callable[[str, str | int], None] = on_edit_change
        self._on_edit_commit: Callable[[], None] = on_edit_commit

        self._variables: dict[str, tk.Variable] = {}
        self._spinboxes: dict[str, tk.Spinbox] = {}
        self._colorpickers: dict[str, tk.Button] = {}
        self._silent_mode: bool = False
        self._edit_in_progress: bool = False

        self._frame: tk.Frame = tk.Frame(
            parent,
            width=ATTRIBUTES_PANEL_WIDTH,
            bg=ATTRIBUTES_PANEL_COLOR
        )
        self._frame.grid_propagate(False)   #prevents child widgets from changing the configured panel width
        self._frame.columnconfigure(0, minsize=50)

    @property
    def frame(
        self
    ) -> tk.Frame:
        return self._frame

    def set_selection(
        self,
        selection: tuple[BaseWidget, ...]
    ) -> None:
        """Build the panel when exactly one widget is selected, otherwise clear the panel."""
        if len(selection) == 1:
            self._build(widget=selection[0])
        else:
            self._clear()

    def refresh_from_widget(
        self,
        widget: BaseWidget
    ) -> None:
        """Refresh the panel from the widget by updating variable values, spinbox limits and colorpicker previews without producing user edit events."""
        self._silent_mode = True
        try:
            self._update_variables_from_widget(widget)
            self._update_spinbox_limits_from_widget(widget)
            self._update_colorpicker_previews_from_widget(widget)
        finally:    #ensures silent mode is reset even if an error occurs
            self._silent_mode = False

    def commit_active_edit(
        self
    ) -> None:
        """Commit the active attribute edit if one is in progress."""
        self._end_attribute_edit()

    def _build(
        self,
        widget: BaseWidget
    ) -> None:
        """Build the panel with editor widgets representing widget attributes."""
        self._clear()
        displayed_attributes = _DISPLAYED_ATTRIBUTES_BY_WIDGET_TYPE[widget.type]

        for row, attribute in enumerate(displayed_attributes):
            self._create_display_name_label_for(attribute, row)
            self._create_editor_widget_for(widget, attribute, row)

    def _clear(
        self
    ) -> None:
        """End the active edit, destroy all editor widgets inside the frame and clear editor mappings."""
        self._end_attribute_edit()

        for editor_widget in self._frame.winfo_children():
            editor_widget.destroy()

        self._variables.clear()
        self._spinboxes.clear()
        self._colorpickers.clear()

    def _update_variables_from_widget(
        self,
        widget: BaseWidget
    ) -> None:
        """Update variable values from the given widget."""
        for attribute, variable in self._variables.items():
            variable.set(str(getattr(widget, attribute)))

    def _update_spinbox_limits_from_widget(
        self,
        widget: BaseWidget
    ) -> None:
        """Update spinbox limits from the given widget."""
        for attribute, spinbox in self._spinboxes.items():
            min_value, max_value = self._compute_spinbox_limits(widget, attribute)

            spinbox.config(
                from_=min_value,
                to=max_value
            )

            if min_value == max_value:  #Tk does not clamp when the range collapses to a single value
                self._variables[attribute].set(str(min_value))

    def _update_colorpicker_previews_from_widget(
        self,
        widget: BaseWidget
    ) -> None:
        """Update the colorpicker previews from the given widget."""
        for attribute, colorpicker in self._colorpickers.items():
            colorpicker.config(bg=getattr(widget, attribute))

    def _compute_spinbox_limits(
        self,
        widget: BaseWidget,
        attribute: str
    ) -> tuple[int, int]:
        """Return numeric minimum and maximum values of the spinbox for the given attribute."""
        if attribute == "x":
            return allowed_x_range(self._canvas_width, widget.width, widget.anchor)
        elif attribute == "y":
            return allowed_y_range(self._canvas_height, widget.height, widget.anchor)
        elif attribute == "width":
            return 1, self._canvas_width
        elif attribute == "height":
            return 1, self._canvas_height

        raise ValueError(f"AttributesPanel - spinbox limit computation failed: unsupported attribute \"{attribute}\"")

    def _validate_spinbox_input(
        self,
        proposed_value: str,
        widget_name: str
    ) -> bool:
        """Validate spinbox input against the spinbox's current limits."""
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

    def _change_color(
        self,
        variable: tk.Variable
    ) -> None:
        """Prompt for a color then apply it as a complete edit."""
        _, color = colorchooser.askcolor(
            color=variable.get(),
            parent=self._frame.winfo_toplevel() #disables interaction with the designer while the dialog is shown
        )

        if color is None:
            return

        self._apply_complete_edit(variable, color)

    def _create_display_name_label_for(
        self,
        attribute: str,
        row: int
    ) -> None:
        """Create a display name label for the given attribute at the specified grid row."""
        tk.Label(
            self._frame,
            text=_DISPLAY_NAME_BY_ATTRIBUTE[attribute],
            bg=ATTRIBUTES_PANEL_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR,
            pady=3
        ).grid(column=0, row=row, sticky="W")

    def _create_editor_widget_for(
        self,
        widget: BaseWidget,
        attribute: str,
        row: int
    ) -> None:
        """Create the configured editor widget for the given attribute at the specified grid row."""
        editor_type = _EDITOR_WIDGET_TYPE_BY_ATTRIBUTE[attribute]
        getattr(self, f"_create_{editor_type}")(widget, attribute, row)

    def _create_label(
        self,
        widget: BaseWidget,
        attribute: str,
        row: int
    ) -> None:
        """Create a static text label for read only attributes."""
        tk.Label(
            self._frame,
            text=getattr(widget, attribute),
            bg=ATTRIBUTES_PANEL_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(
        self,
        widget: BaseWidget,
        attribute: str,
        row: int
    ) -> None:
        """Create a text entry for string attributes."""
        variable = tk.StringVar(value=str(getattr(widget, attribute)))
        entry = tk.Entry(
            self._frame,
            bg=ATTRIBUTES_PANEL_WIDGET_COLOR,
            fg=ATTRIBUTES_PANEL_TEXT_COLOR,
            width=18,
            textvariable=variable
        )
        entry.grid(column=1, row=row)
        entry.bind("<FocusOut>", lambda _event: self._end_attribute_edit())

        self._bind_variable(attribute, variable)

    def _create_spinbox(
        self,
        widget: BaseWidget,
        attribute: str,
        row: int
    ) -> None:
        """Create a spinbox with range validation for numeric attributes."""
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
        spinbox.bind("<FocusOut>", lambda _event: self._end_attribute_edit())
        spinbox.bind("<Leave>", lambda _event: self._end_attribute_edit())  #arrow button clicks do not trigger focus events

        self._spinboxes[attribute] = spinbox    #allows the spinbox's limits to be adjusted when size or anchor change
        self._bind_variable(attribute, variable)

    def _create_colorpicker(
        self,
        widget: BaseWidget,
        attribute: str,
        row: int
    ) -> None:
        """Create a button with color preview for color attributes."""
        color = str(getattr(widget, attribute))
        variable = tk.StringVar(value=color)
        colorpicker = tk.Button(
            self._frame,
            bg=color,
            relief="raised",
            width=3,
            command=lambda: self._change_color(variable)
        )
        colorpicker.grid(column=1, row=row, pady=2, sticky="W")

        self._colorpickers[attribute] = colorpicker #allows the colorpicker preview to be updated
        self._bind_variable(attribute, variable)

    def _create_combobox(
        self,
        widget: BaseWidget,
        attribute: str,
        row: int
    ) -> None:
        """Create a menu based combobox for enumerated attributes."""
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

            for anchor in ("n", "ne", "e", "se", "s", "sw", "w", "nw", "center"):   #tuple preserves the declared order
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

    def _bind_variable(
        self,
        attribute: str,
        variable: tk.Variable
    ) -> None:
        """Store a Tk variable for later updates from the widget and bind writes to propagate displayed value changes to the widget."""
        self._variables[attribute] = variable
        variable.trace_add("write", lambda _name, _index, _mode: self._handle_attribute_edit(attribute, variable))

    def _start_attribute_edit(
        self
    ) -> None:
        """Start an edit if one is not already in progress."""
        if self._edit_in_progress:
            return

        self._edit_in_progress = True
        self._on_edit_start()

    def _handle_attribute_edit(
        self,
        attribute: str,
        variable: tk.Variable
    ) -> None:
        """Propagate live changes to the widget."""
        if self._silent_mode:   #prevents propagating variable writes back to the widget when refreshing the panel from the widget
            return

        self._start_attribute_edit()

        value = variable.get()

        if attribute in {"x", "y", "width", "height"}:
            try:
                value = int(value)
            except ValueError:
                return

        self._on_edit_change(attribute, value)

    def _end_attribute_edit(
        self
    ) -> None:
        """Commit the active attribute edit if one is in progress."""
        if not self._edit_in_progress:
            return

        self._edit_in_progress = False
        self._on_edit_commit()

    def _apply_complete_edit(
        self,
        variable: tk.Variable,
        value: str
    ) -> None:
        """Apply a value using the complete edit lifecycle."""
        if value == variable.get():
            return

        self._start_attribute_edit()
        variable.set(value)
        self._end_attribute_edit()
