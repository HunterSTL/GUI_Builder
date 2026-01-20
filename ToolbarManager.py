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
            callbacks: dict
        ):
        self.parent = parent
        self.height = height
        self.toolbar_color = toolbar_color
        self.button_color = button_color
        self.button_text_color = button_text_color
        self.menu_color = menu_color
        self.menu_text_color = menu_text_color
        self.callbacks = callbacks

        self.toolbar = None

    def create_toolbar(self):
        self.toolbar = tk.Frame(self.parent, height=self.height, bg=self.toolbar_color)
        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)
        self._add_file_menu()
        self._add_widget_menu()
        self._add_grid_menu()
        self._add_debug_menu()

    def _add_file_menu(self):
        export_menu_button = tk.Menubutton(self.toolbar, text="File", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        export_menu = tk.Menu(export_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        export_menu_button.config(menu=export_menu)
        export_menu_button.pack(side="left")

        export_menu.add_command(
            label="New",
            command=self.callbacks["new_project"],
            accelerator="[CTRL] + [N]"
        )
        export_menu.add_command(
            label="Open",
            command=self.callbacks["open_project"],
            accelerator="[CTRL] + [O]"
        )
        export_menu.add_command(
            label="Save",
            command=self.callbacks["save_project"],
            accelerator="[CTRL] + [S]"
        )
        export_menu.add_command(
            label="Save as",
            command=self.callbacks["save_project_as"],
            accelerator="[CTRL] + [SHIFT] + [S]"
        )
        export_menu.add_command(
            label="Export JSON",
            command=self.callbacks["export_json"],
            accelerator="[CTRL] + [E]"
        )
        export_menu.add_command(
            label="Exit",
            command=self.callbacks["exit"],
            accelerator="[ALT] + [F4]"
        )

    def _add_widget_menu(self):
        widget_menu_button = tk.Menubutton(self.toolbar, text="Widgets", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        widget_menu = tk.Menu(widget_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        widget_menu_button.config(menu=widget_menu)
        widget_menu_button.pack(side="left")

        #use callbacks for actions
        widget_menu.add_command(
            label="Delete",
            command=self.callbacks["delete"],
            accelerator="[Del]"
        )
        widget_menu.add_command(
            label="Snap to grid",
            command=self.callbacks["snap_to_grid"],
            accelerator="[S]"
        )
        widget_menu.add_command(
            label="Align left",
            command=self.callbacks["align_left"],
            accelerator="[CTRL] + [←]"
        )
        widget_menu.add_command(
            label="Align right",
            command=self.callbacks["align_right"],
            accelerator="[CTRL] + [→]"
        )
        widget_menu.add_command(
            label="Align top",
            command=self.callbacks["align_top"],
            accelerator="[CTRL] + [↑]"
        )
        widget_menu.add_command(
            label="Align bottom",
            command=self.callbacks["align_bottom"],
            accelerator="[CTRL] + [↓]"
        )

    def _add_grid_menu(self):
        grid_menu_button = tk.Menubutton(self.toolbar, text="Grid", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        grid_menu = tk.Menu(grid_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        grid_menu_button.config(menu=grid_menu)
        grid_menu_button.pack(side="left")

        grid_menu.add_checkbutton(
            label="Visualize grid",
            command=self.callbacks["toggle_grid"],
            accelerator="[G]"
        )
        grid_menu.add_command(
            label="Change grid size",
            command=self.callbacks["change_grid_size"],
            accelerator="[CTRL] + [G]"
        )
        grid_menu.add_command(
            label="Change grid color",
            command=self.callbacks["change_grid_color"],
            accelerator="[SHIFT] + [G]"
        )

    def _add_debug_menu(self):
        debug_menu_button = tk.Menubutton(self.toolbar, text="Debug", bg=self.button_color, fg=self.button_text_color, relief="raised", width=10)
        debug_menu = tk.Menu(debug_menu_button, bg=self.menu_color, fg=self.menu_text_color, tearoff=0)
        debug_menu_button.config(menu=debug_menu)
        debug_menu_button.pack(side="left")

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