import tkinter as tk

class ToolbarView:
    """
    Tk-only view that builds the toolbar frame and provides an API
    for adding menus, menu items, checkbox menu items and separators.
    """
    def __init__(
        self,
        parent: tk.Toplevel,
        height: int,
        toolbar_color: str,
        button_color: str,
        button_text_color: str,
        menu_color: str,
        menu_text_color: str,
        grid_visible_variable
    ):
        """store parent and theme"""
        self.parent = parent
        self.height = height
        self.toolbar_color = toolbar_color
        self.button_color = button_color
        self.button_text_color = button_text_color
        self.menu_color = menu_color
        self.menu_text_color = menu_text_color
        self.grid_visible_variable = grid_visible_variable

        self.toolbar = None
        self._menus = {}    #menu_name: (menu_button, menu)

    #Internals----------------------------------------------------------------------------------------------------------
    def _get_menu(self, menu_name):
        return self._menus[menu_name][1]

    #Construction API---------------------------------------------------------------------------------------------------
    def create_toolbar(self):
        """construct and pack the toolbar frame"""
        self.toolbar = tk.Frame(
            self.parent,
            height=self.height,
            bg=self.toolbar_color
        )
        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)

    def add_menu(self, menu_name: str):
        """add a menu to the toolbar with the given name"""
        menu_button = tk.Menubutton(
            self.toolbar,
            text=menu_name,
            bg=self.button_color,
            fg=self.button_text_color,
            relief="raised",
            width=10
        )
        menu = tk.Menu(
            menu_button,
            bg=self.menu_color,
            fg=self.menu_text_color,
            tearoff=0
        )
        menu_button.config(menu=menu)
        menu_button.pack(side="left")

        self._menus[menu_name] = menu_button, menu

    def add_menu_item(self, menu_name: str, label: str, command, accelerator: str = ""):
        menu = self._get_menu(menu_name)
        menu.add_command(
            label=label,
            command=command,
            accelerator=accelerator
        )

    def add_checkbox_menu_item(self, menu_name: str, label: str, command, accelerator: str = "", variable = None):
        menu = self._get_menu(menu_name)
        menu.add_checkbutton(
            label=label,
            command=command,
            accelerator=accelerator,
            variable=variable
        )

    def add_separator(self, menu_name: str):
        menu = self._get_menu(menu_name)
        menu.add_separator()