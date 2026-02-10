===========================================
Tkinter GUI Builder – README
-------------------------------------------
A complete, canvas‑based Tkinter GUI designer featuring pixel‑precise widget
placement, incremental drag-based movement with a committed undo/redo stack,
multi‑selection and rectangle selection, scrollable work area, attribute panel
with two‑way binding, and a fully decoupled manager architecture.

The Designer orchestrates multiple specialized managers through a shared
callback map that keeps responsibilities isolated and the system maintainable.
===========================================
Quick Start
-------------------------------------------
1) Run App.py
   - Starts the Tk root window and attaches AppController.

2) Choose “New Project” or “Open Project”
   - New:
       • Opens SetupWizard for window size, theme, and optional icon.
       • Produces a ProjectDocument and launches Designer.
   - Open:
       • Loads a *.tkui JSON project, restores widgets, theme, and grid.

3) Inside the Designer
   - Right‑click canvas → Add Label / Entry / Button.
   - Click/CTRL+Click → select or multiselect widgets.
   - Drag widgets → smooth preview movement with drag‑threshold.
   - Scroll large canvases using scrollbars or mouse wheel.
   - Edit properties via Attributes Panel (right side).
   - Use toolbar for project, widget, grid, and debug actions.
===========================================
Module Map (Expanded)
-------------------------------------------
Below is an expanded list of all modules in the project, grouped by purpose.
Each heading shows the **actual file path**, exactly as in your project.

-------------------------------------------
App Entry & Controller
-------------------------------------------

App.py:
  - Program entry point.
  - Creates root Tk, launches AppController, enters mainloop.

AppController.py:
  - Builds the startup window (with custom draggable titlebar).
  - Manages project lifecycle:
       * New, Open, Save, Save As, Export JSON, Exit
  - Tracks unsaved changes and prompts appropriately.
  - Manages a per-session copy of USER_THEME.
  - Launches SetupWizard or Designer.
  - Provides callback map for Designer actions.

-------------------------------------------
Setup Wizard
-------------------------------------------

SetupWizard.py:
  - Window title, canvas size, and complete user‑theme configuration.
  - Live preview widgets for colors (Label, Entry, Button, Background).
  - Optional icon loading.
  - Ensures size constraints via CONSTANTS.
  - Emits (ProjectDocument, icon) to AppController.

-------------------------------------------
Designer (Main Editor)
-------------------------------------------

Designer.py:
  - Central workspace for designing UIs.
  - Creates custom titlebar and main layout:
       * Scrollable canvas viewer
       * Attributes panel frame
       * Toolbar
  - Instantiates and wires:
       * CanvasManager
       * SelectionManager
       * WidgetManager
       * AttributesPanelManager
       * ToolbarManager
  - Integrates CommandStack for undo/redo.
  - Loads widgets from ProjectDocument.
  - Computes window size constraints and activates scrollbars accordingly.
  - Manages dirty state (“*” appended to title).

-------------------------------------------
Managers (Core Editing Logic)
-------------------------------------------

_managers/CanvasManager.py:
  - Creates actual Tkinter Canvas for designing.
  - Draws / clears / refreshes the grid.
  - Maintains scrollregion and scrollbar integration.
  - Binds all keybindings for movement, alignment, grid controls, project actions.
  - Ensures canvas takes focus for keyboard shortcuts.

_managers/SelectionManager.py:
  - Complete selection engine:
       * Single-click, CTRL-click, toggle.
       * Rectangle selection with additive mode (CTRL).
       * Correct topmost widget detection.
       * Drag‑threshold detection for switching from “click” to “drag”.
       * Informs Designer when drag starts/ends.
  - Maintains outline rectangles (including last‑selected colored highlight).

_managers/WidgetManager.py:
  - Responsible for:
       * Creating widgets (new or from model)
       * Deleting widgets
       * Moving widgets (move, move_to)
       * Updating attributes (size, text, color, anchor, x/y)
  - Contains mapping: widget_id → {"model": model, "widget": widget}
  - Forwards all widget mouse events to canvas for unified behavior.

_managers/AttributesPanelManager.py:
  - Builds dynamic attribute panel based on ATTRIBUTE_CONFIG.
  - Provides entries, spinboxes, anchors, and color previews.
  - Enforces min/max spinbox limits based on canvas size + anchor.
  - Two‑way binding with silent update mode.

_managers/ToolbarManager.py:
  - Builds the top toolbar (File, Edit, Widgets, Grid, Debug menus).
  - Connects menu commands to the callback map.
  - Includes checkbutton for grid visualization.

_managers/__init__.py:
  - Exports all managers (CanvasManager, SelectionManager, WidgetManager,
    ToolbarManager, AttributesPanelManager).

-------------------------------------------
Commands (Undo/Redo System)
-------------------------------------------

_commands/BaseCommand.py:
  - Abstract base class defining execute() and undo().

_commands/CommandStack.py:
  - Stores executed commands.
  - Handles undo/redo behavior with correct stack clearing.

_commands/MoveWidgets.py:
  - Represents keyboard‑based movement (dx/dy).
  - Records original positions on execute().
  - Undo restores original coordinates using move_to().

_commands/MoveWidgetsTo.py:
  - Core drag‑movement command.
  - On drag start: captures original positions.
  - preview_move(dx, dy): incremental movement during drag.
  - On drag end: freeze_final_positions() records the end state.
  - execute(): moves widgets to final positions.
  - undo(): restores original positions.

_commands/__init__.py:
  - Re‑exports Command, CommandStack, MoveWidgets, MoveWidgetsTo.

-------------------------------------------
Dataclasses (Project, Widgets, States)
-------------------------------------------

_dataclasses/ProjectDocument.py:
  - Primary project data container.
  - Fields: version, title, width, height, grid, theme, widget_models.
  - to_json() returns serializable dict.
  - from_json() loads widget models and updates IdCounters based on IDs present.

_dataclasses/GridConfig (in ProjectDocument.py):
  - Grid size, color, visibility.

_dataclasses/WidgetModels.py:
  - Defines BaseWidgetData + subclasses:
       * LabelWidgetData
       * EntryWidgetData
       * ButtonWidgetData
  - Each has create_id() that uses central IdCounters.
  - Includes global IdCounters for ID consistency across sessions.

_dataclasses/DesignerState.py:
  - Tracks Designer internal state:
       * last click coords
       * dragging window
       * window coordinates
       * is_dirty
       * is_deleting
       * active MoveWidgetsTo command during drag

_dataclasses/RectangleSelectionState.py:
  - Data for rectangle selection:
       * selection_rectangle_id
       * start coords
       * flags for dragging and additive mode.

_dataclasses/WidgetDragState.py:
  - Data used internally by SelectionManager for drag tracking:
       * start coords
       * end coords
       * last_total_dx / last_total_dy
       * is_dragging flag

_dataclasses/__init__.py:
  - Re‑exports all dataclasses and IdCounters.

-------------------------------------------
Geometry / Utility Logic
-------------------------------------------

Geometry.py:
  - allowed_x_range(), allowed_y_range():
       * Provides min/max allowed coordinates based on widget size + anchor.
  - clamp(): bounds a value in [min, max].
  - clamped_delta(): clamps movement so widgets remain inside canvas.
  - screen_offset_to_center_window(): centers window on screen.

-------------------------------------------
Theme & Constants
-------------------------------------------

Theme.py:
  - USER_THEME defaults (overridden by SetupWizard).
  - PROGRAM_THEME for internal UI.
  - CONSTANTS:
       * window min/max sizes
       * canvas min/max sizes
       * titlebar/toolbar heights
       * selection styling
       * grid size
       * nudge values (small/big)
       * drag_threshold
===========================================
Core Features
-------------------------------------------
- Project lifecycle fully managed (New/Open/Save/Save As/Export JSON).
- Scrollable canvas with smart scrollbar enabling.
- Pixel‑accurate widget placement with anchor support.
- Comprehensive selection system:
    * Single select, multi-select, toggle, rectangle selection.
    * Correct ordering and outline layering.
- Drag-threshold‑based widget movement with incremental deltas.
- Alignment:
    * Left / Right / Top / Bottom relative to last-selected.
- Snap-to-grid, toggle-grid, change grid color and size.
- Attributes panel with strict validation and dynamic spinbox limits.
- Full undo/redo using command pattern.
- Custom draggable titlebars for Startup and Designer windows.
===========================================
Shortcuts & Gestures (default)
-------------------------------------------
Selection:
  * Click → select
  * CTRL+Click → toggle
  * Drag empty canvas → rectangle selection
  * CTRL+Drag → additive rectangle select

Dragging:
  * Drag widget with mouse → live preview then commit
  * Drag threshold prevents accidental drags

Movement:
  * Arrow Keys → 1px nudge
  * Shift+Arrow → 10px nudge

Alignment:
  * CTRL + ←/→/↑/↓ → align relative to last-selected

Grid:
  * g → toggle visualization
  * CTRL+g → change grid size
  * Shift+G → change grid color

Project:
  * CTRL+N / CTRL+O / CTRL+S / CTRL+Shift+S
  * CTRL+E → Export JSON
  * ALT+F4 → Exit

Editing:
  * CTRL+Z / CTRL+Y → undo/redo
  * CTRL+A → select all
  * Delete → delete selected widgets

Scrolling:
  * Mouse wheel → vertical scroll
  * Shift+wheel → horizontal scroll
===========================================
File Format
-------------------------------------------
*.tkui JSON
  - Stores:
       * version
       * title
       * width, height
       * grid config
       * theme colors
       * widget_models list
  - Loader sets IdCounters to avoid ID reuse.
===========================================
Notes
-------------------------------------------
- Widget movement and selection outlines always stay correctly synchronized.
- Attributes panel appears only when exactly one widget is selected.
- Dragging uses incremental deltas (MoveWidgetsTo) to ensure stable undo/redo.
- Scrollbars appear only when needed, based on window size vs canvas dimensions.
- All widget interactions are routed through WidgetManager for consistency.