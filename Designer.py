import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser
from DataModels import *
from ProjectDocument import ProjectDocument
from CanvasManager import CanvasManager
from SelectionManager import SelectionManager
from ToolbarManager import ToolbarManager
from WidgetManager import WidgetManager
from AttributesPanelManager import AttributesPanelManager
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
        self._deleting = False

        #variable to represent grid state from project_document
        self.grid_visible_variable = tk.BooleanVar(value=self.project_document.grid.visible)

        #build designer UI
        self._build_designer_ui()

        #create instance of CanvasManager
        self.canvas_manager = CanvasManager(
            parent=self.viewer,
            project_document=self.project_document,
            nudge_small=self.constants["nudge"]["small"],
            nudge_big=self.constants["nudge"]["big"],
            callbacks=self.callbacks
        )
        self.canvas = self.canvas_manager.canvas

        #embed inner canvas into viewer
        self.canvas_window_id = self.viewer.create_window(0, 0, window=self.canvas, anchor="nw")

        #draw boundry around the work area
        self._boundry = self.canvas.create_rectangle(
            1, 1, self.project_document.width - 1, self.project_document.height - 1,
            outline=self.program_theme["selection"]["color"],
            width=1,
            dash=(2, 2)
        )

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
            callbacks=self.callbacks
        )

        #create instance of AttributesPanelManager to show/hide the attribute panel for a selected widget
        self.attributes_panel_manager = AttributesPanelManager(
            root=self.top,
            frame=self.attributes_panel_frame,
            canvas_width=self.project_document.width,
            canvas_height=self.project_document.height,
            panel_color=self.program_theme["attributes_panel"]["color"],
            widget_color=self.program_theme["attributes_panel"]["widget_color"],
            text_color=self.program_theme["attributes_panel"]["text_color"],
            selection_manager=self.selection_manager,
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
            callbacks=self.callbacks,
            grid_visible_variable=self.grid_visible_variable
        )

        #create shared callback dictionary
        self.callbacks.update({
            "show_menu": self._show_menu,
            "selection": {
                "press": self.selection_manager.handle_canvas_press,
                "drag": self.selection_manager.handle_canvas_drag,
                "release": lambda e: self.selection_manager.handle_canvas_release(e, self._on_selection_changed),
                "select_all": self.selection_manager.select_all
            },
            "project": self.project_callbacks,
            "edit": {
                "cut": self._cut,
                "copy": self._copy,
                "paste": self._paste,
                "undo": self._undo,
                "redo": self._redo
            },
            "widget": {
                "move": self._move,
                "snap_to_grid": self._snap_to_grid,
                "delete": self._delete,
                "align_left": lambda: self._align("left"),
                "align_right": lambda: self._align("right"),
                "align_top": lambda: self._align("top"),
                "align_bottom": lambda: self._align("bottom")
            },
            "grid": {
                "toggle": self._toggle_grid,
                "apply_from_variable": self._apply_grid_from_variable,
                "change_size": self._change_grid_size,
                "change_color": self._change_grid_color
            },
            "attributes_panel": self._on_selection_changed,
            "attribute_changed": self._on_attribute_changed,
            "set_dirty": self._set_dirty,
            "set_clean": self._set_clean
        })

        #toggle grid if grid is set to visible in project_document
        if self.project_document.grid.visible:
            self.canvas_manager.refresh_grid()

        #create toolbar
        self.toolbar_manager.create_toolbar()

        #pack main frame after creating toolbar so toolbar is on top
        self.main_frame.pack(side="top", fill="both", expand=True)

        #create context menu for creating new widgets
        self._add_widget_menu()

        #bind events to keybinds
        self.canvas_manager.bind_events()

        #create widgets for the models from the project_document
        for model in self.project_document.widget_models:
            self.widget_manager.add_widget_from_model(model)

    def is_dirty(self):
        return self._dirty

    def set_clean(self):
        self._set_clean()

    def _add_widget(self, widget_type: str, x: int, y: int):
        if widget_type == "label":
            text = simpledialog.askstring("Label text", "Enter label text:", parent=self.top)
            if text is None:
                return
            bg = self.project_document.theme["label"]["bg"]
            fg = self.project_document.theme["label"]["fg"]
            widget = tk.Label(
                self.canvas,
                text=text,
                bg=bg,
                fg=fg
            )
            model = LabelWidgetData(x=x, y=y, bg=bg, fg=fg, text=text)
        elif widget_type == "entry":
            bg = self.project_document.theme["entry"]["bg"]
            fg = self.project_document.theme["entry"]["fg"]
            widget = tk.Entry(
                self.canvas,
                bg=bg,
                fg=fg
            )
            model = EntryWidgetData(x=x, y=y, bg=bg, fg=fg)
        elif widget_type == "button":
            text = simpledialog.askstring("Button text", "Enter button text:", parent=self.top)
            if text is None:
                return
            bg = self.project_document.theme["button"]["bg"]
            fg = self.project_document.theme["button"]["fg"]
            widget = tk.Button(
                self.canvas,
                text=text,
                bg=bg,
                fg=fg
            )
            model = ButtonWidgetData(x=x, y=y, bg=bg, fg=fg, text=text)
        else:
            return

        model.create_id()

        #calculate clamped x and y to prevent the widget from being created (partially) outside the canvas
        widget.update_idletasks()
        required_width, required_height = widget.winfo_reqwidth(), widget.winfo_reqheight()
        min_x, max_x = self._allowed_x_range(required_width, model.anchor)
        min_y, max_y = self._allowed_y_range(required_height, model.anchor)
        clamped_x = self._clamp(x, min_x, max_x)
        clamped_y = self._clamp(y, min_y, max_y)

        #delegate actual widget creation to WidgetManager
        self.widget_manager.add_widget(model, widget, clamped_x, clamped_y)

        #populate model width and height after creating window and updating widget, otherwise both values are 1
        widget.update()
        model.width, model.height = widget.winfo_width(), widget.winfo_height()
        model.x, model.y = clamped_x, clamped_y

        #append the new model to the project_document
        self.project_document.widget_models.append(model)

        #set app state to dirty
        self._set_dirty()

    def _cut(self):
        print("cut")

    def _copy(self):
        print("copy")

    def _paste(self):
        print("paste")

    def _undo(self):
        print("undo")

    def _redo(self):
        print("redo")

    def _move(self, dx: int, dy: int):
        #get selected widgets
        selected_widgets = self.selection_manager.selected_ids()
        if not selected_widgets:
            return

        #calculate group clamped delta so that widgets can't be moved outside the canvas
        dx, dy = self._group_clamped_delta(selected_widgets, dx, dy)

        for widget_id in selected_widgets:
            #delegate actual movement (canvas item) to WidgetManager
            self.widget_manager.move(widget_id, dx, dy)

            #update model
            model = self.widget_manager.get_model_from_widget_id(widget_id)
            model.x += dx; model.y += dy

            #update attributes panel if only 1 widget is selected
            if len(selected_widgets) == 1:
                self.attributes_panel_manager.update_variable_from_model(model)

        #refresh outline
        self.selection_manager.refresh_all()

        #set app state to dirty
        self._set_dirty()

    def _snap_to_grid(self):
        #get selected widgets
        selected_widgets = self.selection_manager.selected_ids()
        if not selected_widgets:
            return

        grid_size = self.project_document.grid.size

        for widget_id in selected_widgets:
            #calculate necessary movement delta
            model = self.widget_manager.get_model_from_widget_id(widget_id)
            new_x, new_y = round(model.x / grid_size) * grid_size, round(model.y / grid_size) * grid_size
            dx, dy = new_x - model.x, new_y - model.y

            #delegate actual movement (canvas item) to WidgetManager
            self.widget_manager.move(widget_id, dx, dy)

            #update model
            model.x, model.y = new_x, new_y

        #refresh outline
        self.selection_manager.refresh_all()

        #set app state to dirty
        self._set_dirty()

    def _delete(self):
        #prevent concurrent delete calls
        if self._deleting:
            return

        #set deleting flag
        self._deleting = True

        #get selected widgets
        selected_widgets = self.selection_manager.selected_ids()
        #selected_widgets = [widget_id for widget_id in self.selection_manager.selected_ids() if self.canvas.type(widget_id) == "window"]

        #build messagebox text
        count_selected_widgets = len(selected_widgets)
        if count_selected_widgets == 0:
            return
        elif count_selected_widgets == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count_selected_widgets)} selected widgets?"

        if not messagebox.askyesno("Delete", messagebox_text):
            #clear deleting flag
            self._deleting = False
            return

        for widget_id in selected_widgets:
            #remove model from project_document
            model = self.widget_manager.get_model_from_widget_id(widget_id)
            try:
                self.project_document.widget_models.remove(model)
            except ValueError:
                pass

            #delegate actual deletion (canvas item) to WidgetManager
            self.widget_manager.delete(widget_id)

        #clear selection
        self.selection_manager.clear()

        #hide attributes panel
        self._on_selection_changed()

        #set app state to dirty
        self._set_dirty()

        #clear deleting flag
        self._deleting = False

    def _align(self, direction):
        #get selected widgets and last selected widget
        selected_widgets = self.selection_manager.selected_ids()
        last_selected_widget = self.selection_manager.last_selected_id()
        if not selected_widgets or not last_selected_widget:
            return

        reference_model_bbox = self.widget_manager.get_bbox_from_widget_id(last_selected_widget)

        for widget_id in selected_widgets:
            if not widget_id == last_selected_widget:
                model_bbox = self.widget_manager.get_bbox_from_widget_id(widget_id)

                #calculate necessary movement delta
                if direction == "left":
                    dx, dy = reference_model_bbox["left"] - model_bbox["left"], 0
                elif direction == "right":
                    dx, dy = reference_model_bbox["right"] - model_bbox["right"], 0
                elif direction == "top":
                    dx, dy = 0, reference_model_bbox["top"] - model_bbox["top"]
                elif direction == "bottom":
                    dx, dy = 0, reference_model_bbox["bottom"] - model_bbox["bottom"]
                else:
                    dx, dy = 0, 0

                #calculate clamped delta so that widget can't be moved outside the canvas
                dx, dy = self._clamped_delta(widget_id, dx, dy)

                #delegate actual movement (canvas item) to WidgetManager
                self.widget_manager.move(widget_id, dx, dy)

                #update model
                model = self.widget_manager.get_model_from_widget_id(widget_id)
                model.x += dx; model.y += dy

        #refresh outline
        self.selection_manager.refresh_all()

        #set app state to dirty
        self._set_dirty()

    def _toggle_grid(self):
        #flip grid visible variable
        self.grid_visible_variable.set(not self.grid_visible_variable.get())
        #apply grid visible state
        self._apply_grid_from_variable()

    def _apply_grid_from_variable(self):
        visible = self.grid_visible_variable.get()

        #write current grid visible state to project_document
        self.project_document.grid.visible = visible

        #delegate actual drawing of the grid (draw or clear) to CanvasManager
        self.canvas_manager.apply_grid_visibility()

        #set app state to dirty
        self._set_dirty()

    def _change_grid_size(self):
        #prompt for new grid size
        new_grid_size = simpledialog.askinteger("Grid size", "Enter new grid size:", minvalue=5, maxvalue=100, parent=self.parent)

        if new_grid_size is None:
            return

        #update grid size in project_document
        self.project_document.grid.size = new_grid_size

        #delegate redraw of grid to CanvasManager
        self.canvas_manager.refresh_grid()

        #set app state to dirty
        self._set_dirty()

    def _change_grid_color(self):
        #prompt for grid color
        if messagebox.askyesno("Change grid color", "Change grid color?"):
            color = colorchooser.askcolor()[1]
        else:
            self.canvas_manager.canvas.focus_set()
            return

        #abort if user didn't select a color
        if not color:
            return

        #update grid color in project_document
        self.project_document.grid.color = color

        #delegate redraw of grid to CanvasManager
        self.canvas_manager.refresh_grid()

        #set app state to dirty
        self._set_dirty()

    def _set_dirty(self):
        self._dirty = True
        self.title_label.configure(text=self.project_document.title + "*")
        self.title_label.update()

    def _set_clean(self):
        self._dirty = False
        self.title_label.configure(text=self.project_document.title)
        self.title_label.update()

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
            command=lambda: self._add_widget("label", *_pos())
        )
        self.menu.add_command(
            label="Add Entry",
            command=lambda: self._add_widget("entry", *_pos())
        )
        self.menu.add_command(
            label="Add Button",
            command=lambda: self._add_widget("button", *_pos())
        )

    #post context menu
    def _show_menu(self, event):
        self._click_x, self._click_y = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #compute clamped delta, so that widget cannot be moved outside the GUI window
    def _group_clamped_delta(self, widget_ids: frozenset, dx: int, dy: int) -> tuple[int, int]:
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx_clamped, dy_clamped = dx, dy

        for widget_id in widget_ids:
            bbox = self.canvas.bbox(widget_id)
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
    def _clamped_delta(self, widget_id: int, dx: int, dy: int) -> tuple[int, int]:
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx_clamped, dy_clamped = dx, dy

        bbox = self.canvas.bbox(widget_id)
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
            widget_id = next(iter(selected_ids))
            model = self.widget_manager.widget_map.get(widget_id)["model"]
            self.attributes_panel_manager.refresh(model)
        else:
            self.attributes_panel_manager.clear()

    def _on_attribute_changed(self, widget_id: int, attribute: str, value):
        if widget_id is None:
            return

        #apply change to the widget through WidgetManager
        self.widget_manager.update_widget_attribute(widget_id, attribute, value)

        #update model
        model = self.widget_manager.get_model_from_widget_id(widget_id)
        if hasattr(model, attribute):
            setattr(model, attribute, value)

        #recompute spinbox limits
        if attribute in ("anchor", "width", "height"):
            self.attributes_panel_manager.update_spinbox_limits(model)

        #refresh outline
        self.selection_manager.refresh(widget_id)

        #set app state to dirty
        self._set_dirty()

    def _allowed_x_range(self, width, anchor):
        canvas_width = int(self.canvas.winfo_width())
        if anchor in ["sw", "w", "nw"]:
            return 0, canvas_width - width
        elif anchor in ["ne", "e", "se"]:
            return width, canvas_width
        elif anchor in ["n", "s", "center"]:
            return width // 2, canvas_width - (width // 2)
        return 0, canvas_width

    def _allowed_y_range(self, height, anchor):
        canvas_height = int(self.canvas.winfo_height())
        if anchor in ["sw", "s", "se"]:
            return height, canvas_height
        elif anchor in ["nw", "n", "ne"]:
            return 0, canvas_height - height
        elif anchor in ["w", "e", "center"]:
            return height // 2, canvas_height - (height // 2)
        return 0, canvas_height

    #compute minimum window dimensions to fit the entire canvas without scrollbars
    def _compute_initial_window_dimensions(self):
        canvas_width = self.project_document.width
        canvas_height = self.project_document.height

        panel_width = self.constants["attributes_panel"]["width"]
        titlebar_height = self.constants["titlebar_height"]
        toolbar_height = self.constants["toolbar_height"]

        minimum_width = self.constants["window"]["min_width"]
        maximum_width = self.constants["window"]["max_width"]
        minimum_height = self.constants["window"]["min_height"]
        maximum_height = self.constants["window"]["max_height"]

        #ideal size (no scrollbar needed)
        ideal_width = canvas_width + panel_width
        ideal_height = canvas_height + toolbar_height + titlebar_height

        #enforce minimum
        ideal_width = max(ideal_width, minimum_width)
        ideal_height = max(ideal_height, minimum_height)

        #enforce maximum
        ideal_width = min(ideal_width, maximum_width)
        ideal_height = min(ideal_height, maximum_height)

        return ideal_width, ideal_height

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

    #decide which scrollbars to show based on canvas size and the visible viewport
    def _refresh_scrollbars(self):
        #ensure geometry is up-to-date
        self.top.update_idletasks()

        #viewer dimensions
        viewer_width = self.viewer.winfo_width()
        viewer_height = self.viewer.winfo_height()

        #canvas dimensions
        canvas_width = self.project_document.width
        canvas_height = self.project_document.height

        #scrollbar thickness
        vertical_scrollbar_thickness = self.vertical_scrollbar.winfo_reqwidth()
        horizontal_scrollbar_thickness = self.horizontal_scrollbar.winfo_reqheight()

        #check which scrollbar is needed
        need_vertical_scrollbar = canvas_height > viewer_height
        need_horizontal_scrollbar = canvas_width > viewer_width

        #if vertical scrollbar needed → reduces visible width → reevaluate horizontal
        if need_vertical_scrollbar:
            viewer_width_new = viewer_width - vertical_scrollbar_thickness
            need_horizontal_scrollbar = canvas_width > viewer_width_new

        #if horizontal scrollbar needed → reduces visible height → reevaluate vertical
        if need_horizontal_scrollbar:
            viewer_height_new = viewer_height - horizontal_scrollbar_thickness
            need_vertical_scrollbar = canvas_height > viewer_height_new

        #second pass
        if need_vertical_scrollbar:
            viewer_width_new = viewer_width - vertical_scrollbar_thickness
            need_horizontal_scrollbar = canvas_width > viewer_width_new
        if need_horizontal_scrollbar:
            viewer_height_new = viewer_height - horizontal_scrollbar_thickness
            need_vertical_scrollbar = canvas_height > viewer_height_new

        #add or remove scrollbars depending on if they're needed or not
        if need_vertical_scrollbar:
            self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        else:
            self.vertical_scrollbar.grid_remove()

        if need_horizontal_scrollbar:
            self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            self.horizontal_scrollbar.grid_remove()

        #update scroll region (always content size)
        self.viewer.configure(scrollregion=(0, 0, canvas_width, canvas_height))

    def _build_designer_ui(self):
        #create window
        self.top = tk.Toplevel(self.parent)

        #enforce minimum window size
        self.top.wm_minsize(self.constants["window"]["min_width"], self.constants["window"]["min_height"])

        #compute initial window dimensions
        window_width, window_height = self._compute_initial_window_dimensions()
        self.top.geometry(f"{window_width}x{window_height}")

        #create title bar
        self.title_label = None
        self._create_title_bar()

        #create main frame that hosts work area (column 0) and attributes panel (column 1)
        self.main_frame = tk.Frame(self.top, bg=self.project_document.theme["background"]["color"])

        #define column/row growth
        self.main_frame.columnconfigure(0, weight=1)    #work area expands
        self.main_frame.columnconfigure(1, weight=0)    #attributes panel fixed width
        self.main_frame.rowconfigure(0, weight=1)

        #create work area
        self.work_area = tk.Frame(self.main_frame, bg=self.project_document.theme["background"]["color"])
        self.work_area.grid(row=0, column=0, sticky="nsew")
        self.work_area.columnconfigure(0, weight=1)
        self.work_area.rowconfigure(0, weight=1)

        #create viewer for scrolling
        self.viewer = tk.Canvas(
            self.work_area,
            bg=self.project_document.theme["background"]["color"],
            highlightthickness=0
        )
        self.viewer.grid(row=0, column=0, sticky="nsew")

        #create scrollbars
        self.vertical_scrollbar = tk.Scrollbar(self.work_area, orient="vertical", command=self.viewer.yview)
        self.horizontal_scrollbar = tk.Scrollbar(self.work_area, orient="horizontal", command=self.viewer.xview)
        self.viewer.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)

        #create attributes panel frame
        self.attributes_panel_frame = tk.Frame(
            self.main_frame,
            width=self.constants["attributes_panel"]["width"],
            bg=self.program_theme["attributes_panel"]["color"]
        )
        self.attributes_panel_frame.grid(row=0, column=1, sticky="ns")
        self.attributes_panel_frame.pack_propagate(False)   #fixed width
        self.attributes_panel_frame.grid_propagate(False)   #fixed width

        #recompute when viewer's size changes
        self.viewer.bind("<Configure>", lambda e: self._refresh_scrollbars())

        # Force final evaluation after window is mapped
        self.top.after(0, self._refresh_scrollbars)
        self.top.after_idle(self._refresh_scrollbars)

    @staticmethod
    def _clamp(value, minimum, maximum):
        return max(minimum, min(maximum, value))