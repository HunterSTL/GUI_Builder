===========================================
Tkinter GUI Builder – README
-------------------------------------------
A complete, canvas‑based Tkinter GUI designer featuring pixel‑accurate
widget placement, unified event routing, threshold‑based widget dragging,
incremental preview movement, a committed undo/redo stack, scrollable
workspace, dynamic attributes panel with strict validation, and a fully
modular architecture.

The Designer coordinates specialized Managers through a shared callback
map that ensures separation of concerns, predictable behavior, and
maintainable code structure.
===========================================


Quick Start
-------------------------------------------
1) Run App.py
   - Starts the Tk root window and builds AppController.

2) Choose “New Project” or “Open Project”
   - New:
     • Opens SetupWizard (canvas size, theme colors, icon selection)
     • Produces ProjectDocument → launches Designer
   - Open:
     • Loads *.tkui JSON project, restores canvas, theme, widget models

3) Inside the Designer
   - Right‑click canvas → Add Label / Entry / Button
   - Click / CTRL+Click → selection / multiselection
   - Drag widgets → smooth incremental preview + threshold activation
   - Rectangle selection (drag empty canvas) + additive (CTRL)
   - Scroll with mouse wheel or scrollbars
   - Edit properties via Attributes Panel
   - Toolbar provides File / Edit / Widget / Grid / Debug menus
===========================================


Module Map (Expanded)
-------------------------------------------
Below is the complete module map based on the current project structure.

-------------------------------------------
App Entry & Controller
-------------------------------------------
App.py:
 - Application entry point.
 - Creates Tk root and attaches AppController.

AppController.py:
 - Builds startup window using CustomTitlebar.
 - Manages:
   *New, *Open, *Save, *Save As, *Export JSON, *Exit
 - Tracks unsaved changes, window positions, last directory.
 - Maintains user theme copies and PROGRAM_THEME.
 - Creates and destroys SetupWizard or Designer.
 - Provides project‑level callbacks to Designer.
===========================================


Setup Wizard
-------------------------------------------
SetupWizard.py:
 - Asks for:
   • Window title
   • Canvas width/height
   • Theme colors (background, label, entry, button)
   • Icon selection (PNG/JPG/ICO)
 - Shows live previews for theme colors.
 - Validates canvas sizes via CONSTANTS.
 - Builds a ProjectDocument + GridConfig.
 - Returns the ProjectDocument to AppController and closes.
===========================================


Designer (Main Editor)
-------------------------------------------
Designer.py:
 - Creates main workspace:
   *CustomTitlebar
   *Toolbar
   *Scrollable canvas viewer
   *Attributes Panel (right side)
 - Initializes:
   *CanvasManager
   *SelectionManager
   *WidgetManager
   *AttributesPanelManager
   *ToolbarManager
 - Maintains DesignerState (dirty flag, drag command, last click coords).
 - Integrates CommandStack for undo/redo.
 - Loads existing widget models into the canvas.
 - Determines window dimensions & scrollbar requirements dynamically.
 - Updates title with “*” when project is dirty.
===========================================


Managers (Core Editing Logic)
-------------------------------------------
_managers/CanvasManager.py:
 - Builds the design canvas.
 - Draws/clears grid lines.
 - Computes scrollregion and manages scrollbar visibility.
 - Binds all keyboard shortcuts:
   movement, alignment, grid tools, project actions, edit actions.
 - Ensures canvas receives focus.

_managers/SelectionManager.py:
 - Full selection engine:
   *Single, multiselect, toggle selection
   *Rectangle selection (with additive CTRL mode)
   *Top‑most window detection
 - Drag logic:
   *Threshold‑based activation
   *Incremental deltas via WidgetDragState
   *Re‑entry safeguard inside canvas drag handler
 - Maintains selection outlines:
   *Blue = selected, Red = last selected
 - Notifies Designer for attribute panel updates.

_managers/WidgetManager.py:
 - Creates widgets from models or user actions.
 - Maintains widget_map: widget_id → {model, widget}
 - Updates widget attributes (x, y, width, height, text, colors, anchor).
 - Makes all widget mouse events forward to canvas.
 - Handles deletion and model cleanup.
 - Ensures outline stays synced via SelectionManager.

_managers/AttributesPanelManager.py:
 - Dynamically creates attribute editors from ATTRIBUTE_CONFIG.
 - Provides:
   *Spinboxes with clamped ranges
   *Validated text entries
   *Color preview boxes
   *Anchor selector
 - Silent update mode prevents recursive refresh.
 - Recomputes spinbox limits when anchor/size change.

_managers/ToolbarManager.py:
 - Creates top toolbar with:
   *File, *Edit, *Widgets, *Grid, *Debug menus
 - Menus call into Designer callbacks.
 - Provides grid visibility checkbox bound to BooleanVar.
===========================================


Commands (Undo/Redo System)
-------------------------------------------
_commands/BaseCommand.py:
 - Abstract base class for all commands.

_commands/CommandStack.py:
 - Tracks undo/redo stacks and executes commands.

_commands/MoveWidgets.py:
 - Keyboard‑based movement.
 - Records original positions.
 - Undo restores previous coordinates.

_commands/MoveWidgetsTo.py:
 - Drag‑based movement.
 - On drag start: records original positions.
 - preview_move(dx,dy): incremental deltas during drag.
 - freeze_final_positions(): snapshot final placement.
 - execute(): apply final positions.
 - undo(): restore original coordinates.
===========================================


Dataclasses (Project, Models, States)
-------------------------------------------
_dataclasses/ProjectDocument.py:
 - Stores:
   *version, title, width/height, icon_path
   *theme dictionary
   *GridConfig
   *widget_models list
 - Handles JSON (to_json/from_json) and restores ID counters.

_dataclasses/GridConfig:
 - Grid size, color, visibility.

_dataclasses/WidgetModels.py:
 - BaseWidgetData + LabelWidgetData + EntryWidgetData + ButtonWidgetData.
 - Each provides create_id() using global IdCounters.
 - Stores text, size, colors, anchor, x/y.

_dataclasses/DesignerState.py:
 - Tracks dirty flag, deleting flag, last click coords,
   and active MoveWidgetsTo command.

_dataclasses/RectangleSelectionState.py:
 - Start coords, rectangle id, dragging flag, additive flag.

_dataclasses/WidgetDragState.py:
 - Drag state for widget movement:
   start_coords, end_coords, last incremental deltas, state flag.
===========================================


Utility & Geometry
-------------------------------------------
UIComponents.py:
 - load_icon(path,size)
   *Loads PNG/JPG/ICO via PIL
   *Resizes with LANCZOS filtering
 - CustomTitlebar
   *Draggable overrideredirect titlebar
   *Supports icon + title + close button
   *Used by Startup, SetupWizard, Designer

Geometry.py:
 - allowed_x_range(), allowed_y_range()
   *Anchor‑aware coordinate limits
 - clamp(): clamps value to [min,max]
 - clamped_delta(): prevents widgets from exiting canvas bounds
 - screen_offset_to_center_window(): centers window
===========================================


Theme & Constants
-------------------------------------------
Theme.py:
 - USER_THEME: default user‑modifiable theme (SetupWizard).
 - PROGRAM_THEME: static theme used for app UI.
 - CONSTANTS:
   *window min/max sizes
   *canvas min/max sizes
   *titlebar/toolbar/attribute panel dimensions
   *selection styling (padding, width, dash)
   *grid size
   *nudge distances
   *drag threshold
===========================================


Core Features
-------------------------------------------
- Complete project lifecycle support.
- Scrollable canvas with dynamic scrollbar control.
- Accurate widget placement with anchor‑aware bounds.
- Robust selection engine:
  *Single, multi, toggle, rectangle selection
  *Additive rectangle selection via CTRL
- Advanced drag system:
  *Threshold detection
  *Incremental preview movement
  *Safe re‑entry protection
- Widget alignment tools relative to last‑selected widget.
- Grid tools (toggle, recolor, resize).
- Dynamic Attributes Panel with strict constraints.
- Full undo/redo for all widget move operations.
- Custom draggable titlebars for all windows.
===========================================


Shortcuts & Gestures
-------------------------------------------
Selection:
 *Click → select
 *CTRL+Click → toggle
 *Drag empty canvas → rectangle selection
 *CTRL+Drag → additive rectangle select

Dragging:
 *Drag widget → incremental deltas + preview
 *Threshold prevents accidental drags

Movement:
 *Arrow Keys → 1px nudge
 *Shift+Arrow → 10px nudge

Alignment:
 *CTRL+←/→/↑/↓ → align relative to last selected

Grid:
 *g → toggle grid visibility
 *CTRL+g → change grid size
 *Shift+G → change grid color

Project:
 *CTRL+N / CTRL+O / CTRL+S / CTRL+Shift+S
 *CTRL+E → Export JSON
 *ALT+F4 → Exit

Editing:
 *CTRL+Z / CTRL+Y → undo/redo
 *CTRL+A → select all
 *Delete → delete widgets

Scrolling:
 *Mouse wheel → vertical scroll
 *Shift+Wheel → horizontal scroll
===========================================


Unit Tests
-------------------------------------------
UnitTests.py:
 - Contains automated test suites validating core components.

TestProjectDocumentRoundtrip:
 *Ensures ProjectDocument → JSON → ProjectDocument works correctly.
 *Checks:
   version, title, width/height
   GridConfig (size, color, visibility)
   widget restoration
 *Verifies IdCounters are advanced after loading.

TestAddWidgetFromModel:
 *Confirms WidgetManager.add_widget_from_model:
   correct widget placement
   width/height updates
   widget_map entry creation
   correct ID creation (label1, entry1, button1)

TestMoveWidget:
 *Validates:
   move(dx,dy) correctly updates model + canvas
   move_to(x,y) correctly positions widget and updates model

TestUndoRedoMoveWidget:
 *Verifies MoveWidgets command:
   execute(), undo(), redo() maintain correct positions

TestUndoRedoMoveWidgetTo:
 *Validates MoveWidgetsTo drag workflow:
   preview_move(dx,dy)
   freeze_final_positions()
   execute(), undo(), redo()
===========================================


File Format
-------------------------------------------
*.tkui JSON:
 - Stores:
   *version
   *title, width, height
   *grid configuration
   *theme colors
   *list of widget_models
 - Loader restores ID counters to preserve unique naming.
===========================================


Notes
-------------------------------------------
- Selection outlines always stay in sync with widget geometry.
- Attributes Panel appears only for single selection.
- Grid drawing is rebuilt dynamically on changes.
- Incremental drag deltas ensure stable preview + reliable undo/redo.
- Scrollbars appear only when needed based on canvas vs. window size.