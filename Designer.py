import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, ttk

from actions import Actions, EditActions, WidgetActions
from commands import CommandStack
from components import AttributesPanel
from controller import CanvasController, ToolbarController
from events import EventBus, EventRouter
from model import ProjectDocument
from utility import call_tracer, clamp, screen_offset_to_center_window, CustomTitlebar, WidgetType, CONSTANTS
from view import CanvasView, SelectionView, ToolbarView, WidgetView

from AppState import AppState


class Designer:
    """Coordinates events, actions, application state and rendering."""
    def __init__(
        self,
        parent: tk.Tk,
        project_document: ProjectDocument,
        program_theme: dict[str, dict[str, str]],
        app_event_bus: EventBus
    ) -> None:
        self._parent: tk.Tk = parent
        self._program_theme: dict[str, dict[str, str]] = program_theme

        #Event system---------------------------------------------------------------------------------------------------
        self._app_event_bus: EventBus = app_event_bus   #lives for the entire application lifetime (owned by AppController)
        self._designer_event_bus: EventBus = EventBus() #discarded when the Designer window is destroyed
        self._event_router: EventRouter = EventRouter(  #provides a single interface for emitting events
            app_event_bus=self._app_event_bus,
            designer_event_bus=self._designer_event_bus
        )

        #Application state----------------------------------------------------------------------------------------------
        self.app_state: AppState = AppState(
            project_document=project_document
        )
        self.app_state.subscribe(self._on_changed_state)

        self._command_stack: CommandStack = CommandStack()
        self._clipboard: list[dict[str, str | int]] = []
        self._grid_visible_variable: tk.BooleanVar = tk.BooleanVar(value=self.app_state.project.grid.visible)
        self._last_right_click_coordinates: tuple[int, int] | None = None

        #UI construction------------------------------------------------------------------------------------------------
        self._build_designer_ui()
        self._create_context_menu()

        #Views----------------------------------------------------------------------------------------------------------
        self._canvas_view: CanvasView = CanvasView(
            parent=self._viewer,
            canvas_width=self.app_state.project.width,
            canvas_height=self.app_state.project.height,
            background_color=self.app_state.project.theme["background"]["color"],
            boundary_color=self._program_theme["selection"]["color"]
        )
        self._canvas: tk.Canvas = self._canvas_view.canvas
        self._viewer.create_window(     #embeds inner canvas into the scrollable viewer
            0, 0,
            window=self._canvas,
            anchor="nw"
        )

        self._selection_view: SelectionView = SelectionView(
            canvas=self._canvas,
            selection_color=self._program_theme["selection"]["color"],
            last_selected_color=self._program_theme["selection"]["last_selected_color"],
            selection_width=CONSTANTS["selection"]["width"],
            selection_dash=CONSTANTS["selection"]["dash"],
            selection_padding=CONSTANTS["selection"]["padding"]
        )

        self._toolbar_view: ToolbarView = ToolbarView(
            parent=self.top,
            height=CONSTANTS["toolbar_height"],
            toolbar_color=self._program_theme["toolbar"]["bg"],
            button_color=self._program_theme["button"]["bg"],
            button_text_color=self._program_theme["button"]["fg"],
            menu_color=self._program_theme["menu"]["bg"],
            menu_text_color=self._program_theme["menu"]["fg"],
            grid_visible_variable=self._grid_visible_variable
        )

        self._widget_view: WidgetView = WidgetView(
            canvas=self._canvas
        )

        #Controllers----------------------------------------------------------------------------------------------------
        self._canvas_controller: CanvasController = CanvasController(
            canvas=self._canvas,
            event_router=self._event_router,
            app_state=self.app_state,
            resolve_canvas_item_id_to_widget_id=lambda canvas_item_id: self._widget_view.get_widget_id_from_canvas_item_id(canvas_item_id),
        )

        self._toolbar_controller: ToolbarController = ToolbarController(
            toolbar_view=self._toolbar_view,
            event_router=self._event_router
        )
        self._toolbar_controller.build_toolbar()
        self._main_frame.pack(side="top", fill="both", expand=True)

        #Actions--------------------------------------------------------------------------------------------------------
        edit_actions: EditActions = EditActions(
            app_state=self.app_state,
            command_stack=self._command_stack,
            clipboard=self._clipboard,
            confirm_delete_callback=self._confirm_delete,
            commit_active_attributes_panel_edit_callback=self._commit_active_attributes_panel_edit
        )

        widget_actions: WidgetActions = WidgetActions(
            app_state=self.app_state,
            command_stack=self._command_stack,
            measure_preview_tk_widget_callback=self._widget_view.measure_preview_tk_widget
        )

        self._actions: Actions = Actions(
            edit_actions=edit_actions,
            widget_actions=widget_actions
        )

        #Event wiring---------------------------------------------------------------------------------------------------
        self._subscribe_functions_to_events()

        #Startup--------------------------------------------------------------------------------------------------------
        self._initial_render()

    def _build_designer_ui(
        self
    ) -> None:
        """Construct the designer UI layout and its components."""
        self.top: tk.Toplevel = tk.Toplevel(self._parent)
        self.top.wm_minsize(
            CONSTANTS["window"]["min_width"],
            CONSTANTS["window"]["min_height"]
        )

        titlebar = CustomTitlebar(
            parent=self.top,
            title=self.app_state.project.title,
            height=CONSTANTS["titlebar_height"],
            bg_color=self._program_theme["titlebar"]["bg"],
            fg_color=self._program_theme["titlebar"]["fg"],
            icon_path=self.app_state.project.icon_path,
            on_close=lambda: self._event_router.emit("app.exit")
        )
        titlebar.frame.pack(fill="x")
        self._titlebar_label: tk.Label = titlebar.label

        self._main_frame: tk.Frame = tk.Frame(           #hosts work area (column 0) and attributes panel (column 1)
            self.top,
            bg=self.app_state.project.theme["background"]["color"]
        )
        self._main_frame.columnconfigure(0, weight=1)    #work area expands
        self._main_frame.columnconfigure(1, weight=0)    #attributes panel fixed width
        self._main_frame.rowconfigure(0, weight=1)

        self._work_area: tk.Frame = tk.Frame(
            master=self._main_frame,
            bg=self.app_state.project.theme["background"]["color"]
        )
        self._work_area.grid(row=0, column=0, sticky="nsew")
        self._work_area.columnconfigure(0, weight=1)
        self._work_area.rowconfigure(0, weight=1)

        self._attributes_panel: AttributesPanel = AttributesPanel(
            parent=self._main_frame,
            canvas_width=self.app_state.project.width,
            canvas_height=self.app_state.project.height,
            panel_width=CONSTANTS["attributes_panel_width"],
            panel_color=self._program_theme["attributes_panel"]["color"],
            widget_color=self._program_theme["attributes_panel"]["widget_color"],
            text_color=self._program_theme["attributes_panel"]["text_color"],
            on_attribute_panel_edit_callback=self._handle_attribute_panel_edit_phase
        )
        self._attributes_panel.frame.grid(row=0, column=1, sticky="ns")

        self._viewer: tk.Canvas = tk.Canvas(
            master=self._work_area,
            bg=self.app_state.project.theme["background"]["color"],
            highlightthickness=0
        )
        self._viewer.grid(row=0, column=0, sticky="nsew")
        self._bind_mousewheel(self.top)

        #create scrollbars
        self._configure_scrollbar_style()
        self._vertical_scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self._work_area,
            orient="vertical",
            command=self._viewer.yview,
            style="Designer.Vertical.TScrollbar"
        )
        self._horizontal_scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self._work_area,
            orient="horizontal",
            command=self._viewer.xview,
            style="Designer.Horizontal.TScrollbar"
        )
        self._viewer.configure(
            yscrollcommand=self._vertical_scrollbar.set,
            xscrollcommand=self._horizontal_scrollbar.set
        )

        window_width, window_height = self._compute_initial_window_dimensions()
        self.top.geometry(f"{window_width}x{window_height}")

        self._viewer.bind("<Configure>", lambda e: self._refresh_scrollbars())
        self._center_window()

    def _compute_initial_window_dimensions(
        self
    ) -> tuple[int, int]:
        """Compute initial designer window size based on canvas and constraints."""
        self.top.update_idletasks()     #ensures geometry is up-to-date

        requested_canvas_width = self.app_state.project.width
        requested_canvas_height = self.app_state.project.height

        panel_width = CONSTANTS["attributes_panel_width"]
        titlebar_height = CONSTANTS["titlebar_height"]
        toolbar_height = CONSTANTS["toolbar_height"]

        vertical_scrollbar_thickness = self._vertical_scrollbar.winfo_reqwidth()
        horizontal_scrollbar_thickness = self._horizontal_scrollbar.winfo_reqheight()

        minimum_window_width = CONSTANTS["window"]["min_width"]
        maximum_window_width = CONSTANTS["window"]["max_width"]
        minimum_window_height = CONSTANTS["window"]["min_height"]
        maximum_window_height = CONSTANTS["window"]["max_height"]

        required_window_width = requested_canvas_width + panel_width
        required_window_height = requested_canvas_height + toolbar_height + titlebar_height
        actual_window_width = clamp(required_window_width, minimum_window_width, maximum_window_width)
        actual_window_height = clamp(required_window_height, minimum_window_height, maximum_window_height)

        viewport_width = max(0, actual_window_width - panel_width)
        viewport_height = max(0, actual_window_height - (toolbar_height + titlebar_height))
        need_horizontal_scrollbar = requested_canvas_width > viewport_width
        need_vertical_scrollbar = requested_canvas_height > viewport_height

        window_width_new, window_height_new = actual_window_width, actual_window_height

        for _ in range(2):  #one scrollbar can make the other one necessary
            if need_vertical_scrollbar:
                window_width_new = clamp(actual_window_width + vertical_scrollbar_thickness, minimum_window_width, maximum_window_width)
                viewport_width = max(0, window_width_new - panel_width)
                need_horizontal_scrollbar = requested_canvas_width > viewport_width

            if need_horizontal_scrollbar:
                window_height_new = clamp(actual_window_height + horizontal_scrollbar_thickness, minimum_window_height, maximum_window_height)
                viewport_height = max(0, window_height_new - (toolbar_height + titlebar_height))
                need_vertical_scrollbar = requested_canvas_height > viewport_height

        return window_width_new, window_height_new

    def _configure_scrollbar_style(
        self
    ) -> None:
        """Configure custom scrollbar styles."""
        style = ttk.Style(self.top)
        style.theme_use("default")  #allows colors
        style.configure(
            "Designer.Vertical.TScrollbar",
            troughcolor=self._program_theme["scrollbar"]["trough_color"],
            background=self._program_theme["scrollbar"]["background_color"],
            arrowcolor=self._program_theme["scrollbar"]["arrow_color"],
            bordercolor=self._program_theme["scrollbar"]["border_color"]
        )
        style.configure(
            "Designer.Horizontal.TScrollbar",
            troughcolor=self._program_theme["scrollbar"]["trough_color"],
            background=self._program_theme["scrollbar"]["background_color"],
            arrowcolor=self._program_theme["scrollbar"]["arrow_color"],
            bordercolor=self._program_theme["scrollbar"]["border_color"]
        )

    def _refresh_scrollbars(
        self
    ) -> None:
        """Compute which scrollbars should be visible and update layout."""
        self.top.update_idletasks()     #ensures geometry is up-to-date

        canvas_width = self.app_state.project.width
        canvas_height = self.app_state.project.height

        vertical_scrollbar_thickness = self._vertical_scrollbar.winfo_reqwidth()
        horizontal_scrollbar_thickness = self._horizontal_scrollbar.winfo_reqheight()

        viewport_width = self._work_area.winfo_width()
        viewport_height = self._work_area.winfo_height()

        need_horizontal_scrollbar = canvas_width > viewport_width
        need_vertical_scrollbar = canvas_height > viewport_height

        for _ in range(2):  #one scrollbar can make the other one necessary
            if need_vertical_scrollbar:
                viewport_width_new = viewport_width - vertical_scrollbar_thickness
                need_horizontal_scrollbar = canvas_width > viewport_width_new

            if need_horizontal_scrollbar:
                viewport_height_new = viewport_height - horizontal_scrollbar_thickness
                need_vertical_scrollbar = canvas_height > viewport_height_new

        if need_vertical_scrollbar:
            self._vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        else:
            self._vertical_scrollbar.grid_remove()

        if need_horizontal_scrollbar:
            self._horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            self._horizontal_scrollbar.grid_remove()

        self._viewer.configure(scrollregion=(0, 0, canvas_width, canvas_height))

    def _get_pointer_coordinates(
        self
    ) -> tuple[int, int] | None:
        """Return the current pointer coordinates relative to the canvas or None if the pointer is outside the canvas."""
        x = self._canvas.winfo_pointerx() - self._canvas.winfo_rootx()
        y = self._canvas.winfo_pointery() - self._canvas.winfo_rooty()

        if x < 0 or x > self._canvas.winfo_width():
            return None
        if y < 0 or y > self._canvas.winfo_height():
            return None
        return x, y

    def _bind_mousewheel(
        self,
        tk_widget: tk.BaseWidget
    ) -> None:
        """Bind mousewheel scrolling behavior to the given widget."""
        tk_widget.bind("<MouseWheel>", lambda e: self._viewer.yview_scroll(-1 * int(e.delta / 120), "units"))
        tk_widget.bind("<Shift-MouseWheel>", lambda e: self._viewer.xview_scroll(-1 * int(e.delta / 120), "units"))

    def _center_window(
        self
    ) -> None:
        """Center the designer window on screen."""
        self.top.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self.top.winfo_screenwidth(),
            self.top.winfo_screenheight(),
            self.top.winfo_width(),
            self.top.winfo_height()
        )
        self.top.geometry(f"+{x_offset}+{y_offset}")

    #Rendering----------------------------------------------------------------------------------------------------------
    def _on_changed_state(
        self,
        state: AppState
    ) -> None:
        """Render incremental UI updates from AppState state change notification."""
        if state.is_dirty():
            self._titlebar_label.configure(text=self.app_state.project.title + "*")
        else:
            self._titlebar_label.configure(text=self.app_state.project.title)

        #delete Tk widgets and outlines for removed widgets
        for widget_id in state.get_removed_widget_ids():
            self._widget_view.delete_tk_widget_for(widget_id)
            self._selection_view.delete_outline_for(widget_id)

        #render Tk widgets and outlines for dirty widgets
        dirty_widgets = state.get_dirty_widgets()
        for widget in dirty_widgets:
            self._widget_view.render_tk_widget_for(widget)
            if state.selection_contains(widget.id):
                self._selection_view.render_outline_for(
                    widget_id=widget.id,
                    bounding_box=self.app_state.get_widget_bounding_box(widget),
                    is_last_selected=widget.id == self.app_state.get_last_selected_widget_id()
                )

        #show or hide the attributes panel and refresh outlines based on the selection
        if state.selection_change:
            selected_widgets = state.get_selected_widgets()
            self._attributes_panel.set_selection(selected_widgets)
            self._selection_view.clear_all_outlines()
            for widget in selected_widgets:
                self._selection_view.render_outline_for(
                    widget_id=widget.id,
                    bounding_box=self.app_state.get_widget_bounding_box(widget),
                    is_last_selected=widget.id == self.app_state.get_last_selected_widget_id()
                )

        #render grid
        if state.grid_change:
            self._canvas_view.render_grid(
                grid_size=self.app_state.project.grid.size,
                grid_color=self.app_state.project.grid.color,
                grid_visible=self.app_state.project.grid.visible
            )

        #refresh attributes panel if the single selected widget changed
        if len(dirty_widgets) == 1:
            dirty_widget = dirty_widgets[0]
            selected_widgets = state.get_selected_widgets()

            if len(selected_widgets) == 1 and selected_widgets[0].id == dirty_widget.id:    #prevents undo and redo from refreshing the attributes panel with values from an unselected dirty widget
                self._attributes_panel.refresh_from_widget(dirty_widget)

    def _initial_render(
        self
    ) -> None:
        """Create Tk widgets for all domain widgets and render the grid."""
        for widget in self.app_state.get_all_widgets():
            self._widget_view.render_tk_widget_for(widget)

        self._canvas_view.render_grid(
            grid_size=self.app_state.project.grid.size,
            grid_color=self.app_state.project.grid.color,
            grid_visible=self.app_state.project.grid.visible
        )

    #Grid actions-------------------------------------------------------------------------------------------------------
    def _toggle_grid(
        self
    ) -> None:
        """Toggle grid visibility."""
        self._grid_visible_variable.set(not self._grid_visible_variable.get())
        self._apply_grid_from_variable()

    def _change_grid_size(
        self
    ) -> None:
        """Prompt for and apply a new grid size."""
        new_grid_size = simpledialog.askinteger(
            "Grid size",
            "Enter new grid size:",
            minvalue=CONSTANTS["grid"]["min_size"],
            maxvalue=CONSTANTS["grid"]["max_size"],
            parent=self.top
        )

        if new_grid_size is None:
            return

        self.app_state.set_grid_size(new_grid_size)

    def _change_grid_color(
        self
    ) -> None:
        """Prompt for and apply a new grid color."""
        color = colorchooser.askcolor(parent=self.top)[1]

        if color is None:
            return

        self.app_state.set_grid_color(str(color))
        self._canvas.focus_set()

    def _apply_grid_from_variable(
        self
    ) -> None:
        """Apply the current grid visibility state."""
        visible = self._grid_visible_variable.get()
        self.app_state.set_grid_visible(visible)

    #UI actions---------------------------------------------------------------------------------------------------------
    def _show_menu(
        self,
        tk_event: tk.Event
    ) -> None:
        """Show the context menu at the current mouse position."""
        self._last_right_click_coordinates = tk_event.x, tk_event.y
        self._menu.post(tk_event.x_root, tk_event.y_root)

    #Wiring-------------------------------------------------------------------------------------------------------------
    def _subscribe_functions_to_events(
        self
    ) -> None:
        """Subscribe functions to their corresponding events."""
        #menu events
        self._designer_event_bus.subscribe("menu.show", self._show_menu)

        #selection events
        self._designer_event_bus.subscribe("selection.rectangle.start", lambda x1, y1: self._selection_view.render_selection_rectangle(x1, y1, x1, y1))
        self._designer_event_bus.subscribe("selection.rectangle.update", lambda x1, y1, x2, y2: self._selection_view.render_selection_rectangle(x1, y1, x2, y2))
        self._designer_event_bus.subscribe("selection.rectangle.end", self._selection_view.delete_selection_rectangle)

        #edit events
        self._designer_event_bus.subscribe("edit.delete", self._actions.edit.delete)
        self._designer_event_bus.subscribe("edit.copy", self._actions.edit.copy)
        self._designer_event_bus.subscribe("edit.paste", lambda: self._actions.edit.paste(self._get_pointer_coordinates()))
        self._designer_event_bus.subscribe("edit.cut", self._actions.edit.cut)
        self._designer_event_bus.subscribe("edit.undo", self._actions.edit.undo)
        self._designer_event_bus.subscribe("edit.redo", self._actions.edit.redo)

        #widget events
        self._designer_event_bus.subscribe("widget.nudge", self._actions.widget.nudge)
        self._designer_event_bus.subscribe("widget.snap_to_grid", self._actions.widget.snap_to_grid)
        self._designer_event_bus.subscribe("widget.align", self._actions.widget.align)
        self._designer_event_bus.subscribe("widget.select_all", self.app_state.selection_select_all)

        #widget drag lifecycle events
        self._designer_event_bus.subscribe("widget.drag.start", self._actions.widget.start_drag)
        self._designer_event_bus.subscribe("widget.drag.update", self._actions.widget.update_drag)
        self._designer_event_bus.subscribe("widget.drag.end", self._actions.widget.end_drag)

        #widget edit lifecycle events
        self._designer_event_bus.subscribe("widget.edit.start", self._actions.widget.start_edit)
        self._designer_event_bus.subscribe("widget.edit.apply_change", self._actions.widget.apply_attribute_change)
        self._designer_event_bus.subscribe("widget.edit.commit", self._actions.widget.commit_edit)

        #grid events
        self._designer_event_bus.subscribe("grid.toggle", self._toggle_grid)
        self._designer_event_bus.subscribe("grid.apply_variable", self._apply_grid_from_variable)
        self._designer_event_bus.subscribe("grid.change_size", self._change_grid_size)
        self._designer_event_bus.subscribe("grid.change_color", self._change_grid_color)

        #debug events
        self._designer_event_bus.subscribe("debug.toggle_call_tracing", call_tracer.toggle)
        self._designer_event_bus.subscribe("debug.print_widget_count", self._print_widget_count)
        self._designer_event_bus.subscribe("debug.print_clipboard", self._print_clipboard)
        self._designer_event_bus.subscribe("debug.print_command_stack", self._print_command_stack)
        self._designer_event_bus.subscribe("debug.print_selection", self._print_selection)
        self._designer_event_bus.subscribe("debug.print_bounding_boxes", self._print_bounding_boxes)
        self._designer_event_bus.subscribe("debug.print_id_counters", self._print_id_counters)

    #Domain logic-------------------------------------------------------------------------------------------------------
    def _request_add_widget_from_context_menu(
        self,
        widget_type: WidgetType
    ) -> None:
        """Collect required widget specific input and request widget creation at the last right click position."""
        text = None

        if widget_type == WidgetType.LABEL:
            text = simpledialog.askstring("Label text", "Enter label text:", parent=self.top)
            if text is None:
                return
        elif widget_type == WidgetType.BUTTON:
            text = simpledialog.askstring("Button text", "Enter button text:", parent=self.top)
            if text is None:
                return

        self._actions.widget.add(
            widget_type=widget_type,
            coordinates=self._last_right_click_coordinates,
            text=text
        )

    def _handle_attribute_panel_edit_phase(
        self,
        phase: str,
        **kwargs: str | int
    ) -> None:
        """Handle an attributes panel edit phase by emitting the corresponding widget edit lifecycle event."""
        if phase == "start":
            self._event_router.emit("widget.edit.start")
        elif phase == "apply_change":
            self._event_router.emit("widget.edit.apply_change", **kwargs)
        elif phase == "commit":
            self._event_router.emit("widget.edit.commit")
        else:
            raise ValueError(f"Designer - attributes panel edit failed: unsupported edit phase \"{phase}\"")

    def _commit_active_attributes_panel_edit(
        self
    ) -> None:
        """Commit the active attributes panel edit if one is in progress."""
        self._attributes_panel.commit_active_edit()

    #Internals----------------------------------------------------------------------------------------------------------
    def _create_context_menu(
        self
    ) -> None:
        """Create the context menu for adding widgets."""
        self._menu: tk.Menu = tk.Menu(
            self.top,
            bg=self._program_theme["toolbar"]["bg"],
            fg=self._program_theme["toolbar"]["fg"],
            tearoff=0
        )

        self._menu.add_command(
            label="Add Label",
            command=lambda: self._request_add_widget_from_context_menu(WidgetType.LABEL)
        )
        self._menu.add_command(
            label="Add Entry",
            command=lambda: self._request_add_widget_from_context_menu(WidgetType.ENTRY)
        )
        self._menu.add_command(
            label="Add Button",
            command=lambda: self._request_add_widget_from_context_menu(WidgetType.BUTTON)
        )

    def _confirm_delete(
        self,
        count: int
    ) -> bool:
        """Prompt for delete confirmation."""
        if count == 1:
            messagebox_text = "Delete selected widget?"
        else:
            messagebox_text = f"Delete {str(count)} selected widgets?"

        return messagebox.askyesno(
            "Delete",
            messagebox_text,
            parent=self.top     #disables interaction with the parent (Designer) while the messagebox is shown
        )

    def _print_widget_count(
        self
    ) -> None:
        """Print the live widget count to the console."""
        print("#"*150)
        print(f"Live widget count: {len(self._canvas.children)}")

    def _print_clipboard(
        self
    ) -> None:
        """Print the clipboard contents to the console."""
        print("#"*150)
        print(f"Clipboard:")
        for widget_data in self._clipboard:
            print(f"{widget_data}")

    def _print_command_stack(
        self
    ) -> None:
        """Print the command stack to the console."""
        print("#"*150)
        print(f"Command stack:")
        print(self._command_stack)

    def _print_selection(
        self
    ) -> None:
        """Print the current selection to the console."""
        selected_widgets = self.app_state.get_selected_widgets()
        print("#"*150)
        print(f"Selection:")
        print(f"Selected widget IDs: {[widget.id for widget in selected_widgets]}")
        print(f"Last selected widget ID: {self.app_state.get_last_selected_widget_id()}")

    def _print_bounding_boxes(
        self
    ) -> None:
        """Print the bounding boxes of all widgets to the console."""
        print("#"*150)
        print(f"Widget bounding boxes:")
        for widget in self.app_state.get_all_widgets():
            bbox = self.app_state.get_widget_bounding_box(widget)
            print(f"{widget.id}:\t{bbox}")

    def _print_id_counters(
        self
    ) -> None:
        """Print the current ID counter values to the console."""
        print("#"*150)
        print(f"ID counters:")
        print(self.app_state.project.id_counters)
