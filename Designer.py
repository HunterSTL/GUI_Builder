#tkinter
import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, ttk
#model
from AppState import AppState
#dataclasses
from _dataclasses import DesignerState
from _dataclasses import ProjectDocument
from _dataclasses import LabelWidgetData, EntryWidgetData, ButtonWidgetData
#managers
from _managers import CanvasController
from _managers import CanvasView
from _managers import SelectionManager
from _managers import ToolbarManager
from _managers import WidgetManager
from _managers import AttributesPanelManager
#commands
from _commands import CommandStack, MoveWidgets, MoveWidgetsTo
#misc
from Geometry import allowed_x_range, allowed_y_range, clamp, clamped_delta, screen_offset_to_center_window
from UIComponents import CustomTitlebar
from CallTracer import call_tracer

class Designer:
    def __init__(
        self,
        parent: tk.Tk,
        project_document: ProjectDocument,
        program_theme: dict,
        constants: dict,
        project_callbacks: dict
    ):
        """initialize the Designer window, UI, managers, callbacks, and state"""
        self.parent = parent
        self.program_theme = program_theme
        self.constants = constants
        self.project_callbacks = project_callbacks

        #shared mutable callbacks dictionary
        self.callbacks = {}

        #app state (pure model)
        self.app_state = AppState(project_document)

        #designer state (last click position, dirty flag, deleting flag etc.)
        self.state = DesignerState()

        #command stack
        self.command_stack = CommandStack()

        #variable to represent grid state from project_document
        self.grid_visible_variable = tk.BooleanVar(value=self.app_state.project.grid.visible)

        #build designer UI
        self._build_designer_ui()

        #create CanvasView to render the grid---------------------------------------------------------------------------
        self.canvas_view = CanvasView(
            parent=self.viewer,
            project_document=self.app_state.project
        )
        self.canvas = self.canvas_view.canvas

        #embed inner canvas into the scrollable viewer
        self.canvas_window_id = self.viewer.create_window(0, 0, window=self.canvas, anchor="nw")

        #draw boundry around the work area
        self._boundry = self.canvas.create_rectangle(
            1, 1, self.app_state.project.width - 1, self.app_state.project.height - 1,
            outline=self.program_theme["selection"]["color"],
            width=1,
            dash=(2, 2)
        )

        #draw grid in case project_document.grid.visible is True
        self.canvas_view.refresh_grid()

        #create CanvasController to create key binds--------------------------------------------------------------------
        self.canvas_controller = CanvasController(
            view=self.canvas_view,
            nudge_small=self.constants["nudge"]["small"],
            nudge_big=self.constants["nudge"]["big"],
            callbacks=self.callbacks
        )

        #create SelectionManager to store selected widgets--------------------------------------------------------------
        self.selection_manager = SelectionManager(
            canvas=self.canvas,
            ctrl_key=self.constants["ctrl_key"],
            selection_width=self.constants["selection"]["width"],
            selection_dash=self.constants["selection"]["dash"],
            selection_padding=self.constants["selection"]["padding"],
            selection_color=self.program_theme["selection"]["color"],
            last_selected_color=self.program_theme["selection"]["last_selected_color"],
            drag_threshold=self.constants["drag_threshold"],
            callbacks=self.callbacks,
            resolve_model_to_widget=lambda model_id: self.widget_manager.get_widget_id_from_model_id(model_id),
            resolve_widget_to_model=lambda widget_id: self.widget_manager.get_model_id_from_widget_id(widget_id)
        )

        #create WidgetManager to store created widgets------------------------------------------------------------------
        self.widget_manager = WidgetManager(
            top=self.top,
            canvas=self.canvas,
            app_state=self.app_state,
            selection_manager=self.selection_manager
        )

        #create AttributesPanelManager to show/hide the attribute panel for a selected widget---------------------------
        self.attributes_panel_manager = AttributesPanelManager(
            root=self.top,
            frame=self.attributes_panel_frame,
            canvas_width=self.app_state.project.width,
            canvas_height=self.app_state.project.height,
            panel_color=self.program_theme["attributes_panel"]["color"],
            widget_color=self.program_theme["attributes_panel"]["widget_color"],
            text_color=self.program_theme["attributes_panel"]["text_color"],
            selection_manager=self.selection_manager,
            callbacks=self.callbacks
        )

        #create ToolbarManager to store theme and function callbacks----------------------------------------------------
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

        #build shared callback dictionary-------------------------------------------------------------------------------
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
            "toggle_call_tracing": call_tracer.toggle,
            "set_dirty": self._set_dirty,
            "set_clean": self._set_clean
        })

        #call functions that require the callback dictionary to be built------------------------------------------------
        #create toolbar
        self.toolbar_manager.create_toolbar()

        #pack main frame after creating toolbar so toolbar is on top
        self.main_frame.pack(side="top", fill="both", expand=True)

        #bind events to canvas
        self.canvas_controller.bind_events()

        #create context menu (right click) for creating new widgets
        self._add_widget_menu()

        #create widgets for the existing models in the project_document
        for model in self.app_state.project.widget_models:
            self.widget_manager.add_widget_from_model(model)

        #subscribe the function "_on_changed_state" as a listener for state changes
        self.app_state.subscribe(self._on_changed_state)

    def _on_changed_state(self, state):
        """respond to AppState mutations by performing full or soft rendering"""
        #re-render entire app state if structural change happened (widget creation/deletion, grid settings)
        if state.structural_change or len(state.dirty_model_ids) > 10:  #full render may be faster than doing soft render for multiple models
            self._do_full_render()
            return

        #only update dirty models
        for model_id in state.dirty_model_ids:
            model = self.widget_manager.get_model_from_model_id(model_id)
            self._do_soft_render(model)

    def _do_full_render(self):
        """perform a full re-render of widgets, selection outlines, and grid"""
        call_tracer.log_event(f"full render\n{'#'*150}")
        self.widget_manager.render_full()       #render widgets
        self.selection_manager.refresh_all()    #refresh widget outlines
        self.canvas_view.refresh_grid()      #refresh grid

    def _do_soft_render(self, model):
        """perform a soft re-render limited to a single updated widget"""
        call_tracer.log_event(f"soft render {model.id}")
        self.widget_manager.render_soft(model)

    def is_dirty(self):
        """return True if the project has unsaved changes"""
        return self.state.is_dirty

    def set_clean(self):
        """mark project state as clean (no unsaved changes)"""
        self._set_clean()

    def _add_widget(self, widget_type: str, x: int, y: int):
        """create a new widget of the given type at the given coordinates"""
        if widget_type == "label":
            text = simpledialog.askstring("Label text", "Enter label text:", parent=self.top)
            if text is None:
                return
            bg = self.app_state.project.theme["label"]["bg"]
            fg = self.app_state.project.theme["label"]["fg"]
            widget = tk.Label(
                self.canvas,
                text=text,
                bg=bg,
                fg=fg
            )
            model = LabelWidgetData(x=x, y=y, bg=bg, fg=fg, text=text)
        elif widget_type == "entry":
            bg = self.app_state.project.theme["entry"]["bg"]
            fg = self.app_state.project.theme["entry"]["fg"]
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
            bg = self.app_state.project.theme["button"]["bg"]
            fg = self.app_state.project.theme["button"]["fg"]
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

        #batch app state changes so _on_changed_state gets called only once (instead of per change)
        with self.app_state.batch():
            #append the new model to the project_document via AppState
            self.app_state.add_widget(model)

            #populate model width and height after creating window and updating widget, otherwise both values are 1
            widget.update()
            self.app_state.set_widget_attribute(model, "width", widget.winfo_width())
            self.app_state.set_widget_attribute(model, "height", widget.winfo_height())

            #set absolute position via AppState
            self.app_state.move_widget_to(model, clamped_x, clamped_y)

        #clear selection
        self.selection_manager.clear()

        #set app state to dirty
        self._set_dirty()

    def _cut(self):
        """cut selected widgets (placeholder)"""
        print("cut")

    def _copy(self):
        """copy selected widgets (placeholder)"""
        print("copy")

    def _paste(self):
        """paste widgets (placeholder)"""
        print("paste")

    def _undo(self):
        """undo last command and refresh selection outlines"""
        self.command_stack.undo()
        self.selection_manager.refresh_all()
        self._set_dirty()

    def _redo(self):
        """redo last undone command and refresh selection outlines"""
        self.command_stack.redo()
        self.selection_manager.refresh_all()
        self._set_dirty()

    def _move(self, dx: int, dy: int):
        """move selected widgets by a delta or preview drag movement"""
        #get selected widgets
        selected_model_ids = self.selection_manager.selected_model_ids()
        if not selected_model_ids:
            return

        #calculate clamped delta of all selected widgets so that widgets can't be moved outside the canvas
        selected_widget_ids = set(self.widget_manager.get_widget_id_from_model_id(model_id) for model_id in selected_model_ids)
        dx, dy = clamped_delta(
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            self.canvas.bbox(*selected_widget_ids),
            dx, dy
        )

        if self.selection_manager.is_dragging() and self.state.active_widget_drag_command:
            #moving widgets by dragging
            self.state.active_widget_drag_command.preview_move(dx, dy)
        else:
            #moving widgets with keyboard shortcuts (nudge)
            self.command_stack.execute(MoveWidgets(selected_model_ids, dx, dy, self.widget_manager))

        #update attributes panel if only one widget is selected
        if len(selected_model_ids) == 1:
            model = self.widget_manager.get_model_from_model_id(next(iter(selected_model_ids)))
            self.attributes_panel_manager.update_variable_from_model(model)

        #set app state to dirty
        self._set_dirty()

    def _start_drag(self):
        """initialize a MoveWidgetsTo command when dragging begins"""
        #get selected widgets
        selected_model_ids = self.selection_manager.selected_model_ids()

        #reset active_widget_drag_command if no widgets selected
        if not selected_model_ids:
            self.state.active_widget_drag_command = None
            return

        #create the MoveWidgetsTo command to record original widget positions
        self.state.active_widget_drag_command = MoveWidgetsTo(selected_model_ids, self.widget_manager)

    def _end_drag(self):
        """finalize drag movement, executing stored MoveWidgetsTo command"""
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
        """align selected widgets to nearest grid positions"""
        #get selected widgets
        selected_model_ids = self.selection_manager.selected_model_ids()
        if not selected_model_ids:
            return

        grid_size = self.app_state.project.grid.size

        with self.app_state.batch():
            for model_id in selected_model_ids:
                #calculate necessary movement delta
                model = self.widget_manager.get_model_from_model_id(model_id)
                new_x, new_y = round(model.x / grid_size) * grid_size, round(model.y / grid_size) * grid_size

                #set absolute position via AppState
                self.app_state.move_widget_to(model, new_x, new_y)

        #set app state to dirty
        self._set_dirty()

    def _delete(self):
        """delete selected widgets from project and canvas"""
        #prevent concurrent delete calls
        if self.state.is_deleting:
            return

        #get selected model ids
        selected_model_ids = self.selection_manager.selected_model_ids()

        #build messagebox text
        count = len(selected_model_ids)
        if count == 0:
            return
        elif count == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count)} selected widgets?"

        if not messagebox.askyesno("Delete", messagebox_text):
            return

        #clear selection
        self.selection_manager.clear()

        #set deleting flag
        self.state.is_deleting = True

        try:
            with self.app_state.batch():
                for model_id in selected_model_ids:
                    #remove model from project_document
                    model = self.widget_manager.get_model_from_model_id(model_id)
                    self.app_state.remove_widget(model)

                    #delete widget from widget manager
                    widget_id = self.widget_manager.get_widget_id_from_model_id(model_id)
                    self.widget_manager.delete(widget_id)   #removes from widget_id <> model_id mapping and widget map and deletes the actual tk widget
        finally:
            #clear deleting flag
            self.state.is_deleting = False

            #set app state to dirty
            self._set_dirty()

    def _align(self, direction):
        """align selected widgets relative to the last selected widget"""
        #get selected widgets and last selected widget
        selected_model_ids = self.selection_manager.selected_model_ids()
        last_selected_model_id = self.selection_manager.last_selected_model_id()
        if not selected_model_ids or not last_selected_model_id:
            return

        reference_widget_bbox = self.widget_manager.get_bbox_from_model_id(last_selected_model_id)

        if not reference_widget_bbox:
            return

        with self.app_state.batch():
            for model_id in selected_model_ids:
                if not model_id == last_selected_model_id:
                    widget_bbox = self.widget_manager.get_bbox_from_model_id(model_id)

                    if not widget_bbox:
                        return

                    #calculate necessary movement delta
                    if direction == "left":
                        dx, dy = reference_widget_bbox["left"] - widget_bbox["left"], 0
                    elif direction == "right":
                        dx, dy = reference_widget_bbox["right"] - widget_bbox["right"], 0
                    elif direction == "top":
                        dx, dy = 0, reference_widget_bbox["top"] - widget_bbox["top"]
                    elif direction == "bottom":
                        dx, dy = 0, reference_widget_bbox["bottom"] - widget_bbox["bottom"]
                    else:
                        dx, dy = 0, 0

                    #calculate clamped delta so that widget can't be moved outside the canvas
                    widget_id = self.widget_manager.get_widget_id_from_model_id(model_id)
                    dx, dy = clamped_delta(self.canvas.winfo_width(), self.canvas.winfo_height(), self.canvas.bbox(widget_id), dx, dy)

                    #move widget via AppState
                    model = self.widget_manager.get_model_from_model_id(model_id)
                    self.app_state.move_widget_by(model, dx, dy)

        #set app state to dirty
        self._set_dirty()

    def _toggle_grid(self):
        """toggle grid visibility"""
        #flip grid visible variable
        self.grid_visible_variable.set(not self.grid_visible_variable.get())
        #apply grid visible state
        self._apply_grid_from_variable()

    def _apply_grid_from_variable(self):
        """apply grid visibility state from BooleanVar to AppState"""
        visible = self.grid_visible_variable.get()

        #write current grid visible state to project_document
        self.app_state.set_grid_visible(visible)

        #set app state to dirty
        self._set_dirty()

    def _change_grid_size(self):
        """prompt for and apply a new grid size"""
        #prompt for new grid size
        new_grid_size = simpledialog.askinteger("Grid size", "Enter new grid size:", minvalue=5, maxvalue=100, parent=self.parent)

        if new_grid_size is None:
            return

        #update grid size in project_document
        self.app_state.set_grid_size(new_grid_size)

        #set app state to dirty
        self._set_dirty()

    def _change_grid_color(self):
        """prompt for and apply a new grid color"""
        color = colorchooser.askcolor()[1]

        #abort if user didn't select a color
        if not color:
            return

        #update grid color in project_document
        self.app_state.set_grid_color(color)

        #set focus back to canvas
        self.canvas.focus_set()

        #set app state to dirty
        self._set_dirty()

    def _set_dirty(self):
        """mark project as dirty and update titlebar"""
        self.state.is_dirty = True
        self.titlebar_label.configure(text=self.app_state.project.title + "*")
        self.titlebar_label.update()

    def _set_clean(self):
        """mark project as clean and update titlebar"""
        self.state.is_dirty = False
        self.titlebar_label.configure(text=self.app_state.project.title)
        self.titlebar_label.update()

    def _add_widget_menu(self):
        """construct the context menu for adding widgets"""
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

    def _show_menu(self, event):
        """show the context menu at the mouse position"""
        self.state.last_click_coords = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    def _on_selection_changed(self):
        """update attributes panel when selection changes"""
        selected_model_ids = self.selection_manager.selected_model_ids()
        call_tracer.log_event(f"selection changed: {selected_model_ids}")
        if len(selected_model_ids) == 1:
            model_id = next(iter(selected_model_ids))
            model = self.widget_manager.get_model_from_model_id(model_id)
            self.attributes_panel_manager.refresh(model)
        else:
            self.attributes_panel_manager.clear()

    def _on_attribute_changed(self, model_id: str, attribute: str, value):
        """apply attribute changes coming from the attributes panel"""
        if model_id is None:
            return

        #apply change to the widget through WidgetManager
        self.widget_manager.update_widget_attribute(model_id, attribute, value)

        #recompute spinbox limits
        model = self.widget_manager.get_model_from_model_id(model_id)
        if attribute in ("anchor", "width", "height"):
            self.attributes_panel_manager.update_spinbox_limits(model)

        #refresh outline
        self.selection_manager.refresh(model_id)

        #set app state to dirty
        self._set_dirty()

    def _compute_initial_window_dimensions(self):
        """compute initial Designer window size based on canvas and constraints"""
        #ensure geometry is up-to-date
        self.top.update_idletasks()

        #requested canvas dimensions
        canvas_width = self.app_state.project.width
        canvas_height = self.app_state.project.height

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

    def _refresh_scrollbars(self):
        """compute which scrollbars should be visible and update layout"""
        #ensure geometry is up-to-date
        self.top.update_idletasks()

        #canvas dimensions
        canvas_width = self.app_state.project.width
        canvas_height = self.app_state.project.height

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
        """configure custom scrollbar styles"""
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
        """bind mousewheel scrolling behavior to a widget (in this case the Toplevel)"""
        widget.bind("<MouseWheel>", lambda e: self.viewer.yview_scroll(-1 * int(e.delta / 120), "units"))
        widget.bind("<Shift-MouseWheel>", lambda e: self.viewer.xview_scroll(-1 * int(e.delta / 120), "units"))

    def _center_window(self):
        """center the Designer window on screen"""
        self.top.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self.top.winfo_screenwidth(),
            self.top.winfo_screenheight(),
            self.top.winfo_width(),
            self.top.winfo_height()
        )
        self.top.geometry(f"+{x_offset}+{y_offset}")

    def _build_designer_ui(self):
        """construct the full Designer UI layout and its components"""
        #create window
        self.top = tk.Toplevel(self.parent)

        #enforce minimum window size
        self.top.wm_minsize(self.constants["window"]["min_width"], self.constants["window"]["min_height"])

        #create title bar
        titlebar = CustomTitlebar(
            parent=self.top,
            title=self.app_state.project.title,
            height=self.constants["titlebar_height"],
            bg_color=self.program_theme["titlebar"]["bg"],
            fg_color=self.program_theme["titlebar"]["fg"],
            icon_path=self.app_state.project.icon_path,
            on_close=self.project_callbacks["exit_app"]
        )
        titlebar.frame.pack(fill="x")
        self.titlebar_label = titlebar.label

        #create main frame that hosts work area (column 0) and attributes panel (column 1)
        self.main_frame = tk.Frame(self.top, bg=self.app_state.project.theme["background"]["color"])

        #define column/row growth
        self.main_frame.columnconfigure(0, weight=1)    #work area expands
        self.main_frame.columnconfigure(1, weight=0)    #attributes panel fixed width
        self.main_frame.rowconfigure(0, weight=1)

        #create work area
        self.work_area = tk.Frame(self.main_frame, bg=self.app_state.project.theme["background"]["color"])
        self.work_area.grid(row=0, column=0, sticky="nsew")
        self.work_area.columnconfigure(0, weight=1)
        self.work_area.rowconfigure(0, weight=1)

        #create viewer for scrolling
        self.viewer = tk.Canvas(
            self.work_area,
            bg=self.app_state.project.theme["background"]["color"],
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