import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, ttk
from model import DesignerState, ProjectDocument, LabelWidgetData, EntryWidgetData, ButtonWidgetData
from view import AttributesPanelView, CanvasView, SelectionView, ToolbarView, WidgetView
from controller import AttributesPanelController, CanvasController, SelectionController, ToolbarController, WidgetController
from events import EventBus, EventRouter
from commands import CommandStack, MoveWidgets, MoveWidgetsTo
from utility import call_tracer, allowed_x_range, allowed_y_range, clamp, clamped_delta, screen_offset_to_center_window, nearest_in_bounds_grid_step, CustomTitlebar
from AppState import AppState

class Designer:
    """
    Responsible for constructing the editor window, wiring
    together views, controllers and state and coordinating user interaction
    with the underlying ProjectDocument via AppState.

    Responsibilities include:
    *Building and owning the Designer window layout and scrollable work area
    *Creating and connecting all major views (attributes panel, canvas, selection, toolbar, widget)
    *Routing user input via the EventBus into edit, widget, grid and UI actions
    *Managing rendering in response to AppState mutations (full and soft renders)
    *Executing domain-specific editor logic (widget creation, alignment, snapping)
    *Tracking dirty state and updating the window title accordingly
    """
    #Construction-------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        parent: tk.Tk,
        project_document: ProjectDocument,
        program_theme: dict,
        constants: dict,
        app_event_bus: EventBus
    ):
        """initialize the Designer window, UI, managers, callbacks, and state"""
        self.parent = parent
        self.program_theme = program_theme
        self.constants = constants

        #Event system---------------------------------------------------------------------------------------------------
        #application events live for the entire application lifetime (owned by AppController)
        self.app_event_bus = app_event_bus

        #UI events are local to this Designer instance and are discarded when the Designer window is destroyed
        self.ui_event_bus = EventBus()

        #EventRouter: provides a single interface for emitting events and routes events to the correct EventBus
        self.event_router = EventRouter(
            app_event_bus=self.app_event_bus,
            ui_event_bus=self.ui_event_bus
        )

        #This split prevents callbacks from referencing destroyed Tk widgets
        #----------------------------------------------------------------------------------------------------------------

        #AppState: central model mutation engine
        self.app_state = AppState(project_document)

        #DesignerState: last click position, dirty flag, deleting flag etc.
        self.state = DesignerState()

        #CommandStack: provides undo/redo functionality
        self.command_stack = CommandStack()

        #stores a copy of the model for every copied widget
        self.clipboard = []

        #variable to represent grid state from ProjectDocument
        self.grid_visible_variable = tk.BooleanVar(value=self.app_state.project.grid.visible)

        #build designer UI
        self._build_designer_ui()

        #create CanvasView to render the grid---------------------------------------------------------------------------
        self.canvas_view = CanvasView(
            parent=self.viewer,
            canvas_width=self.app_state.project.width,
            canvas_height=self.app_state.project.height,
            background_color=self.app_state.project.theme["background"]["color"]
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

        #create CanvasController to create key binds--------------------------------------------------------------------
        self.canvas_controller = CanvasController(
            app_state=self.app_state,
            canvas_view=self.canvas_view,
            nudge_small=self.constants["nudge"]["small"],
            nudge_big=self.constants["nudge"]["big"],
            event_router=self.event_router
        )

        #create SelectionView to render selection rectangle and selection outlines--------------------------------------
        self.selection_view = SelectionView(
            canvas=self.canvas,
            selection_color=self.program_theme["selection"]["color"],
            last_selected_color=self.program_theme["selection"]["last_selected_color"],
            selection_width=self.constants["selection"]["width"],
            selection_dash=self.constants["selection"]["dash"],
            selection_padding=self.constants["selection"]["padding"]
        )

        #create SelectionController to handle selection and drag gestures-----------------------------------------------
        self.selection_controller = SelectionController(
            canvas=self.canvas,
            app_state=self.app_state,
            selection_view=self.selection_view,
            ctrl_key=self.constants["ctrl_key"],
            drag_threshold=self.constants["drag_threshold"],
            resolve_model_to_widget=lambda model_id: self.widget_view.get_widget_id_from_model_id(model_id),
            resolve_widget_to_model=lambda widget_id: self.widget_view.get_model_id_from_widget_id(widget_id),
            event_router=self.event_router
        )

        #create WidgetView to render widget models and store mappings---------------------------------------------------
        self.widget_view = WidgetView(
            canvas=self.canvas
        )

        #create WidgetController to handle widget mutations-------------------------------------------------------------
        self.widget_controller = WidgetController(
            app_state=self.app_state,
            widget_view=self.widget_view
        )

        #create AttributePanelView to render the attributes and bind tk variables---------------------------------------
        self.attributes_panel_view = AttributesPanelView(
            frame=self.attributes_panel_frame,
            panel_color=self.program_theme["attributes_panel"]["color"],
            widget_color=self.program_theme["attributes_panel"]["widget_color"],
            text_color=self.program_theme["attributes_panel"]["text_color"],
            on_attribute_changed_callback=self._on_attribute_changed
        )

        #create AttributesPanelController to provide refresh/clear API and to compute spinbox limits--------------------
        self.attributes_panel_controller = AttributesPanelController(
            attribute_panel_view=self.attributes_panel_view,
            canvas_width=self.app_state.project.width,
            canvas_height=self.app_state.project.height
        )

        #create ToolbarView to provide the API for building the toolbar-------------------------------------------------
        self.toolbar_view = ToolbarView(
            parent=self.top,
            height=self.constants["toolbar_height"],
            toolbar_color=self.program_theme["toolbar"]["bg"],
            button_color=self.program_theme["button"]["bg"],
            button_text_color=self.program_theme["button"]["fg"],
            menu_color=self.program_theme["menu"]["bg"],
            menu_text_color=self.program_theme["menu"]["fg"],
            grid_visible_variable=self.grid_visible_variable
        )

        #create ToolbarController to build the toolbar and wire the events
        self.toolbar_controller = ToolbarController(
            toolbar_view=self.toolbar_view,
            event_router=self.event_router
        )

        self._subscribe_functions_to_events()

        #create toolbar
        self.toolbar_controller.build_toolbar()

        #pack main frame after creating toolbar so toolbar is on top
        self.main_frame.pack(side="top", fill="both", expand=True)

        #bind events to canvas
        self.canvas_controller.bind_events()

        #create context menu (right click) for creating new widgets
        self._add_widget_menu()

        #do full render to create widgets for the existing models in the ProjectDocument and to render grid
        self._do_full_render()

        #subscribe the function "_on_changed_state" as a listener for state changes
        self.app_state.subscribe(self._on_changed_state)

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
            on_close=lambda: self.app_event_bus.emit("app.exit")
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

    #Rendering API------------------------------------------------------------------------------------------------------
    def _on_changed_state(self, state: AppState):
        """respond to AppState mutations by performing full or soft rendering"""
        #re-render entire AppState if structural change happened (widget creation/deletion, grid settings, selection outlines)
        if state.structural_change or len(state.dirty_model_ids) > 10:  #full render may be faster than doing soft render for multiple models
            self._do_full_render()
            return

        #only update dirty models
        for model_id in state.dirty_model_ids:
            self._do_soft_render(model_id)

        #re-render selection outlines if selection changed and refresh attributes panel
        if state.selection_change:
            self._update_attributes_panel_visibility()
            self.selection_controller.render_all_outlines()

    def _do_full_render(self):
        """perform a full re-render of widgets, selection outlines, and grid"""
        call_tracer.log_event(f"full render\n{'#'*150}")
        #render widgets
        self.widget_controller.render_full()

        #render grid
        self.canvas_controller.render_grid()

        #render selection outlines
        self.selection_controller.render_all_outlines()

    def _do_soft_render(self, model_id: str):
        """perform a soft re-render limited to a single updated widget"""
        call_tracer.log_event(f"soft render {model_id}")
        self.widget_controller.render_soft(model_id)
        self.selection_controller.render_outline_for(model_id)

    def _update_attributes_panel_visibility(self):
        """update attributes panel visibility when selection changes"""
        selected_models = self.app_state.selection_currently_selected()
        call_tracer.log_event(f"Selection: {selected_models}")
        call_tracer.log_event(f"Last Selected: {self.app_state.selection_last_selected()}")

        if len(selected_models) == 1:
            model = self.app_state.get_model_from_model_id(next(iter(selected_models)))
            self.attributes_panel_controller.refresh(model)
        else:
            self.attributes_panel_controller.clear()

    #External API-------------------------------------------------------------------------------------------------------
    def is_dirty(self):
        """return True if the project has unsaved changes"""
        return self.state.is_dirty

    def set_clean(self):
        """mark project state as clean (no unsaved changes)"""
        self._set_clean()

    #Event handling (edit actions)--------------------------------------------------------------------------------------
    def _delete(self):
        """delete selected widgets after user confirmation"""
        #prevent concurrent delete calls
        if self.state.is_deleting:
            return

        count = len(self.app_state.selection_currently_selected())

        if count == 0:
            return
        elif count == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count)} selected widgets?"

        self.state.is_deleting = True

        if not messagebox.askyesno("Delete", messagebox_text):
            self.state.is_deleting = False
            return

        self._delete_selected_models()

    def _copy(self):
        """copy selected widgets to clipboard"""
        #clear clipboard
        self.clipboard = []

        #serialize the model of selected widgets into model_data and append it to the clipboard
        selected_models = self.app_state.selection_currently_selected()
        for model_id in selected_models:
            model = self.app_state.get_model_from_model_id(model_id)
            if model is None:
                continue

            model_data = self._serialize_model(model)
            self.clipboard.append(model_data)

    def _paste(self):
        """paste widgets from clipboard"""
        if not self.clipboard:
            return

        #create new widget models from serialized clipboard model_data
        with self.app_state.batch():
            for model_data in self.clipboard:
                widget_type = model_data.get("type")

                if widget_type == "Label":
                    model = LabelWidgetData(**model_data)
                elif widget_type == "Entry":
                    model = EntryWidgetData(**model_data)
                elif widget_type == "Button":
                    model = ButtonWidgetData(**model_data)
                else:
                    continue

                #create id and add to ProjectDocument
                model.create_id(self.app_state.project.id_counters)
                self.app_state.add_widget(model)

        #set AppState to dirty
        self._set_dirty()

    def _cut(self):
        """copy selected widgets to clipboard then delete them"""
        self._copy()
        self._delete_selected_models()

    def _undo(self):
        """undo last command and refresh selection outlines"""
        self.command_stack.undo()
        self._set_dirty()

    def _redo(self):
        """redo last undone command and refresh selection outlines"""
        self.command_stack.redo()
        self._set_dirty()

    #Event handling (widget actions)------------------------------------------------------------------------------------
    def _move(self, dx: int, dy: int):
        """move selected widgets by a delta or preview drag movement"""
        selected_models = self.app_state.selection_currently_selected()

        if not selected_models:
            return

        #calculate clamped delta of all selected widgets so that widgets can't be moved outside the canvas
        selected_widget_ids = set(self.widget_view.get_widget_id_from_model_id(model_id) for model_id in selected_models)
        dx, dy = clamped_delta(
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            self.canvas.bbox(*selected_widget_ids),
            dx, dy
        )

        is_dragging = self.selection_controller.is_dragging()

        if is_dragging and self.state.active_widget_drag_command:
            #moving widgets by dragging
            self.state.active_widget_drag_command.preview_move(dx, dy)
        else:
            #moving widgets with keyboard shortcuts (nudge)
            self.command_stack.execute(
                MoveWidgets(
                    model_ids=selected_models,
                    dx=dx,
                    dy=dy,
                    widget_controller=self.widget_controller
                )
            )

        #refresh attributes panel if only one widget is selected
        if len(selected_models) == 1:
            model = self.app_state.get_model_from_model_id(next(iter(selected_models)))
            self.attributes_panel_view.update_variables_from_model(model)

        #set AppState to dirty
        if not is_dragging:
            self._set_dirty()

    def _start_drag(self):
        """initialize a MoveWidgetsTo command when dragging begins"""
        selected_models = self.app_state.selection_currently_selected()

        #reset active_widget_drag_command if no widgets selected
        if not selected_models:
            self.state.active_widget_drag_command = None
            return

        #create the MoveWidgetsTo command to record original widget positions
        self.state.active_widget_drag_command = MoveWidgetsTo(
            model_ids=selected_models,
            widget_controller=self.widget_controller
        )

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

        #set AppState to dirty
        self._set_dirty()

    def _snap_to_grid(self):
        """align selected widgets to nearest grid positions"""
        selected_models = self.app_state.selection_currently_selected()
        if not selected_models:
            return

        with self.app_state.batch():
            for model_id in selected_models:
                #compute allowed x and y range for the model
                model = self.app_state.get_model_from_model_id(model_id)
                min_x, max_x = allowed_x_range(self.app_state.project.width, model.width, model.anchor)
                min_y, max_y = allowed_y_range(self.app_state.project.height, model.height, model.anchor)

                #find nearest grid step that is still inside the allowed range
                new_x = nearest_in_bounds_grid_step(model.x, self.app_state.project.grid.size, min_x, max_x)
                new_y = nearest_in_bounds_grid_step(model.y, self.app_state.project.grid.size, min_y, max_y)

                #set absolute position via AppState
                self.app_state.move_widget_to(model, new_x, new_y)


        #refresh attributes panel if only one widget is selected
        if len(selected_models) == 1:
            model = self.app_state.get_model_from_model_id(next(iter(selected_models)))
            self.attributes_panel_view.update_variables_from_model(model)

        #set AppState to dirty
        self._set_dirty()

    def _align(self, direction):
        """align selected widgets relative to the last selected widget"""
        selected_models = self.app_state.selection_currently_selected()
        last_selected_model = self.app_state.selection.last_selected_model
        if not selected_models or not last_selected_model:
            return

        reference_widget_bbox = self.widget_view.get_bbox_from_model_id(last_selected_model)

        if not reference_widget_bbox:
            return

        with self.app_state.batch():
            for model_id in selected_models:
                if not model_id == last_selected_model:
                    widget_bbox = self.widget_view.get_bbox_from_model_id(model_id)

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
                    widget_id = self.widget_view.get_widget_id_from_model_id(model_id)
                    dx, dy = clamped_delta(self.canvas.winfo_width(), self.canvas.winfo_height(), self.canvas.bbox(widget_id), dx, dy)

                    #move widget via AppState
                    model = self.app_state.get_model_from_model_id(model_id)
                    self.app_state.move_widget_by(model, dx, dy)

        #set AppState to dirty
        self._set_dirty()

    #Event handling (grid actions)--------------------------------------------------------------------------------------
    def _toggle_grid(self):
        """toggle grid visibility"""
        #flip grid visible variable
        self.grid_visible_variable.set(not self.grid_visible_variable.get())
        #apply grid visible state
        self._apply_grid_from_variable()

    def _change_grid_size(self):
        """prompt for and apply a new grid size"""
        #prompt for new grid size
        new_grid_size = simpledialog.askinteger("Grid size", "Enter new grid size:", minvalue=5, maxvalue=100, parent=self.parent)

        if new_grid_size is None:
            return

        #update grid size in ProjectDocument
        self.app_state.set_grid_size(new_grid_size)

        #set AppState to dirty
        self._set_dirty()

    def _change_grid_color(self):
        """prompt for and apply a new grid color"""
        color = colorchooser.askcolor()[1]

        #abort if user didn't select a color
        if color is None:
            return

        #update grid color in ProjectDocument
        self.app_state.set_grid_color(str(color))

        #set focus back to canvas
        self.canvas.focus_set()

        #set AppState to dirty
        self._set_dirty()

    def _apply_grid_from_variable(self):
        """apply grid visibility state from BooleanVar to AppState"""
        visible = self.grid_visible_variable.get()

        #write current grid visible state to ProjectDocument
        self.app_state.set_grid_visible(visible)

        #set AppState to dirty
        self._set_dirty()

    #Event handling (UI actions)----------------------------------------------------------------------------------------
    def _show_menu(self, event):
        """show the context menu at the mouse position"""
        self.state.last_click_coords = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #Event handling (wiring)--------------------------------------------------------------------------------------------
    def _subscribe_functions_to_events(self):
        """subscribe all functions, that should be called when an event is emitted, to the corresponding event"""
        #menu events
        self.ui_event_bus.subscribe("menu.show", self._show_menu)

        #selection events
        self.ui_event_bus.subscribe("selection.handle_press", self.selection_controller.handle_canvas_press)
        self.ui_event_bus.subscribe("selection.handle_drag", self.selection_controller.handle_canvas_drag)
        self.ui_event_bus.subscribe("selection.handle_release", self.selection_controller.handle_canvas_release)

        #edit events
        self.ui_event_bus.subscribe("edit.cut", self._cut)
        self.ui_event_bus.subscribe("edit.copy", self._copy)
        self.ui_event_bus.subscribe("edit.paste", self._paste)
        self.ui_event_bus.subscribe("edit.undo", self._undo)
        self.ui_event_bus.subscribe("edit.redo", self._redo)

        #widget events
        self.ui_event_bus.subscribe("widget.move", self._move)
        self.ui_event_bus.subscribe("widget.start_drag", self._start_drag)
        self.ui_event_bus.subscribe("widget.end_drag", self._end_drag)
        self.ui_event_bus.subscribe("widget.snap_to_grid", self._snap_to_grid)
        self.ui_event_bus.subscribe("widget.delete", self._delete)
        self.ui_event_bus.subscribe("widget.align.left", lambda: self._align("left"))
        self.ui_event_bus.subscribe("widget.align.right", lambda: self._align("right"))
        self.ui_event_bus.subscribe("widget.align.top", lambda: self._align("top"))
        self.ui_event_bus.subscribe("widget.align.bottom", lambda: self._align("bottom"))
        self.ui_event_bus.subscribe("widget.select_all", self.app_state.selection_select_all)

        #grid events
        self.ui_event_bus.subscribe("grid.toggle", self._toggle_grid)
        self.ui_event_bus.subscribe("grid.apply_variable", self._apply_grid_from_variable)
        self.ui_event_bus.subscribe("grid.change_size", self._change_grid_size)
        self.ui_event_bus.subscribe("grid.change_color", self._change_grid_color)

        #debug events
        self.ui_event_bus.subscribe("debug.toggle_call_tracing", call_tracer.toggle)
        self.ui_event_bus.subscribe("debug.set_dirty", self._set_dirty)
        self.ui_event_bus.subscribe("debug.set_clean", self._set_clean)
        self.ui_event_bus.subscribe("debug.print_widget_count", self._print_widget_count)

        #attribute events
        self.ui_event_bus.subscribe("attribute.changed", self._on_attribute_changed)

    #Domain logic-------------------------------------------------------------------------------------------------------
    def _add_widget(self, widget_type: str, desired_x: int, desired_y: int):
        """create a new widget of the given type at the given coordinates (with clamping)"""
        if widget_type == "Label":
            text = simpledialog.askstring("Label text", "Enter label text:", parent=self.top)
            if text is None:
                return

            bg = self.app_state.project.theme["label"]["bg"]
            fg = self.app_state.project.theme["label"]["fg"]
            model = LabelWidgetData(x=desired_x, y=desired_y, bg=bg, fg=fg, text=text)
        elif widget_type == "Entry":
            bg = self.app_state.project.theme["entry"]["bg"]
            fg = self.app_state.project.theme["entry"]["fg"]
            model = EntryWidgetData(x=desired_x, y=desired_y, bg=bg, fg=fg)
        elif widget_type == "Button":
            text = simpledialog.askstring("Button text", "Enter button text:", parent=self.top)
            if text is None:
                return

            bg = self.app_state.project.theme["button"]["bg"]
            fg = self.app_state.project.theme["button"]["fg"]
            model = ButtonWidgetData(x=desired_x, y=desired_y, bg=bg, fg=fg, text=text)
        else:
            return

        model.create_id(self.app_state.project.id_counters)

        #create a temporary preview widget to measure dimensions and clamp coordinates
        preview_widget, preview_widget_id = self.widget_view.create_preview_widget(model)

        #update widget's text and colors (can influence dimensions)
        if widget_type in ("Label", "Button"):
            preview_widget.config(text=model.text)
        preview_widget.config(bg=model.bg, fg=model.fg)

        #measure the preview widget's dimensions
        preview_widget.update_idletasks()
        widget_width, widget_height = preview_widget.winfo_reqwidth(), preview_widget.winfo_reqheight()

        #calculate clamped x and y to prevent the widget from being created (partially) outside the canvas
        min_x, max_x = allowed_x_range(self.canvas.winfo_width(), widget_width, model.anchor)
        min_y, max_y = allowed_y_range(self.canvas.winfo_height(), widget_height, model.anchor)
        clamped_x = clamp(model.x, min_x, max_x)
        clamped_y = clamp(model.y, min_y, max_y)

        #delete preview widget
        self.canvas.delete(preview_widget_id)   #delete the widget from canvas
        preview_widget.destroy()                #delete the tk widget instance

        #update model
        with self.app_state.batch():
            #update model position
            self.app_state.set_widget_attribute(model, "x", clamped_x)
            self.app_state.set_widget_attribute(model, "y", clamped_y)

            #populate model with dimensions
            self.app_state.set_widget_attribute(model, "width", widget_width)
            self.app_state.set_widget_attribute(model, "height", widget_height)

            #add new model to AppState
            self.app_state.add_widget(model)

        #clear selection
        self.app_state.selection_clear()

        #set AppState to dirty
        self._set_dirty()

    def _delete_selected_models(self):
        with self.app_state.batch():
            for model_id in self.app_state.selection_currently_selected():
                #let WidgetController delete the widget (deletes widget model from ProjectDocument, tk widget from canvas and removes widget from mappings)
                self.widget_controller.delete_widget(model_id)

            #clear selection
            self.app_state.selection_clear()

            #clear deleting flag
            self.state.is_deleting = False

            #set AppState to dirty
            self._set_dirty()

    def _on_attribute_changed(self, model_id: str, attribute: str, value):
        """apply attribute changes coming from the attributes panel to the model"""
        if model_id is None:
            return

        #apply change to the model through WidgetController
        self.widget_controller.update_widget_attribute(model_id, attribute, value)

        #recompute spinbox limits
        model = self.app_state.get_model_from_model_id(model_id)
        if attribute in ("anchor", "width", "height"):
            self.attributes_panel_controller.update_spinbox_limits(model)

        #set AppState to dirty
        self._set_dirty()

    #Internals----------------------------------------------------------------------------------------------------------
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
            command=lambda: self._add_widget("Label", *_pos())
        )
        self.menu.add_command(
            label="Add Entry",
            command=lambda: self._add_widget("Entry", *_pos())
        )
        self.menu.add_command(
            label="Add Button",
            command=lambda: self._add_widget("Button", *_pos())
        )

    def _set_dirty(self):
        """mark project as dirty and update titlebar"""
        self.state.is_dirty = True
        self.titlebar_label.configure(text=self.app_state.project.title + "*")

    def _set_clean(self):
        """mark project as clean and update titlebar"""
        self.state.is_dirty = False
        self.titlebar_label.configure(text=self.app_state.project.title)
        self.titlebar_label.update()

    def _print_widget_count(self):
        print(f"Live widget count: {len(self.canvas.children)}")

    #Helpers------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _serialize_model(model) -> dict:
        #copy the dictionary of attributes from this model
        data = model.__dict__.copy()

        #strip the ID attribute
        data.pop("id", None)
        return data