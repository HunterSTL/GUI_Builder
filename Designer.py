#tkinter
import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, ttk
#dataclasses
from _dataclasses import DesignerState
from _dataclasses import ProjectDocument
from _dataclasses import LabelWidgetData, EntryWidgetData, ButtonWidgetData
#managers
from _managers import CanvasManager
from _managers import SelectionManager
from _managers import ToolbarManager
from _managers import WidgetManager
from _managers import AttributesPanelManager
#commands
from _commands import CommandStack, MoveWidgets, MoveWidgetsTo
#misc
from PIL import ImageTk
from Geometry import allowed_x_range, allowed_y_range, clamp, clamped_delta, screen_offset_to_center_window

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

        #designer state (last click position, dirty flag, deleting flag etc.)
        self.state = DesignerState()

        #command stack
        self.command_stack = CommandStack()

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
            last_selected_color=self.program_theme["selection"]["last_selected_color"],
            drag_threshold=self.constants["drag_threshold"],
            callbacks=self.callbacks
        )

        #create instance of WidgetManager to store created widgets
        self.widget_manager = WidgetManager(
            top=self.top,
            canvas=self.canvas,
            project_document=self.project_document,
            selection_manager=self.selection_manager
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
                "release": self.selection_manager.handle_canvas_release,
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
                "start_drag": self._start_drag,
                "end_drag": self._end_drag,
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
        return self.state.is_dirty

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
        min_x, max_x = allowed_x_range(self.canvas.winfo_width(), required_width, model.anchor)
        min_y, max_y = allowed_y_range(self.canvas.winfo_height(), required_height, model.anchor)
        clamped_x = clamp(x, min_x, max_x)
        clamped_y = clamp(y, min_y, max_y)

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
        self.command_stack.undo()
        self.selection_manager.refresh_all()
        self._set_dirty()

    def _redo(self):
        self.command_stack.redo()
        self.selection_manager.refresh_all()
        self._set_dirty()

    def _move(self, dx: int, dy: int):
        #get selected widgets
        selected_widgets = self.selection_manager.selected_ids()
        if not selected_widgets:
            return

        #calculate clamped delta of all selected widgets so that widgets can't be moved outside the canvas
        dx, dy = clamped_delta(
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            self.canvas.bbox(*selected_widgets),
            dx, dy
        )

        #moving widgets by dragging
        if self.selection_manager.is_dragging() and self.state.active_widget_drag_command:
            self.state.active_widget_drag_command.preview_move(dx, dy)
        else:
            #moving widgets with keyboard shortcuts (nudge)
            self.command_stack.execute(MoveWidgets(selected_widgets, dx, dy, self.widget_manager))

        #update attributes panel if only one widget is selected
        if len(selected_widgets) == 1:
            model = self.widget_manager.get_model_from_widget_id(next(iter(selected_widgets)))
            self.attributes_panel_manager.update_variable_from_model(model)

        #set app state to dirty
        self._set_dirty()

    def _start_drag(self):
        #get selected widgets
        selected_widgets = self.selection_manager.selected_ids()

        #reset active_widget_drag_command if no widgets selected
        if not selected_widgets:
            self.state.active_widget_drag_command = None
            return

        #create the MoveWidgetsTo command to record original widget positions
        self.state.active_widget_drag_command = MoveWidgetsTo(selected_widgets, self.widget_manager)

    def _end_drag(self):
        #get active widget drag command
        cmd = self.state.active_widget_drag_command

        if not cmd:
            return

        if cmd and cmd.has_effect():
            #record final widget positions
            cmd.freeze_final_positions()

            #execute the actual command
            self.command_stack.execute(cmd)

        #reset active_widget_drag_command
        self.state.active_widget_drag_command = None

        #refresh all outline
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
        if self.state.is_deleting:
            return

        #get selected widgets
        selected_widgets = self.selection_manager.selected_ids()

        #build messagebox text
        count_selected_widgets = len(selected_widgets)
        if count_selected_widgets == 0:
            return
        elif count_selected_widgets == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count_selected_widgets)} selected widgets?"

        if not messagebox.askyesno("Delete", messagebox_text):
            return

        #set deleting flag
        self.state.is_deleting = True

        try:
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
        finally:
            #clear deleting flag
            self.state.is_deleting = False

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
                dx, dy = clamped_delta(self.canvas.winfo_width(), self.canvas.winfo_height(), self.canvas.bbox(widget_id), dx, dy)

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
        color = colorchooser.askcolor()[1]

        #abort if user didn't select a color
        if not color:
            return

        #update grid color in project_document
        self.project_document.grid.color = color

        #delegate redraw of grid to CanvasManager
        self.canvas_manager.refresh_grid()

        #set focus back to canvas
        self.canvas.focus_set()

        #set app state to dirty
        self._set_dirty()

    def _set_dirty(self):
        self.state.is_dirty = True
        self.title_label.configure(text=self.project_document.title + "*")
        self.title_label.update()

    def _set_clean(self):
        self.state.is_dirty = False
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
            if self.state.last_click_coords is None:
                return 100, 100
            else:
                return self.state.last_click_coords

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
        self.state.last_click_coords = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

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

    #compute minimum window dimensions to fit the entire canvas without scrollbars, then enforce maximum constraints
    def _compute_initial_window_dimensions(self):
        #ensure geometry is up-to-date
        self.top.update_idletasks()

        #requested canvas dimensions
        canvas_width = self.project_document.width
        canvas_height = self.project_document.height

        #dimensions of UI elements
        panel_width = self.constants["attributes_panel"]["width"]
        titlebar_height = self.constants["titlebar_height"]
        toolbar_height = self.constants["toolbar_height"]
        vertical_scrollbar_thickness = self.vertical_scrollbar.winfo_reqwidth()
        horizontal_scrollbar_thickness = self.horizontal_scrollbar.winfo_reqheight()

        #minimum/maximum designer window dimensions
        minimum_width = self.constants["window"]["min_width"]
        maximum_width = self.constants["window"]["max_width"]
        minimum_height = self.constants["window"]["min_height"]
        maximum_height = self.constants["window"]["max_height"]

        #compute ideal designer window dimensions to fit the entire canvas without scrollbars
        required_window_width = canvas_width + panel_width
        required_window_height = canvas_height + toolbar_height + titlebar_height

        #compute actual designer window dimensions (enforce min/max constraints)
        window_width = clamp(required_window_width, minimum_width, maximum_width)
        window_height = clamp(required_window_height, minimum_height, maximum_height)

        #derive available viewport from clamped window size
        viewport_width = max(0, window_width - panel_width)
        viewport_height = max(0, window_height - (toolbar_height + titlebar_height))

        #check whether scrollbars are needed
        need_horizontal_scrollbar = canvas_width > viewport_width
        need_vertical_scrollbar = canvas_height > viewport_height

        window_width_new, window_height_new = window_width, window_height

        for _ in range(2):
            #vertical scrollbar needed → add scrollbar width to window width → enforce min/max → check whether horizontal scrollbar is needed
            if need_vertical_scrollbar:
                window_width_new = clamp(window_width + vertical_scrollbar_thickness, minimum_width, maximum_width)
                viewport_width = max(0, window_width_new - panel_width)
                need_horizontal_scrollbar = canvas_width > viewport_width

            #horizontal scrollbar needed → add scrollbar width to window height → enforce min/max → check whether vertical scrollbar is needed
            if need_horizontal_scrollbar:
                window_height_new = clamp(window_height + horizontal_scrollbar_thickness, minimum_height, maximum_height)
                viewport_height = max(0, window_height_new - (toolbar_height + titlebar_height))
                need_vertical_scrollbar = canvas_height > viewport_height

        return window_width_new, window_height_new

    #decide which scrollbars to show based on canvas size and the visible viewport
    def _refresh_scrollbars(self):
        #ensure geometry is up-to-date
        self.top.update_idletasks()

        #canvas dimensions
        canvas_width = self.project_document.width
        canvas_height = self.project_document.height

        #scrollbar thickness
        vertical_scrollbar_thickness = self.vertical_scrollbar.winfo_reqwidth()
        horizontal_scrollbar_thickness = self.horizontal_scrollbar.winfo_reqheight()

        #viewport dimensions
        viewport_width = self.work_area.winfo_width()
        viewport_height = self.work_area.winfo_height()

        #check whether scrollbars are needed
        need_horizontal_scrollbar = canvas_width > viewport_width
        need_vertical_scrollbar = canvas_height > viewport_height

        for _ in range(2):
            #vertical scrollbar needed → reduce viewport width by scrollbar width → check whether horizontal scrollbar is needed
            if need_vertical_scrollbar:
                viewport_width_new = viewport_width - vertical_scrollbar_thickness
                need_horizontal_scrollbar = canvas_width > viewport_width_new

            #horizontal scrollbar needed → reduce viewport height by scrollbar width → check whether vertical scrollbar is needed
            if need_horizontal_scrollbar:
                viewport_height_new = viewport_height - horizontal_scrollbar_thickness
                need_vertical_scrollbar = canvas_height > viewport_height_new

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

    def _configure_scrollbar_style(self):
        style = ttk.Style(self.top)
        style.theme_use("default")  #allows colors
        style.configure(
            "Designer.Vertical.TScrollbar",
            troughcolor=self.program_theme["scrollbar"]["trough_color"],
            background=self.program_theme["scrollbar"]["background_color"],
            arrowcolor=self.program_theme["scrollbar"]["arrow_color"],
            bordercolor=self.program_theme["scrollbar"]["border_color"]
        )
        style.configure(
            "Designer.Horizontal.TScrollbar",
            troughcolor=self.program_theme["scrollbar"]["trough_color"],
            background=self.program_theme["scrollbar"]["background_color"],
            arrowcolor=self.program_theme["scrollbar"]["arrow_color"],
            bordercolor=self.program_theme["scrollbar"]["border_color"]
        )

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", lambda e: self.viewer.yview_scroll(-1 * int(e.delta / 120), "units"))
        widget.bind("<Shift-MouseWheel>", lambda e: self.viewer.xview_scroll(-1 * int(e.delta / 120), "units"))

    #create a custom draggable title bar with a close button
    def _create_title_bar(self):
        def start_move(event):
            self.state.drag_start_coords = event.x_root, event.y_root
            self.state.window_coords = self.top.winfo_x(), self.top.winfo_y()

        def do_move(event):
            dx = event.x_root - self.state.drag_start_coords[0]
            dy = event.y_root - self.state.drag_start_coords[1]
            self.top.geometry(f"+{self.state.window_coords[0] + dx}+{self.state.window_coords[1] + dy}")

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

    #center window
    def _center_window(self):
        self.top.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self.top.winfo_screenwidth(),
            self.top.winfo_screenheight(),
            self.top.winfo_width(),
            self.top.winfo_height()
        )
        self.top.geometry(f"+{x_offset}+{y_offset}")

    def _build_designer_ui(self):
        #create window
        self.top = tk.Toplevel(self.parent)

        #enforce minimum window size
        self.top.wm_minsize(self.constants["window"]["min_width"], self.constants["window"]["min_height"])

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

        #bind mousewheel for scrolling
        self._bind_mousewheel(self.top)

        #create scrollbars
        self._configure_scrollbar_style()
        self.vertical_scrollbar = ttk.Scrollbar(
            self.work_area,
            orient="vertical",
            command=self.viewer.yview,
            style="Designer.Vertical.TScrollbar"
        )
        self.horizontal_scrollbar = ttk.Scrollbar(
            self.work_area,
            orient="horizontal",
            command=self.viewer.xview,
            style="Designer.Horizontal.TScrollbar"
        )
        self.viewer.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)

        #compute initial window dimensions
        window_width, window_height = self._compute_initial_window_dimensions()
        self.top.geometry(f"{window_width}x{window_height}")

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

        self._center_window()