import tkinter as tk
from typing import Dict, Optional
from CanvasManager import CanvasManager
from SelectionManager import SelectionManager
from ToolbarManager import ToolbarManager
from WidgetManager import WidgetManager
from AttributesPanelManager import AttributesPanelManager
from DataModels import *
from Theme import *
from PIL import ImageTk

class Designer:
    def __init__(self, parent: tk.Tk, title: str, width: int, height: int, theme: dict, icon: ImageTk.PhotoImage):
        self.parent = parent
        self.width = width
        self.height = height
        self.theme = theme
        self.icon = icon
        self.grid_size = GRID_SIZE

        #last right-click position for insertion
        self.click_x: Optional[int] = None
        self.click_y: Optional[int] = None

        #drag state for moving the designer window
        self._drag_start_x = None
        self._drag_start_y = None
        self._win_x = None
        self._win_y = None

        #create instance of GUIWindow to store dimensions, title and color pallette
        self.gui_window = GUIWindow(title, self.width, self.height, self.theme["background"]["bg"])

        #create window
        self.top = tk.Toplevel(parent)
        self.top.geometry(f"{self.width}x{self.height}")

        #create title bar
        self._create_title_bar()

        #create main frame that will host canvas frame and attributes panel frame
        self.main_frame = tk.Frame(self.top, bg=self.theme["background"]["bg"])
        self.canvas_frame = tk.Frame(self.main_frame, bg=self.theme["background"]["bg"])
        self.canvas_frame.pack(side="left", fill="both", expand=True)
        self.canvas_frame.pack_propagate(False)
        self.attributes_panel_frame = tk.Frame(self.main_frame, width=ATTRIBUTES_PANEL_WIDTH, bg=ATTRIBUTES_PANEL_COLOR)
        self.attributes_panel_frame.pack_propagate(False)   #keep fixed width
        self.attributes_panel_frame.grid_propagate(False)

        #create instance of CanvasManager
        self.canvas_manager = CanvasManager(
            parent=self.canvas_frame,
            width=width,
            height=height,
            bg_color=self.theme["background"]["bg"],
            grid_size=GRID_SIZE,
            grid_color=GRID_COLOR
        )

        self.canvas = self.canvas_manager.create_canvas()

        #create instance of SelectionManager to store selected widgets
        self.selection_manager = SelectionManager(self.canvas)

        #create instance of WidgetManager to store created widgets
        self.widget_manager = WidgetManager(self.top, self.canvas, self.theme, self.selection_manager, self._on_selection_changed, self._group_clamped_delta)

        self.canvas_manager.bind_events(
            self._show_menu,
            {
                "press": self.selection_manager.handle_canvas_press,
                "drag": self.selection_manager.handle_canvas_drag,
                "release": lambda e: self.selection_manager.handle_canvas_release(e, self._on_selection_changed)
            },
            self._move_selection,
            self.widget_manager.delete_selected_widgets
        )

        #create instance of ToolbarManager to store theme and function callbacks
        self.toolbar_manger = ToolbarManager(
            parent=self.top,
            theme={
                "toolbar_color": TOOLBAR_COLOR,
                "button_color": BUTTON_COLOR,
                "text_color": TEXT_COLOR,
                "menu_color": MENU_COLOR
            },
            callbacks={
                "snap_to_grid": lambda: self.widget_manager.snap_to_grid(self.grid_size),
                "align_left": lambda: self.widget_manager.snap_to_grid(self.grid_size),   #currently place holder
                "align_top": lambda: self.widget_manager.snap_to_grid(self.grid_size),    #currently place holder
                "toggle_grid": self.canvas_manager.toggle_grid
            }
        )

        self.toolbar_manger.create_toolbar()

        #pack content frame after creating toolbar so the toolbar is on top
        self.main_frame.pack(side="top", fill="both", expand=True)

        #pack canvas after creating toolbar so the toolbar is on top
        self.canvas_manager.pack_canvas()

        #create instance of AttributesPanelManager to show/hide the attribute panel for a selected widget
        self.attributes_panel_manager = AttributesPanelManager(
            root=self.top,
            frame=self.attributes_panel_frame,
            theme={
                "background_color": ATTRIBUTES_PANEL_COLOR,
                "text_color": TEXT_COLOR
            },
            canvas_width=self.width,
            canvas_height=self.height,
            panel_width = ATTRIBUTES_PANEL_WIDTH,
            selection_manager=self.selection_manager,
            widget_manager=self.widget_manager
        )

        self._add_widget_menu()

    #create title bar
    def _create_title_bar(self):
        def start_move(event):
            self._drag_start_x = event.x_root
            self._drag_start_y = event.y_root
            self._win_x = self.top.winfo_x()
            self._win_y = self.top.winfo_y()

        def do_move(event):
            dx = event.x_root - self._drag_start_x
            dy = event.y_root - self._drag_start_y
            self.top.geometry(f"+{self._win_x + dx}+{self._win_y + dy}")

        #create custom title bar
        self.top.overrideredirect(True)
        title_bar = tk.Frame(self.top, bg=TITLE_BAR_COLOR)
        title_bar.pack(fill="x")
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        #add icon
        icon_label = tk.Label(title_bar, image=self.icon, bg=TITLE_BAR_COLOR)
        icon_label.pack(side="left", padx=2, pady=2)
        icon_label.bind("<Button-1>", start_move)
        icon_label.bind("<B1-Motion>", do_move)

        #add title
        title_label = tk.Label(title_bar, text=self.gui_window.title, bg=TITLE_BAR_COLOR, fg=TITLE_BAR_TEXT_COLOR)
        title_label.pack(side="left")
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<B1-Motion>", do_move)

        #add close button
        close_button = tk.Button(title_bar, text=" X ", bg=TITLE_BAR_COLOR, fg=TITLE_BAR_TEXT_COLOR, relief="flat", command=lambda: self.top.destroy())
        close_button.pack(side="right")

    #create add widget menu
    def _add_widget_menu(self):
        self.menu = tk.Menu(self.top, bg=TOOLBAR_COLOR, fg=TEXT_COLOR, tearoff=0)

        def _pos():
            x = self.click_x if self.click_x is not None else 20
            y = self.click_y if self.click_y is not None else 20
            return x, y

        self.menu.add_command(
            label="Add Label",
            command=lambda: self.widget_manager.add_widget("label", *_pos())
        )
        self.menu.add_command(
            label="Add Entry",
            command=lambda: self.widget_manager.add_widget("entry", *_pos())
        )
        self.menu.add_command(
            label="Add Button",
            command=lambda: self.widget_manager.add_widget("button", *_pos())
        )

    #post context menu
    def _show_menu(self, event):
        self.click_x, self.click_y = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #move selected widgets
    def _move_selection(self, dx, dy):
        if not self.selection_manager:
            return
        dx, dy = self._group_clamped_delta(dx, dy)
        for item_id in self.selection_manager.selected_ids():
            #move widget in canvas
            self.canvas.move(item_id, dx, dy)

            #update model data
            model = self.widget_manager.widget_map.get(item_id)["model"]
            if model:
                model.x += dx
                model.y += dy

            #update highlight
            self.selection_manager.refresh(item_id)

    #compute clamped delta, so that widget cannot be moved outside the GUI window
    def _group_clamped_delta(self, dx: int, dy: int) -> tuple[int, int]:
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx_clamped, dy_clamped = dx, dy

        for item_id in self.selection_manager.selected_ids():
            bbox = self.canvas.bbox(item_id)
            if not bbox:
                continue
            x0, y0, x1, y1 = bbox
            min_dx = -x0
            max_dx = canvas_width - x1
            min_dy = -y0
            max_dy = canvas_height - y1
            dx_clamped = max(min_dx, min(max_dx, dx_clamped))
            dy_clamped = max(min_dy, min(max_dy, dy_clamped))

        return dx_clamped, dy_clamped

    def _on_selection_changed(self):
        selected_ids = self.selection_manager.selected_ids()
        if len(selected_ids) == 1:
            item_id = next(iter(selected_ids))
            model = self.widget_manager.widget_map.get(item_id)["model"]
            self.attributes_panel_manager.show(model)
        else:
            self.attributes_panel_manager.hide()