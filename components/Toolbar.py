import tkinter as tk

from events import EventRouter
from utility import Edge
from utility.AppTheme import TOOLBAR_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, MENU_COLOR, MENU_TEXT_COLOR
from utility.Constants import TOOLBAR_HEIGHT


class Toolbar:
    """Provides toolbar controls that emit events."""
    def __init__(
        self,
        parent: tk.Toplevel,
        event_router: EventRouter,
        grid_visible: bool,
        call_tracing_enabled: bool
    ) -> None:
        self._event_router: EventRouter = event_router

        self._grid_visible_variable: tk.BooleanVar = tk.BooleanVar(
            master=parent,
            value=grid_visible
        )
        self._call_tracing_enabled_variable: tk.BooleanVar = tk.BooleanVar(
            master=parent,
            value=call_tracing_enabled
        )

        self._frame: tk.Frame = tk.Frame(
            parent,
            height=TOOLBAR_HEIGHT,
            bg=TOOLBAR_COLOR
        )
        self._frame.pack_propagate(False)

        self._add_file_menu()
        self._add_edit_menu()
        self._add_widgets_menu()
        self._add_grid_menu()
        self._add_debug_menu()

    @property
    def frame(
        self
    ) -> tk.Frame:
        """Return the toolbar frame."""
        return self._frame

    def set_grid_visibility_checkmark(
        self,
        visible: bool
    ) -> None:
        """Update the checkmark that represents grid visibility."""
        self._grid_visible_variable.set(visible)

    def set_call_tracing_checkmark(
        self,
        enabled: bool
    ) -> None:
        """Update the checkmark that represents call tracing state."""
        self._call_tracing_enabled_variable.set(enabled)

    def _add_file_menu(
        self
    ) -> None:
        menu = self._add_menu("File")
        menu.add_command(
            label="New",
            command=lambda: self._event_router.emit("project.new"),
            accelerator="[CTRL] + [N]"
        )
        menu.add_command(
            label="Open",
            command=lambda: self._event_router.emit("project.open"),
            accelerator="[CTRL] + [O]"
        )
        menu.add_command(
            label="Save",
            command=lambda: self._event_router.emit("project.save"),
            accelerator="[CTRL] + [S]"
        )
        menu.add_command(
            label="Save as",
            command=lambda: self._event_router.emit("project.save_as"),
            accelerator="[CTRL] + [SHIFT] + [S]"
        )
        menu.add_separator()
        menu.add_command(
            label="Exit",
            command=lambda: self._event_router.emit("app.exit"),
            accelerator="[ALT] + [F4]"
        )

    def _add_edit_menu(
        self
    ) -> None:
        menu = self._add_menu("Edit")
        menu.add_command(
            label="Delete",
            command=lambda: self._event_router.emit("edit.delete"),
            accelerator="[Del]"
        )
        menu.add_command(
            label="Copy",
            command=lambda: self._event_router.emit("edit.copy"),
            accelerator="[CTRL] + [C]"
        )
        menu.add_command(
            label="Paste",
            command=lambda: self._event_router.emit("edit.paste"),
            accelerator="[CTRL] + [V]"
        )
        menu.add_command(
            label="Cut",
            command=lambda: self._event_router.emit("edit.cut"),
            accelerator="[CTRL] + [X]"
        )
        menu.add_command(
            label="Undo",
            command=lambda: self._event_router.emit("edit.undo"),
            accelerator="[CTRL] + [Z]"
        )
        menu.add_command(
            label="Redo",
            command=lambda: self._event_router.emit("edit.redo"),
            accelerator="[CTRL] + [Y]"
        )

    def _add_widgets_menu(
        self
    ) -> None:
        menu = self._add_menu("Widgets")
        menu.add_command(
            label="Snap to grid",
            command=lambda: self._event_router.emit("widget.snap_to_grid"),
            accelerator="[S]"
        )
        menu.add_command(
            label="Align left",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.LEFT),
            accelerator="[CTRL] + [←]"
        )
        menu.add_command(
            label="Align right",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.RIGHT),
            accelerator="[CTRL] + [→]"
        )
        menu.add_command(
            label="Align top",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.TOP),
            accelerator="[CTRL] + [↑]"
        )
        menu.add_command(
            label="Align bottom",
            command=lambda: self._event_router.emit("widget.align", edge=Edge.BOTTOM),
            accelerator="[CTRL] + [↓]"
        )
        menu.add_command(
            label="Select all",
            command=lambda: self._event_router.emit("widget.select_all"),
            accelerator="[CTRL] + [A]"
        )

    def _add_grid_menu(
        self
    ) -> None:
        menu = self._add_menu("Grid")
        menu.add_checkbutton(
            label="Show grid",
            command=lambda: self._event_router.emit("grid.toggle"),
            accelerator="[G]",
            variable=self._grid_visible_variable
        )
        menu.add_command(
            label="Change grid size",
            command=lambda: self._event_router.emit("grid.change_size"),
            accelerator="[CTRL] + [G]"
        )
        menu.add_command(
            label="Change grid color",
            command=lambda: self._event_router.emit("grid.change_color"),
            accelerator="[SHIFT] + [G]"
        )

    def _add_debug_menu(
        self
    ) -> None:
        menu = self._add_menu("Debug")
        menu.add_checkbutton(
            label="Call tracing",
            command=lambda: self._event_router.emit("debug.toggle_call_tracing"),
            accelerator="[CTRL] + [SHIFT] + [T]",
            variable=self._call_tracing_enabled_variable
        )
        menu.add_command(
            label="Print widget count",
            command=lambda: self._event_router.emit("debug.print_widget_count"),
            accelerator="[#]"
        )
        menu.add_command(
            label="Print clipboard",
            command=lambda: self._event_router.emit("debug.print_clipboard"),
            accelerator="[F1]"
        )
        menu.add_command(
            label="Print command stack",
            command=lambda: self._event_router.emit("debug.print_command_stack"),
            accelerator="[F2]"
        )
        menu.add_command(
            label="Print selection",
            command=lambda: self._event_router.emit("debug.print_selection"),
            accelerator="[F3]"
        )
        menu.add_command(
            label="Print bounding boxes",
            command=lambda: self._event_router.emit("debug.print_bounding_boxes"),
            accelerator="[F4]"
        )
        menu.add_command(
            label="Print ID counters",
            command=lambda: self._event_router.emit("debug.print_id_counters"),
            accelerator="[F5]"
        )

    def _add_menu(
        self,
        name: str
    ) -> tk.Menu:
        """Add and return a named toolbar menu."""
        menu_button = tk.Menubutton(
            self._frame,
            text=name,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            relief="raised",
            width=10
        )
        menu = tk.Menu(
            menu_button,
            bg=MENU_COLOR,
            fg=MENU_TEXT_COLOR,
            tearoff=0
        )
        menu_button.config(menu=menu)
        menu_button.pack(side="left")
        return menu
