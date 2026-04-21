================================================================================================
Overview / Explanation
================================================================================================
The Tkinter GUI Builder is an advanced, fully interactive, canvas‑based graphical interface designerbuilt on top of Tkinter.
It enables the creation, manipulation, arrangement and configuration of UI widgets inside a pixel‑accurate design space.
The program is architected around a robust MVC (Model‑View‑Controller) system combined with an AppState mutation engine
and an EventBus-driven communication layer.

The core purpose of the application is to provide an intuitive drag‑and‑drop GUI editing environment with:
   *Multi-selection tools
   *Rectangle selection
   *Smooth dragging powered by a threshold + live preview system
   *Dynamic attribute editing via a dedicated attributes panel
   *Undo/redo command stack for both drag and keyboard-based transformations
   *Automatic geometry clamping based on canvas boundaries and widget anchor behavior
   *Custom overrideredirect windows (Designer + Setup Wizard)
   *Scrollable and auto-sizing viewer for very large canvases
   *Theme configurability
   *A clean separation between model state mutation (AppState), business/event logic (Controllers) and drawing/UI layers (Views)

The system is structured into subsystems:  
   *Application entry and controller  
   *Designer (main interface)  
   *MVC subsystems (Canvas, Selection, Widget, Attributes Panel, Toolbar)  
   *Command subsystem (undo/redo)  
   *Model subsystem (ProjectDocument, widget models, grid)  
   *Utility subsystem (geometry helpers, call tracing, icon loading, custom titlebar)  

Through AppState, all model changes are batched and observed by subscribers.
The Designer subscribes to these changes and decides when to soft-render specific widgets or perform a full re-render.
The EventBus allows fully decoupled communication between UI elements, controllers and the Designer.
Widget manipulation (movement, resizing through text updates, deletion) is synchronized between the model and Tkinter widgets in real time.

The result is an editor capable of building Tkinter GUI layouts with precision, consistency and a highly modular architecture suited for extension, debugging and testing.
================================================================================================
Quick Start Guide
================================================================================================
*Run the Application:
   -Launch App.py
   -Tk root window is created
   -AppController initializes and displays the startup window

*Create a New Project:
   -Click "New Project"
   -SetupWizard opens in a child window
   -Enter title, dimensions, theme colors and optionally an icon
   -Press "Launch designer" to open the main Designer

*Open an Existing Project:
   -Click "Open Project"
   -Select a .tkui file
   -Designer loads with all widgets, theme and grid configuration

*Using the Designer:
   -Right‑click → add widgets (Label, Entry, Button)
   -Left‑click → select
   -[Ctrl] + Left‑click → multi-select
   -Drag on widget → move widget (after threshold is exceeded)
   -Drag on empty area → rectangle selection, [Ctrl] = additive
   -Scroll using mouse wheel or scrollbars, [Shift] = horizontal
   -Use toolbar menus for editing, grid configuration, debug tools
   -Modify selected widget attributes in the attributes panel
   -Undo/redo widget movement
   -Snap widgets to grid, align to last-selected widget, delete widgets

*Saving:
   -Save or Save As creates/updates a .tkui file
   -Upon saving, Designer marks the project “clean”
================================================================================================
Module Map
================================================================================================
Application Entry & Controller
--------------------------------------------------------------------------------------
*App.py:
   -Creates the Tk root window
   -Initializes AppController
   -Starts Tk mainloop

*AppController.py:
   -Owns the Tk root window
   -Constructs the startup UI with CustomTitlebar
   -Holds program theme, constants, user theme, save path, last directory
   -Creates and owns the global EventBus:
      >Used for fully decoupled event dispatching
   -Subscribes functions to EventBus events:
      >project.new
      >project.open
      >project.save
      >project.save_as
      >widget.move
      >widget.delete
      >debug.toggle_call_tracing
   -Handles:
      >New Project workflow via SetupWizard
      >Open Project (.tkui)
      >Save / Save As logic
      >Unsaved changes prompts
      >Startup window display/hide behavior
   -Launches the Designer window and injects:
      >ProjectDocument
      >Theme
      >Constants
      >EventBus
--------------------------------------------------------------------------------------
Setup Wizard
--------------------------------------------------------------------------------------
*SetupWizard.py:
   -Displayed when creating a new project
   -CustomTitlebar with draggable frame
   -Collects:
      >Window title
      >Canvas width and height
      >Theme colors for background, labels, entries, buttons
      >Icon path selection
   -Validates width/height using constants (min/max)
   -Live previews of theme elements
   -Creates a ProjectDocument with:
      >Version
      >Title
      >Canvas dimensions
      >Icon
      >GridConfig
      >Theme dictionary
      >Empty widget list
   -On completion:
      >Returns the ProjectDocument to AppController
      >Destroys itself
--------------------------------------------------------------------------------------
Designer - Main Editor
--------------------------------------------------------------------------------------
*Designer.py:
   -Creates the main Designer window using Tk.Toplevel
   -Uses CustomTitlebar
   -Constructs main layout:
      >Toolbar across the top
      >Scrollable viewer containing the canvas
      >Attributes panel on the right
   -Initializes core subsystems:
      >AppState (model mutation engine)
      >DesignerState (dirty/deleting/active drag information)
      >CanvasView + CanvasController
      >SelectionView + SelectionController
      >WidgetView + WidgetController
      >AttributesPanelView + AttributesPanelController
      >ToolbarView + ToolbarController
      >CommandStack for undo/redo
   -Computes initial window dimensions based on:
      >Canvas size
      >UI element sizes
      >Scrollbar thickness
      >Min/max window constraints
   -Manages scrollbars visibility dynamically in response to viewer size
   -Binds mouse wheel events for scrolling
   -Builds context menu for adding widgets
   -Performs:
      >Full render for initial load
      >Soft render for selective widget updates
   -Subscribes to AppState notifications:
      >On structural_change → full re-render
      >On dirty_model_ids update → soft re-render of those widgets
      >On selection_change → update outlines + attributes panel
   -Handles movement, drag lifecycle, deletion, alignment, snap-to-grid
   -Provides attribute change callback to AttributesPanelController
--------------------------------------------------------------------------------------
AppState – Central Model Mutation Engine
--------------------------------------------------------------------------------------
*AppState.py:
   -Stores the ProjectDocument (the complete model)
   -Stores SelectionState
   -Supports batching of edits:
      >Batched changes only notify subscribers once
   -Tracks:
      >Dirty model IDs
      >Structural changes
      >Selection changes
   -Provides APIs:
      >add_widget
      >remove_widget
      >move_widget_to
      >move_widget_by
      >set_widget_attribute
      >set_grid_visible
      >set_grid_size
      >set_grid_color
      >set_title
      >selection_clear
      >selection_toggle
      >selection_select_only
      >selection_select_all
      >apply_rectangle_selection
   -Provides helpers to query models:
      >get_model_from_model_id
      >get_model_coordinates_from_model_id
--------------------------------------------------------------------------------------
EventBus – Decoupled Dispatch System
--------------------------------------------------------------------------------------
*EventBus.py:
   -Maps string event names to lists of subscribers
   -Provides:
      >subscribe(event, handler)
      >unsubscribe(event, handler)
      >emit(event, **kwargs)
   -Used to route:
      >Canvas events → Controller logic
      >Toolbar menu items → Designer actions
      >Widget interactions → movement/drag logic
      >Grid/debug operations → Designer updates
--------------------------------------------------------------------------------------
Models - Project, Widgets, State Objects
--------------------------------------------------------------------------------------
*ProjectDocument.py:
   -Stores:
      >version
      >title
      >width / height
      >icon_path
      >GridConfig
      >theme dictionary
      >widget_models list
   -Serializes/deserializes JSON
   -Restores ID counters for widgets

*GridConfig:
   -Holds grid size, color, visibility

*WidgetModels.py:
   -IdCounters:
      >Manages auto-incrementing widget IDs
   -BaseWidgetData:
      >Holds common widget fields:
         -id
         -x / y
         -bg / fg
         -width / height
         -anchor
   -LabelWidgetData:
      >Adds text attribute
      >Type "Label"
      >create_id() → assigns unique id
   -EntryWidgetData:
      >Type "Entry"
      >create_id()
   -ButtonWidgetData:
      >Adds text attribute
      >Type "Button"
      >create_id()

*DesignerState:
   -Stores:
      >Last click coordinates
      >Drag start coordinates
      >Window coordinates
      >Dirty flag
      >Delete-in-progress flag
      >Active MoveWidgetsTo command

*SelectionState:
   -Stores:
      >Selected model IDs set
      >Last selected model

*RectangleSelectionState:
   -Stores:
      >Is dragging
      >Additive selection flag
      >Drag start coordinates

*WidgetDragState:
   -Stores:
      >Is dragging
      >Drag start coords
      >Last total dx/dy
--------------------------------------------------------------------------------------
Views - Tkinter Rendering Components
--------------------------------------------------------------------------------------
*CanvasView.py:
   -Creates inner drawing canvas
   -Provides:
      >Grid rendering (draw, clear)
      >Storing grid line IDs

*SelectionView.py:
   -Draws:
      >Selection outlines (blue)
      >Last-selected outline (red)
      >Rectangle-selection rectangle
   -Maintains:
      >Outline item IDs per model
      >Current selection rectangle

*WidgetView.py:
   -Creates Tk widgets from models
   -Inserts them into the canvas via create_window
   -Maintains:
      >widget_map
      >model_id → widget_id mapping
      >widget_id → model_id mapping
   -Renders updates:
      >Position
      >Colors
      >Text
      >Anchor
      >Dimensions
   -Creates preview widgets to measure required geometry
   -Deletes widgets when necessary

*AttributesPanelView.py:
   -Renders the Attributes Panel
   -Builds rows of labels, entries, spinboxes, color previews, anchor selector
   -Binds tk.Variable updates to callback
   -Applies spinbox min/max updates
   -Provides silent-update mode
   -Stores:
      >Active model ID
      >Spinboxes dict
      >Variables dict

*ToolbarView.py:
   -Creates toolbar frame
   -Adds Menubuttons for:
      >File
      >Edit
      >Widgets
      >Grid
      >Debug
   -Adds menu items, separators, checkbox menu items
   -Holds pointer to grid_visible variable
--------------------------------------------------------------------------------------
Controllers - Event & Logic Handlers
--------------------------------------------------------------------------------------
*CanvasController.py:
   -Binds all keyboard/mouse events to the canvas
   -Routes events to EventBus:
      >Widget movement (arrow keys)
      >Shift movement
      >Align commands
      >Snap-to-grid
      >Delete
      >Project saving/opening
      >Grid toggling
      >Selection events
   -Keeps focus, handles context menu trigger
   -Calls CanvasView.render_grid()

*SelectionController.py:
   -Implements:
      >Click selection
      >Ctrl-additive selection
      >Rectangle selection
      >Drag detection (threshold)
      >Drag lifecycle (start, handle, end)
   -Converts canvas coordinates, hit-tests for widget at pointer
   -Uses SelectionView for drawing all selection UIs
   -Emits widget movement events through EventBus

*WidgetController.py:
   -Responsible for applying model changes:
      >Soft rendering (existing widget updates)
      >Full rendering (rebuild all widgets)
      >delete_widget
      >update_widget_attribute (including text-size recalculation)
   -Works tightly with AppState for model mutation

*AttributesPanelController.py:
   -Builds attribute rows based on ATTRIBUTE_CONFIG
   -Computes valid ranges for spinboxes (allowed_x_range / allowed_y_range)
   -Refreshes panel when selection changes
   -Updates spinbox limits when size/anchor changes
   -Clears panel when selection is not singular

*ToolbarController.py:
   -Builds the toolbar menus using ToolbarView
   -Connects each menu item to an EventBus action
   -Handles File, Edit, Widgets, Grid, Debug categories
--------------------------------------------------------------------------------------
Commands - Undo / Redo
--------------------------------------------------------------------------------------
*BaseCommand.py:
   -Abstract base class requiring:
      >execute()
      >undo()

*CommandStack.py:
   -Stores undo and redo stacks
   -Provides:
      >execute(command)
      >undo()
      >redo()

*MoveWidgets.py:
   -Keyboard-based movement
   -Records original positions
   -Applies dx/dy to all selected models
   -Undo restores previous positions via AppState

*MoveWidgetsTo.py:
   -Drag-based movement
   -Records original positions at drag start
   -preview_move() applies incremental deltas
   -freeze_final_positions() stores commit positions
   -execute() applies final positions
   -undo() restores initial position
--------------------------------------------------------------------------------------
Utility System
--------------------------------------------------------------------------------------
*UIComponents.py:
   -load_icon():
      >Loads, converts, resizes image using PIL
   -CustomTitlebar:
      >Implements draggable custom window titlebar
      >Displays icon if provided
      >Close button linking to provided callback
      >Handles movement of window

*Geometry.py:
   -allowed_x_range / allowed_y_range:
      >Computes permissible widget placement range based on anchor + size
   -clamp():
      >Clamps a value between min/max
   -clamped_delta():
      >Clamps movement deltas so widgets remain inside canvas
   -screen_offset_to_center_window():
      >Computes coordinates to center window on screen
   -nearest_in_bounds_grid_step():
      >Computes nearest grid step within allowed range

*CallTracer.py:
   -Optional call-tracing utility for debugging
   -Uses Python profiler for call logging
   -toggle() enables/disables logging
   -Used through Debug menu
================================================================================================
Shortcuts and Gestures
================================================================================================
*Selection:
   -Click → select widget
   -[Ctrl] + Click → toggle selection
   -Drag empty canvas → rectangle selection
      >[Ctrl] → additive rectangle selection

*Movement:
   -Arrow keys → 1px nudge
   -[Shift] + Arrow keys → 10px nudge
   -Keyboard movement supports undo/redo

*Dragging:
   -Drag widget → movement after threshold
   -Preview updates while dragging

*Alignment:
   -Align all selected widgets with the edge of the last selected widget left:
      >[Ctrl] + [Left] → align with left edge
      >[Ctrl] + [Right] → align with right edge
      >[Ctrl] + [Up] → align with top edge
      >[Ctrl] + [Down] → align with bottom edge

*Grid:
   -[G] → toggle grid visibility
   -[Ctrl] + [G] → change grid size
   -[Shift] + [G] → change grid color

*Project:
   -[Ctrl] + [N] → new project
   -[Ctrl] + [O] → open project
   -[Ctrl] + [S] → save project
   -[Ctrl] + [Shift] + [S] → save project as
   -[Alt] + [F4] → exit

*Editing:
   -[Ctrl] + [Z] → undo
   -[Ctrl] + [Y] → redo
   -[Ctrl] + [A] → select all widgets
   -[Delete] → delete selected widgets

*Scrolling:
   -Mouse wheel → vertical scroll
   -[Shift] + Mouse wheel → horizontal scroll
================================================================================================
Unit Tests
================================================================================================
*TestProjectDocumentRoundtrip:
   -Tests JSON serialization/deserialization
   -Ensures grid, theme, dimensions, title are preserved
   -Confirms widget models and ID counters are restored correctly

*TestAddWidgetFromModel:
   -Tests widget creation from a model
   -Ensures preview widget measurement is correct
   -Validates mapping from model ID → widget ID

*TestMoveWidget:
   -Tests move_widget_by and move_widget_to operations
   -Ensures canvas coords match model coordinates

*TestUndoRedoMoveWidget:
   -Verifies MoveWidgets command
   -Ensures undo restores original position
   -Ensures redo reapplies movement

*TestUndoRedoMoveWidgetTo:
   -Verifies drag-based MoveWidgetsTo command
   -Tests preview_move, commit, undo, redo
================================================================================================
Further Notes / Information
================================================================================================
*The program uses a strongly decoupled architecture centered around AppState and EventBus.

*All mutations pass through a unified state engine which ensures predictable rendering behavior.

*Soft vs. full rendering decisions are automatically handled based on the nature of the changes.  

*Scrollbars dynamically appear only when the canvas exceeds the viewport.  

*The Designer uses precise geometry calculations to determine initial window size and scrollbar need, enabling large canvas editing without layout glitches.  

*All user interactions (movement, dragging, attribute editing, selection) are immediately synchronized between the model and view, ensuring correctness and stability.

*The modularity of the subsystem design allows straightforward extension, debugging and testing of individual parts without modifying the whole system.
================================================================================================