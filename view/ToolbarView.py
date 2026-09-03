import tkinter as tk

from utility.AppTheme import TOOLBAR_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, MENU_COLOR, MENU_TEXT_COLOR
from utility.Constants import TOOLBAR_HEIGHT

class ToolbarView:
    """
    Tk-only view that builds the toolbar and provides an API
    for adding menus, menu items, checkbox menu items and separators.
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        parent: tk.Toplevel,
        grid_visible_variable
    ):
        """store parent and theme"""
        self.parent = parent
        self.grid_visible_variable = grid_visible_variable

        self.toolbar = None
        self._menus = {}    #menu_name: (menu_button, menu)

    def create_toolbar(self):
        """construct and pack the toolbar frame"""
        self.toolbar = tk.Frame(
            self.parent,
            height=TOOLBAR_HEIGHT,
            bg=TOOLBAR_COLOR
        )
        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)

    def add_menu(self, menu_name: str):
        """add a menu to the toolbar with the given name"""
        menu_button = tk.Menubutton(
            self.toolbar,
            text=menu_name,
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

    #Internals----------------------------------------------------------------------------------------------------------
    def _get_menu(self, menu_name):
        return self._menus[menu_name][1]