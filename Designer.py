import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, ttk
from model import ProjectDocument
from view import CanvasView, SelectionView, ToolbarView, WidgetView
from controller import CanvasController, SelectionController, ToolbarController
from components import AttributesPanel
from events import EventBus, EventRouter
from actions import Actions, EditActions, WidgetActions
from commands import CommandStack
from utility import call_tracer, clamp, screen_offset_to_center_window, CustomTitlebar, WidgetType
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
    *Managing incremental rendering in response to AppState mutations
    *Executing domain specific editor logic (widget creation, alignment, snapping)
    *Reflecting dirty state in the window title
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
        self.app_event_bus = app_event_bus          #lives for the entire application lifetime (owned by AppController)
        self.designer_event_bus = EventBus()        #discarded when the Designer window is destroyed
        self.event_router = EventRouter(            #provides a single interface for emitting events and routes events to the correct EventBus
            app_event_bus=self.app_event_bus,
            designer_event_bus=self.designer_event_bus
        )
        #----------------------------------------------------------------------------------------------------------------
        self.app_state = AppState(project_document) #central model mutation engine
        self.command_stack = CommandStack()         #provides undo and redo functionality
        self.clipboard = []                         #stores a copy of the model for every copied widget

        self.grid_visible_variable = tk.BooleanVar(value=self.app_state.project.grid.visible)   #represents grid state from ProjectDocument
        self._last_right_click_coordinates: tuple[int, int] | None = None

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

        #draw boundary around the work area
        self.canvas.create_rectangle(
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
            resolve_widget_to_model=lambda widget_id: self.widget_view.get_model_id_from_widget_id(widget_id),
            event_router=self.event_router
        )

        #create WidgetView to render widget models and store mappings---------------------------------------------------
        self.widget_view = WidgetView(
            canvas=self.canvas
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

        #create ToolbarController to build the toolbar and wire the events----------------------------------------------
        self.toolbar_controller = ToolbarController(
            toolbar_view=self.toolbar_view,
            event_router=self.event_router
        )

        #create EditActions to provide edit semantics (delete, copy, paste, cut, undo and redo)-------------------------
        edit_actions = EditActions(
            app_state=self.app_state,
            command_stack=self.command_stack,
            clipboard=self.clipboard,
            confirm_delete_callback=self._confirm_delete,
            commit_active_attributes_panel_edit_callback=self._commit_active_attributes_panel_edit
        )

        #create WidgetActions to provide widget semantics (nudge, drag, snap to grid, align)---------------------------
        widget_actions = WidgetActions(
            app_state=self.app_state,
            command_stack=self.command_stack,
            measure_preview_widget_callback=self.widget_view.measure_preview_widget
        )

        #create Actions to provide a single access point for all actions------------------------------------------------
        self.actions = Actions(
            edit_actions=edit_actions,
            widget_actions=widget_actions
        )

        self._subscribe_functions_to_events()

        #create toolbar
        self.toolbar_controller.build_toolbar()

        #pack main frame after creating toolbar so toolbar is on top
        self.main_frame.pack(side="top", fill="both", expand=True)

        #bind events to canvas
        self.canvas_controller.bind_events()

        #create context menu (right click) for creating new widgets
        self._create_context_menu()

        #subscribe the function "_on_changed_state" as a listener for state changes
        self.app_state.subscribe(self._on_changed_state)

        self._initial_render()

    def _build_designer_ui(self):
        """construct the full Designer UI layout and its components"""
        self.top = tk.Toplevel(self.parent)
        self.top.wm_minsize(self.constants["window"]["min_width"], self.constants["window"]["min_height"])  #enforces minimum window size

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

        self.main_frame = tk.Frame(                     #hosts work area (column 0) and attributes panel (column 1)
            self.top,
            bg=self.app_state.project.theme["background"]["color"]
        )
        self.main_frame.columnconfigure(0, weight=1)    #work area expands
        self.main_frame.columnconfigure(1, weight=0)    #attributes panel fixed width
        self.main_frame.rowconfigure(0, weight=1)

        self.work_area = tk.Frame(self.main_frame, bg=self.app_state.project.theme["background"]["color"])
        self.work_area.grid(row=0, column=0, sticky="nsew")
        self.work_area.columnconfigure(0, weight=1)
        self.work_area.rowconfigure(0, weight=1)

        self.attributes_panel = AttributesPanel(
            parent=self.main_frame,
            canvas_width=self.app_state.project.width,
            canvas_height=self.app_state.project.height,
            panel_width=self.constants["attributes_panel_width"],
            panel_color=self.program_theme["attributes_panel"]["color"],
            widget_color=self.program_theme["attributes_panel"]["widget_color"],
            text_color=self.program_theme["attributes_panel"]["text_color"],
            on_attribute_panel_edit_callback=self._handle_attribute_panel_edit_phase
        )
        self.attributes_panel.frame.grid(row=0, column=1, sticky="ns")

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
        panel_width = self.constants["attributes_panel_width"]
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

    #Rendering----------------------------------------------------------------------------------------------------------
    def _on_changed_state(self, state: AppState):
        """respond to AppState mutations by performing incremental updates to widgets and selection outlines as well as updating the grid and the attributes panel"""
        if state.is_dirty():
            self.titlebar_label.configure(text=self.app_state.project.title + "*")
        else:
            self.titlebar_label.configure(text=self.app_state.project.title)

        #delete widgets and outlines for removed models
        for model_id in state.get_removed_model_ids():
            self.widget_view.delete_widget_for(model_id)
            self.selection_view.delete_outline_for(model_id)

        #update widgets and outlines for dirty models
        dirty_models = state.get_dirty_models()
        for model in dirty_models:
            self.widget_view.update_widget_for(model)
            if state.selection_contains(model.id):
                self.selection_controller.update_outline_for(model) #controller derives required data from model and AppState

        #show or hide the attributes panel and refresh outlines based on the selection
        if state.selection_change:
            selected_models = state.get_selected_models()
            self.attributes_panel.set_selection(selected_models)
            self.selection_view.clear_all_outlines()
            for model in selected_models:
                self.selection_controller.update_outline_for(model)

        #update grid
        if state.grid_change:
            self.canvas_controller.render_grid()

        #refresh attributes panel if the single selected model changed
        if len(dirty_models) == 1:
            dirty_model = dirty_models[0]
            selected_models = state.get_selected_models()

            if len(selected_models) == 1 and selected_models[0].id == dirty_model.id:   #prevents undo and redo from refreshing the attributes panel with values from an unselected dirty model
                self.attributes_panel.refresh_from_model(dirty_model)

    def _initial_render(self):
        for model in self.app_state.get_all_models():
            self.widget_view.update_widget_for(model)
        self.canvas_controller.render_grid()

    #Grid actions-------------------------------------------------------------------------------------------------------
    def _toggle_grid(self):
        """toggle grid visibility"""
        self.grid_visible_variable.set(not self.grid_visible_variable.get())
        self._apply_grid_from_variable()

    def _change_grid_size(self):
        """prompt for and apply a new grid size"""
        #prompt for new grid size
        new_grid_size = simpledialog.askinteger(
            "Grid size",
            "Enter new grid size:",
            minvalue=5,
            maxvalue=100,
            parent=self.top
        )
        if new_grid_size is None:
            return

        #update grid size in ProjectDocument
        self.app_state.set_grid_size(new_grid_size)

    def _change_grid_color(self):
        """prompt for and apply a new grid color"""
        color = colorchooser.askcolor(parent=self.top)[1]

        #abort if user didn't select a color
        if color is None:
            return

        #update grid color in ProjectDocument
        self.app_state.set_grid_color(str(color))

        #set focus back to canvas
        self.canvas.focus_set()

    def _apply_grid_from_variable(self):
        """apply grid visibility state from BooleanVar to AppState"""
        visible = self.grid_visible_variable.get()

        #write current grid visible state to ProjectDocument
        self.app_state.set_grid_visible(visible)

    #UI actions---------------------------------------------------------------------------------------------------------
    def _show_menu(self, event):
        """show the context menu at the mouse position"""
        self._last_right_click_coordinates = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #Wiring-------------------------------------------------------------------------------------------------------------
    def _subscribe_functions_to_events(self):
        """subscribe all functions, that should be called when an event is emitted, to the corresponding event"""
        #menu events
        self.designer_event_bus.subscribe("menu.show", self._show_menu)

        #selection events
        self.designer_event_bus.subscribe("selection.handle_press", self.selection_controller.handle_canvas_press)
        self.designer_event_bus.subscribe("selection.handle_drag", self.selection_controller.handle_canvas_drag)
        self.designer_event_bus.subscribe("selection.handle_release", self.selection_controller.handle_canvas_release)

        #edit events
        self.designer_event_bus.subscribe("edit.delete", self.actions.edit.delete)
        self.designer_event_bus.subscribe("edit.copy", self.actions.edit.copy)
        self.designer_event_bus.subscribe("edit.paste", self.actions.edit.paste)
        self.designer_event_bus.subscribe("edit.cut", self.actions.edit.cut)
        self.designer_event_bus.subscribe("edit.undo", self.actions.edit.undo)
        self.designer_event_bus.subscribe("edit.redo", self.actions.edit.redo)

        #widget events
        self.designer_event_bus.subscribe("widget.nudge", self.actions.widget.nudge)
        self.designer_event_bus.subscribe("widget.snap_to_grid", self.actions.widget.snap_to_grid)
        self.designer_event_bus.subscribe("widget.align", self.actions.widget.align)
        self.designer_event_bus.subscribe("widget.select_all", self.app_state.selection_select_all)

        #widget drag lifecycle events
        self.designer_event_bus.subscribe("widget.drag.start", self.actions.widget.start_drag)
        self.designer_event_bus.subscribe("widget.drag.apply_delta", self.actions.widget.apply_drag_delta)
        self.designer_event_bus.subscribe("widget.drag.commit", self.actions.widget.commit_drag)

        #widget edit lifecycle events
        self.designer_event_bus.subscribe("widget.edit.start", self.actions.widget.start_edit)
        self.designer_event_bus.subscribe("widget.edit.apply_change", self.actions.widget.apply_attribute_change)
        self.designer_event_bus.subscribe("widget.edit.commit", self.actions.widget.commit_edit)

        #grid events
        self.designer_event_bus.subscribe("grid.toggle", self._toggle_grid)
        self.designer_event_bus.subscribe("grid.apply_variable", self._apply_grid_from_variable)
        self.designer_event_bus.subscribe("grid.change_size", self._change_grid_size)
        self.designer_event_bus.subscribe("grid.change_color", self._change_grid_color)

        #debug events
        self.designer_event_bus.subscribe("debug.toggle_call_tracing", call_tracer.toggle)
        self.designer_event_bus.subscribe("debug.print_widget_count", self._print_widget_count)
        self.designer_event_bus.subscribe("debug.print_clipboard", self._print_clipboard)
        self.designer_event_bus.subscribe("debug.print_command_stack", self._print_command_stack)
        self.designer_event_bus.subscribe("debug.print_selection", self._print_selection)
        self.designer_event_bus.subscribe("debug.print_bounding_boxes", self._print_bounding_boxes)
        self.designer_event_bus.subscribe("debug.print_id_counters", self._print_id_counters)

    #Domain logic-------------------------------------------------------------------------------------------------------
    def _request_add_widget_from_context_menu(self, widget_type: WidgetType):
        """collect required widget specific input and request widget creation at the last right click position"""
        text = None

        if widget_type == WidgetType.LABEL:
            text = simpledialog.askstring("Label text", "Enter label text:", parent=self.top)
            if text is None:
                return
        elif widget_type == WidgetType.BUTTON:
            text = simpledialog.askstring("Button text", "Enter button text:", parent=self.top)
            if text is None:
                return

        self.actions.widget.add(
            widget_type=widget_type,
            coordinates=self._last_right_click_coordinates,
            text=text
        )

    def _handle_attribute_panel_edit_phase(self, phase: str, **kwargs) -> None:
        """handle an attributes panel edit phase by emitting the corresponding widget edit lifecycle event"""
        if phase == "start":
            self.event_router.emit("widget.edit.start")
        elif phase == "apply_change":
            self.event_router.emit("widget.edit.apply_change", **kwargs)
        elif phase == "commit":
            self.event_router.emit("widget.edit.commit")
        else:
            raise ValueError(f"Designer - attributes panel edit failed: unsupported edit phase \"{phase}\"")

    def _commit_active_attributes_panel_edit(self) -> None:
        """commit the active attributes panel edit if one is in progress"""
        self.attributes_panel.commit_active_edit()

    #Internals----------------------------------------------------------------------------------------------------------
    def _create_context_menu(self):
        """create the context menu for adding widgets"""
        self.menu = tk.Menu(
            self.top,
            bg=self.program_theme["toolbar"]["bg"],
            fg=self.program_theme["toolbar"]["fg"],
            tearoff=0
        )

        self.menu.add_command(
            label="Add Label",
            command=lambda: self._request_add_widget_from_context_menu(WidgetType.LABEL)
        )
        self.menu.add_command(
            label="Add Entry",
            command=lambda: self._request_add_widget_from_context_menu(WidgetType.ENTRY)
        )
        self.menu.add_command(
            label="Add Button",
            command=lambda: self._request_add_widget_from_context_menu(WidgetType.BUTTON)
        )

    def _confirm_delete(self, count: int) -> bool:
        """prompt user to confirm the deletion"""
        if count == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count)} selected widgets?"

        return messagebox.askyesno(
            "Delete",
            messagebox_text,
            parent=self.top     #disables interaction with the parent (Designer) while the messagebox is shown
        )

    def _print_widget_count(self):
        print("#"*150)
        print(f"Live widget count: {len(self.canvas.children)}")

    def _print_clipboard(self):
        print("#"*150)
        print(f"Clipboard:")
        for model_data in self.clipboard:
            print(f"{model_data}")

    def _print_command_stack(self):
        print("#"*150)
        print(f"Command stack:")
        print(self.command_stack)

    def _print_selection(self):
        selected_models = self.app_state.get_selected_models()
        print("#"*150)
        print(f"Selection:")
        print(f"Selected model IDs: {[model.id for model in selected_models]}")
        print(f"Last selected model ID: {self.app_state.get_last_selected_model_id()}")

    def _print_bounding_boxes(self):
        print("#"*150)
        print(f"Model bounding boxes:")
        for model in self.app_state.get_all_models():
            bbox = self.app_state.get_model_bounding_box(model)
            print(f"{model.id}:\t{bbox}")

    def _print_id_counters(self):
        print("#"*150)
        print(f"ID counters:")
        print(self.app_state.project.id_counters)
