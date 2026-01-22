import tkinter as tk
from CanvasManager import CanvasManager
from SelectionManager import SelectionManager
from ToolbarManager import ToolbarManager
from WidgetManager import WidgetManager
from AttributesPanelManager import AttributesPanelManager
from ProjectDocument import ProjectDocument
from PIL import ImageTk

class Designer:
    def __init__(
            self,
            parent: tk.Tk,
            project_document: ProjectDocument,
            icon: ImageTk.PhotoImage,
            program_theme: dict,
            constants: dict,
            project_callbacks: dict
        ):
        self.parent = parent
        self.project_document = project_document
        self.icon = icon
        self.program_theme = program_theme
        self.constants = constants
        self.project_callbacks = project_callbacks

        #shared mutable callbacks dictionary
        self.callbacks = {}

        #last right-click position for insertion
        self._click_x = None
        self._click_y = None

        #drag state for moving the designer window
        self._drag_start_x = None
        self._drag_start_y = None
        self._win_x = None
        self._win_y = None

        #app state
        self._dirty = False

        #create window
        self.top = tk.Toplevel(parent)
        titlebar_height = self.constants["titlebar_height"]
        toolbar_height = self.constants["toolbar_height"]
        self.top.geometry(f"{self.project_document.width}x{(self.project_document.height + titlebar_height + toolbar_height)}")

        #create title bar
        self.title_label = None
        self._create_title_bar()

        #create main frame that will host canvas frame and attributes panel frame
        self.main_frame = tk.Frame(self.top, bg=self.project_document.theme["background"]["color"])

        #create canvas frame
        self.canvas_frame = tk.Frame(self.main_frame, width=self.project_document.width, height=self.project_document.height, bg=self.project_document.theme["background"]["color"])
        self.canvas_frame.pack(side="left", anchor="nw")
        self.canvas_frame.pack_propagate(False) #keep fixed size

        #create attributes panel frame
        self.attributes_panel_frame = tk.Frame(self.main_frame, width=self.constants["attributes_panel"]["width"], bg=self.program_theme["attributes_panel"]["color"])
        self.attributes_panel_frame.pack_propagate(False)
        self.attributes_panel_frame.grid_propagate(False)

        #create instance of CanvasManager
        self.canvas_manager = CanvasManager(
            parent=self.canvas_frame,
            project_document=self.project_document,
            nudge_small=self.constants["nudge"]["small"],
            nudge_big=self.constants["nudge"]["big"],
            callbacks=self.callbacks
        )

        self.canvas = self.canvas_manager.create_canvas()

        #create instance of SelectionManager to store selected widgets
        self.selection_manager = SelectionManager(
            canvas=self.canvas,
            ctrl_key=self.constants["ctrl_key"],
            selection_width=self.constants["selection"]["width"],
            selection_dash=self.constants["selection"]["dash"],
            selection_padding=self.constants["selection"]["padding"],
            selection_color=self.program_theme["selection"]["color"],
            last_selected_color=self.program_theme["selection"]["last_selected_color"]
        )

        #create instance of WidgetManager to store created widgets
        self.widget_manager = WidgetManager(
            top=self.top,
            canvas=self.canvas,
            project_document=self.project_document,
            selection_manager=self.selection_manager,
            callbacks=self.callbacks,
            panel_update=lambda widget_model: self.attributes_panel_manager.update_variable_from_model(widget_model, ["x", "y"])
        )

        #create instance of AttributesPanelManager to show/hide the attribute panel for a selected widget
        self.attributes_panel_manager = AttributesPanelManager(
            root=self.top,
            frame=self.attributes_panel_frame,
            canvas_width=self.project_document.width,
            canvas_height=self.project_document.height,
            window_height=self.project_document.height + self.constants["titlebar_height"] + self.constants["toolbar_height"],
            panel_width=self.constants["attributes_panel"]["width"],
            panel_height=self.constants["attributes_panel"]["height"],
            panel_color=self.program_theme["attributes_panel"]["color"],
            widget_color=self.program_theme["attributes_panel"]["widget_color"],
            text_color=self.program_theme["attributes_panel"]["text_color"],
            selection_manager=self.selection_manager,
            widget_manager=self.widget_manager,
            callbacks=self.callbacks
        )

        #create instance of ToolbarManager to store theme and function callbacks
        self.toolbar_manager = ToolbarManager(
            parent=self.top,
            height=self.constants["toolbar_height"],
            toolbar_color=self.program_theme["toolbar"]["bg"],
            button_color=self.program_theme["button"]["bg"],
            button_text_color=self.program_theme["button"]["fg"],
            menu_color=self.program_theme["menu"]["bg"],
            menu_text_color=self.program_theme["menu"]["fg"],
            callbacks=self.callbacks
        )

        #create shared callback dictionary
        self.callbacks.update({
            "show_menu": self._show_menu,
            "selection": {
                "press": self.selection_manager.handle_canvas_press,
                "drag": self.selection_manager.handle_canvas_drag,
                "release": lambda e: self.selection_manager.handle_canvas_release(e, self._on_selection_changed)
            },
            "project": self.project_callbacks,
            "widget": {
                "move": self.widget_manager.move_selected_widgets,
                "snap_to_grid": self.widget_manager.snap_to_grid,
                "delete": self.widget_manager.delete_selected_widgets,
                "align_left": lambda: self.widget_manager.align("left"),
                "align_right": lambda: self.widget_manager.align("right"),
                "align_top": lambda: self.widget_manager.align("top"),
                "align_bottom": lambda: self.widget_manager.align("bottom")
            },
            "grid": {
                "toggle": self.canvas_manager.toggle_grid,
                "change_size": self.canvas_manager.change_grid_size,
                "change_color": self.canvas_manager.change_grid_color
            },
            "clamped_delta": {
                "group": self._group_clamped_delta,
                "single": self._clamped_delta
            },
            "attributes_panel": self._on_selection_changed,
            "set_dirty": self.set_dirty,
            "set_clean": self.set_clean
        })

        #toggle grid if grid is set to visible in project_document
        if self.project_document.grid.visible:
            self.canvas_manager.draw_grid()

        #create toolbar
        self.toolbar_manager.create_toolbar()

        #pack content frame after creating toolbar so the toolbar is on top
        self.main_frame.pack(side="top", fill="both", expand=True)

        #pack canvas after creating toolbar so the toolbar is on top
        self.canvas_manager.pack_canvas()

        #create context menu for creating new widgets
        self._add_widget_menu()

        #bind events to keybinds
        self.canvas_manager.bind_events()

        #create widgets for the models from the project_document
        for model in self.project_document.widget_models:
            self.widget_manager.add_widget_from_model(model)

    def is_dirty(self):
        return self._dirty

    def set_dirty(self):
        self._dirty = True
        self.title_label.configure(text=self.project_document.title + "*")
        self.title_label.update()

    def set_clean(self):
        self._dirty = False
        self.title_label.configure(text=self.project_document.title)
        self.title_label.update()

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
        title_bar = tk.Frame(
            self.top,
            height=self.constants["titlebar_height"],
            bg=self.program_theme["titlebar"]["bg"]
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        #add icon
        icon_label = tk.Label(
            title_bar,
            image=self.icon,
            bg=self.program_theme["titlebar"]["bg"]
        )
        icon_label.pack(side="left", padx=2, pady=2)
        icon_label.bind("<Button-1>", start_move)
        icon_label.bind("<B1-Motion>", do_move)

        #add title
        self.title_label = tk.Label(
            title_bar,
            text=self.project_document.title,
            bg=self.program_theme["titlebar"]["bg"],
            fg=self.program_theme["titlebar"]["fg"]
        )
        self.title_label.pack(side="left")
        self.title_label.bind("<Button-1>", start_move)
        self.title_label.bind("<B1-Motion>", do_move)

        #add close button
        close_button = tk.Button(
            title_bar,
            text=" X ",
            bg=self.program_theme["titlebar"]["bg"],
            fg=self.program_theme["titlebar"]["fg"],
            relief="flat",
            command=self.project_callbacks["exit_app"]
        )
        close_button.pack(side="right")

    #create add widget menu
    def _add_widget_menu(self):
        self.menu = tk.Menu(
            self.top,
            bg=self.program_theme["toolbar"]["bg"],
            fg=self.program_theme["toolbar"]["fg"],
            tearoff=0
        )

        def _pos():
            x = self._click_x if self._click_x is not None else 20
            y = self._click_y if self._click_y is not None else 20
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
        self._click_x, self._click_y = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

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

    #compute clamped delta, so that widget cannot be moved outside the GUI window
    def _clamped_delta(self, item_id, dx: int, dy: int) -> tuple[int, int]:
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx_clamped, dy_clamped = dx, dy

        bbox = self.canvas.bbox(item_id)
        if not bbox:
            return 0, 0
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