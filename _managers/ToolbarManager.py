import tkinter as tk
from EventBus import EventBus

class ToolbarManager:
    def __init__(
        self,
        parent: tk.Toplevel,
        height: int,
        toolbar_color: str,
        button_color: str,
        button_text_color: str,
        menu_color: str,
        menu_text_color: str,
        event_bus: EventBus,
        grid_visible_variable: tk.BooleanVar
    ):
        """initialize the toolbar manager and its configuration"""
        self.parent = parent
        self.height = height
        self.toolbar_color = toolbar_color
        self.button_color = button_color
        self.button_text_color = button_text_color
        self.menu_color = menu_color
        self.menu_text_color = menu_text_color
        self.event_bus = event_bus
        self.grid_visible_variable = grid_visible_variable

        self.toolbar = None

    def create_toolbar(self):
        """construct and display the complete toolbar"""
        self.toolbar = tk.Frame(self.parent, height=self.height, bg=self.toolbar_color)
        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)
        self._add_file_menu()
        self._add_edit_menu()
        self._add_widget_menu()
        self._add_grid_menu()
        self._add_debug_menu()

    def _add_file_menu(self):
        """add the file menu to the toolbar"""
        file_menu_button = tk.Menubutton(self.toolbar, text="File", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        file_menu = tk.Menu(file_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        file_menu_button.config(menu=file_menu)
        file_menu_button.pack(side="left")

        #project events
        file_menu.add_command(
            label="New",
            command=lambda: self.event_bus.emit("project.new"),
            accelerator="[CTRL] + [N]"
        )
        file_menu.add_command(
            label="Open",
            command=lambda: self.event_bus.emit("project.open"),
            accelerator="[CTRL] + [O]"
        )
        file_menu.add_command(
            label="Save",
            command=lambda: self.event_bus.emit("project.save"),
            accelerator="[CTRL] + [S]"
        )
        file_menu.add_command(
            label="Save as",
            command=lambda: self.event_bus.emit("project.save_as"),
            accelerator="[CTRL] + [SHIFT] + [S]"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=lambda: self.event_bus.emit("app.exit"),
            accelerator="[ALT] + [F4]"
        )

    def _add_edit_menu(self):
        """add the edit menu to the toolbar"""
        edit_menu_button = tk.Menubutton(self.toolbar, text="Edit", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        edit_menu = tk.Menu(edit_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        edit_menu_button.config(menu=edit_menu)
        edit_menu_button.pack(side="left")

        #edit events
        edit_menu.add_command(
            label="Cut",
            command=lambda: self.event_bus.emit("edit.cut"),
            accelerator="[CTRL] + [X]"
        )
        edit_menu.add_command(
            label="Copy",
            command=lambda: self.event_bus.emit("edit.copy"),
            accelerator="[CTRL] + [C]"
        )
        edit_menu.add_command(
            label="Paste",
            command=lambda: self.event_bus.emit("edit.paste"),
            accelerator="[CTRL] + [V]"
        )
        edit_menu.add_command(
            label="Undo",
            command=lambda: self.event_bus.emit("edit.undo"),
            accelerator="[CTRL] + [Z]"
        )
        edit_menu.add_command(
            label="Redo",
            command=lambda: self.event_bus.emit("edit.redo"),
            accelerator="[CTRL] + [Y]"
        )

    def _add_widget_menu(self):
        """add the widget menu to the toolbar"""
        widget_menu_button = tk.Menubutton(self.toolbar, text="Widgets", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        widget_menu = tk.Menu(widget_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        widget_menu_button.config(menu=widget_menu)
        widget_menu_button.pack(side="left")

        #widget events
        widget_menu.add_command(
            label="Delete",
            command=lambda: self.event_bus.emit("widget.delete"),
            accelerator="[Del]"
        )
        widget_menu.add_command(
            label="Snap to grid",
            command=lambda: self.event_bus.emit("widget.snap_to_grid"),
            accelerator="[S]"
        )
        widget_menu.add_command(
            label="Align left",
            command=lambda: self.event_bus.emit("widget.align.left"),
            accelerator="[CTRL] + [←]"
        )
        widget_menu.add_command(
            label="Align right",
            command=lambda: self.event_bus.emit("widget.align.right"),
            accelerator="[CTRL] + [→]"
        )
        widget_menu.add_command(
            label="Align top",
            command=lambda: self.event_bus.emit("widget.align.top"),
            accelerator="[CTRL] + [↑]"
        )
        widget_menu.add_command(
            label="Align bottom",
            command=lambda: self.event_bus.emit("widget.align.bottom"),
            accelerator="[CTRL] + [↓]"
        )
        widget_menu.add_command(
            label="Select all",
            command=lambda: self.event_bus.emit("widget.select_all"),
            accelerator="[CTRL] + [A]"
        )

    def _add_grid_menu(self):
        """add the grid menu to the toolbar"""
        grid_menu_button = tk.Menubutton(self.toolbar, text="Grid", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        grid_menu = tk.Menu(grid_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        grid_menu_button.config(menu=grid_menu)
        grid_menu_button.pack(side="left")

        #grid events
        grid_menu.add_checkbutton(
            label="Visualize grid",
            variable=self.grid_visible_variable,
            command=lambda: self.event_bus.emit("grid.apply_variable"),
            accelerator="[G]"
        )
        grid_menu.add_command(
            label="Change grid size",
            command=lambda: self.event_bus.emit("grid.change_size"),
            accelerator="[CTRL] + [G]"
        )
        grid_menu.add_command(
            label="Change grid color",
            command=lambda: self.event_bus.emit("grid.change_color"),
            accelerator="[SHIFT] + [G]"
        )

    def _add_debug_menu(self):
        """add the debug menu to the toolbar"""
        debug_menu_button = tk.Menubutton(self.toolbar, text="Debug", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        debug_menu = tk.Menu(debug_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        debug_menu_button.config(menu=debug_menu)
        debug_menu_button.pack(side="left")

        #debug events
        debug_menu.add_checkbutton(
            label="Call tracing",
            command=lambda: self.event_bus.emit("debug.toggle_call_tracing"),
            accelerator="[CTRL] + [SHIFT] + [T]"
        )
        debug_menu.add_command(
            label="Set dirty",
            command=lambda: self.event_bus.emit("debug.set_dirty"),
            accelerator="[CTRL] + [D]"
        )
        debug_menu.add_command(
            label="Set clean",
            command=lambda: self.event_bus.emit("debug.set_clean"),
            accelerator="[CTRL] + [SHIFT] + [D]"
        )
        debug_menu.add_command(
            label="Print widget count",
            command=lambda: self.event_bus.emit("debug.print_widget_count"),
            accelerator="[#]"
        )