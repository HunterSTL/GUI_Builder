import tkinter as tk

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
        callbacks: dict,
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
        self.callbacks = callbacks
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
        project_callbacks = self.callbacks["project"]
        file_menu.add_command(
            label="New",
            command=project_callbacks["new"],
            accelerator="[CTRL] + [N]"
        )
        file_menu.add_command(
            label="Open",
            command=project_callbacks["open"],
            accelerator="[CTRL] + [O]"
        )
        file_menu.add_command(
            label="Save",
            command=project_callbacks["save"],
            accelerator="[CTRL] + [S]"
        )
        file_menu.add_command(
            label="Save as",
            command=project_callbacks["save_as"],
            accelerator="[CTRL] + [SHIFT] + [S]"
        )
        file_menu.add_command(
            label="Export JSON",
            command=project_callbacks["export_json"],
            accelerator="[CTRL] + [E]"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=project_callbacks["exit_app"],
            accelerator="[ALT] + [F4]"
        )

    def _add_edit_menu(self):
        """add the edit menu to the toolbar"""
        edit_menu_button = tk.Menubutton(self.toolbar, text="Edit", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        edit_menu = tk.Menu(edit_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        edit_menu_button.config(menu=edit_menu)
        edit_menu_button.pack(side="left")

        #edit events
        edit_callbacks = self.callbacks["edit"]
        edit_menu.add_command(
            label="Cut",
            command=edit_callbacks["cut"],
            accelerator="[CTRL] + [X]"
        )
        edit_menu.add_command(
            label="Copy",
            command=edit_callbacks["copy"],
            accelerator="[CTRL] + [C]"
        )
        edit_menu.add_command(
            label="Paste",
            command=edit_callbacks["paste"],
            accelerator="[CTRL] + [V]"
        )
        edit_menu.add_command(
            label="Undo",
            command=edit_callbacks["undo"],
            accelerator="[CTRL] + [Z]"
        )
        edit_menu.add_command(
            label="Redo",
            command=edit_callbacks["redo"],
            accelerator="[CTRL] + [Y]"
        )
        edit_menu.add_command(
            label="Select all",
            command=self.callbacks["selection"]["select_all"],
            accelerator="[CTRL] + [A]"
        )

    def _add_widget_menu(self):
        """add the widget menu to the toolbar"""
        widget_menu_button = tk.Menubutton(self.toolbar, text="Widgets", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        widget_menu = tk.Menu(widget_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        widget_menu_button.config(menu=widget_menu)
        widget_menu_button.pack(side="left")

        #widget events
        widget_callbacks = self.callbacks["widget"]
        widget_menu.add_command(
            label="Delete",
            command=widget_callbacks["delete"],
            accelerator="[Del]"
        )
        widget_menu.add_command(
            label="Snap to grid",
            command=widget_callbacks["snap_to_grid"],
            accelerator="[S]"
        )
        widget_menu.add_command(
            label="Align left",
            command=widget_callbacks["align_left"],
            accelerator="[CTRL] + [←]"
        )
        widget_menu.add_command(
            label="Align right",
            command=widget_callbacks["align_right"],
            accelerator="[CTRL] + [→]"
        )
        widget_menu.add_command(
            label="Align top",
            command=widget_callbacks["align_top"],
            accelerator="[CTRL] + [↑]"
        )
        widget_menu.add_command(
            label="Align bottom",
            command=widget_callbacks["align_bottom"],
            accelerator="[CTRL] + [↓]"
        )

    def _add_grid_menu(self):
        """add the grid menu to the toolbar"""
        grid_menu_button = tk.Menubutton(self.toolbar, text="Grid", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        grid_menu = tk.Menu(grid_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        grid_menu_button.config(menu=grid_menu)
        grid_menu_button.pack(side="left")

        #grid events
        grid_callbacks = self.callbacks["grid"]
        grid_menu.add_checkbutton(
            label="Visualize grid",
            variable=self.grid_visible_variable,
            command=grid_callbacks["apply_from_variable"],
            accelerator="[G]"
        )
        grid_menu.add_command(
            label="Change grid size",
            command=grid_callbacks["change_size"],
            accelerator="[CTRL] + [G]"
        )
        grid_menu.add_command(
            label="Change grid color",
            command=grid_callbacks["change_color"],
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
            command=self.callbacks["toggle_call_tracing"],
            accelerator="[CTRL] + [SHIFT] + [T]"
        )
        debug_menu.add_command(
            label="Set dirty",
            command=self.callbacks["set_dirty"],
            accelerator="[CTRL] + [D]"
        )
        debug_menu.add_command(
            label="Set clean",
            command=self.callbacks["set_clean"],
            accelerator="[CTRL] + [SHIFT] + [D]"
        )