import tkinter as tk

class ToolbarManager:
    def __init__(self, parent: tk.Tk, theme: dict, callbacks: dict):
        """
        parent:     parent window (Designer.top)
        theme:      dictionary with colors for toolbar
        callbacks:  dictionary of functions (snap_to_grid, toggle_grid etc.)
        """
        self.parent = parent
        self.theme = theme
        self.callbacks = callbacks
        self.toolbar = None

    def create_toolbar(self):
        self.toolbar = tk.Frame(self.parent, bg=self.theme.get("toolbar_color"))
        self.toolbar.pack(side="top", fill="x")
        self._add_widget_menu()
        self._add_grid_menu()

    def _add_widget_menu(self):
        widget_menu_button = tk.Menubutton(self.toolbar, text="Widgets", bg=self.theme.get("button_color"), fg=self.theme.get("text_color"), relief="raised", width=10)
        widget_menu = tk.Menu(widget_menu_button, bg=self.theme.get("menu_color"), fg=self.theme.get("text_color"), tearoff=0)
        widget_menu_button.config(menu=widget_menu)
        widget_menu_button.pack(side="left")

        #use callbacks for actions
        widget_menu.add_command(label="Snap to grid", command=self.callbacks["snap_to_grid"])
        widget_menu.add_command(label="Align left", command=self.callbacks["align_left"])
        widget_menu.add_command(label="Align top", command=self.callbacks["align_top"])

    def _add_grid_menu(self):
        grid_menu_button = tk.Menubutton(self.toolbar, text="Grid", bg=self.theme.get("button_color"), fg=self.theme.get("text_color"), relief="raised", width=10)
        grid_menu = tk.Menu(grid_menu_button, bg=self.theme.get("menu_color"), fg=self.theme.get("text_color"), tearoff=0)
        grid_menu_button.config(menu=grid_menu)
        grid_menu_button.pack(side="left")
        grid_menu.add_checkbutton(label="Visualize grid", command=self.callbacks["toggle_grid"])