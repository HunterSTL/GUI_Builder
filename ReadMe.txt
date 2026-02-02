===========================================
Tkinter GUI Builder – README
-------------------------------------------
A lightweight, canvas-based GUI designer for Tkinter with pixel-precise widget
placement, a two-way bound attributes panel, robust selection, and a command-
driven undo/redo stack. The Designer orchestrates dedicated managers through a
shared callback map for clear, decoupled responsibilities.
===========================================

Quick Start
-------------------------------------------
1) Run App.py
   - Creates a Tk root, wires AppController, starts the mainloop.
2) Choose “New project” or “Open project”
   - New: launches the SetupWizard to configure window size, theme colors, and
     optional icon, then opens the Designer with a fresh ProjectDocument.
   - Open: loads a *.tkui file (JSON) into a ProjectDocument and opens the Designer.
3) In the Designer
   - Right-click canvas to add widgets (Label / Entry / Button).
   - Use the attributes panel (right side) for precise edits with validation.
   - Use the toolbar/shortcuts for selection, movement, alignment, grid, and save.

===========================================
Module Map
-------------------------------------------
"Theme.py":
 Centralized themes & constants.
  - USER_THEME: user-editable colors applied to designed widgets.
  - PROGRAM_THEME: program UI colors (titlebar, toolbar, menus, panels).
  - CONSTANTS: sizing constraints, key masks, selection styling, nudge sizes,
    toolbar/titlebar heights, attributes panel width.

"DataModels.py":
 Dataclasses for widget models (LabelWidgetData, EntryWidgetData, ButtonWidgetData)
 with position, size, colors, anchor, and generated IDs. Includes IdCounters for
 stable, unique IDs across reloads.

"ProjectDocument.py":
 Serializable container for project state.
  - Fields: version, title, window size, grid config, theme, widget_models.
  - to_json(): JSON-serializable dict for persistence.
  - from_json(): reconstructs a ProjectDocument and updates IdCounters to avoid
    ID collisions across sessions.

"App.py":
 Application entry point.
  - Creates Tk root, instantiates AppController, starts mainloop.

"AppController.py":
 Startup UI and application lifecycle.
  - Custom titlebar (drag + close).
  - “New / Open / Exit” actions.
  - Tracks save path & last directory, prompts on unsaved changes.
  - Maintains a safe, per-session copy of USER_THEME.
  - Launches SetupWizard for new projects and opens Designer with callbacks:
    new/open/save/save_as/export_json/exit_app.

"SetupWizard.py":
 Pre-designer configuration dialog.
  - Window title & size inputs.
  - Live color pickers for USER_THEME.
  - Optional icon selection + preview.
  - Emits a ready-to-use ProjectDocument via on_done callback.

"Designer.py":
 Central coordinator and UI shell.
  - Wires:
    * CanvasManager (canvas creation, grid rendering, keybindings),
    * SelectionManager (selection state, rectangle selection, outlines),
    * WidgetManager (canvas widget creation, movement, deletion, attribute apply),
    * AttributesPanelManager (dynamic attributes UI),
    * ToolbarManager (menus + shared command/callback wiring).
  - Single authority for widget mutations, model updates, dirty/clean marking,
    and grid synchronization.
  - Appends "*" to window title on unsaved changes.

"AttributesPanelManager.py":
 Dynamic attributes panel driven by ATTRIBUTE_CONFIG and DISPLAY_NAMES.
  - Builds labeled rows and appropriate editors (entry, spinbox, color, anchor).
  - Two-way binding:
    * User edits → attribute_changed callbacks.
    * Programmatic model changes → silent variable updates.
  - Spinbox limits adapt to canvas size and widget anchor.
  - Visible only when exactly one widget is selected.

"CanvasManager.py":
 Canvas construction and global bindings.
  - Creates the design canvas from project dimensions/background.
  - Grid rendering: draw/clear/refresh based on project state (size/color/visible).
  - Ensures the canvas reliably holds keyboard focus.
  - Binds context menu, selection gestures, movement/alignment/grid shortcuts,
    and project actions (new/open/save/...).

"SelectionManager.py":
 Selection and drag-gesture controller for canvas window items.
  - Single/multi-select with CTRL, additive rectangle selection.
  - Maintains "last-selected" for alignment and highlighting.
  - Draws outlines and forwards drag deltas to movement logic.

"ToolbarManager.py":
 Toolbar and menu bar.
  - File: New, Open, Save, Save As, Export JSON, Exit.
  - Edit: Cut, Copy, Paste, Undo, Redo, Select All (some may be stubs).
  - Widget: Delete, Snap to Grid, Align (left/right/top/bottom).
  - Grid: Visualize toggle (bound to BooleanVar), Change size, Change color.
  - Debug: Set dirty / Set clean.

"commands/":
 Command abstraction and undo/redo stack for editor actions.
  - BaseCommand.py: abstract Command with execute()/undo().
  - CommandStack.py: push/undo/redo; clears redo on new execute().
  - MoveWidgets.py: move selected widgets by (dx, dy) with clamped deltas.
  - MoveWidgetsTo.py: drag-aware command:
    * On drag start: captures original positions (models) in _original_positions.
    * preview_move(dx, dy): live, non-committal movement while dragging.
    * On drag end: freeze_final_positions() to capture final positions.
    * execute()/undo(): move to final/original positions for robust redo/undo.

"WidgetManager.py":
 Widget <-> Canvas adapter.
  - Creates canvas window items from models/live widgets and maintains
    widget_map: { canvas_window_id: { "model": model, "widget": tk_widget } }.
  - Applies model attribute changes (position/size/text/colors/anchor).
  - Provides movement helpers (move, move_to) with selection outline sync.
  - Emits begin/end drag notifications to Designer via callbacks.

===========================================
Core Features
-------------------------------------------
- AppController-driven startup with unsaved-changes prompting.
- JSON project persistence (*.tkui), human-readable and diff-friendly.
- Canvas-based layout with pixel-precise placement (Canvas window items).
- Explicit callback map to keep managers decoupled and testable.
- Selection:
  * Single/multi-select with CTRL,
  * Additive rectangle selection,
  * Last-selected highlighting for alignment reference.
- Widget operations:
  * Mouse-drag movement with clamped deltas (canvas bounds),
  * Keyboard nudging (small/large),
  * Align to last-selected (left/right/top/bottom),
  * Snap to grid,
  * Delete with confirmation.
- Attributes panel with validation and dynamic spinbox limits.
- Grid controls: show/hide, size, color.
- Title-based dirty indicator in Designer (“*” suffix).
- Command-based undo/redo:
  * MoveWidgets: keyboard-based nudge steps.
  * MoveWidgetsTo: fully undoable drag-and-drop with preview + commit phases.

===========================================
Shortcuts & Gestures (default)
-------------------------------------------
- Selection:
  * Click to select; CTRL+Click to toggle.
  * Drag on empty canvas for rectangle selection; CTRL for additive.
- Movement:
  * Arrow keys → small nudge (dx, dy).
  * Shift+Arrow → large nudge.
  * Mouse drag on widget → live preview; commit on mouse release.
- Alignment:
  * Ctrl+Left/Right/Up/Down → align to last-selected’s left/right/top/bottom.
- Grid:
  * g → toggle visualization,
  * Ctrl+g → change grid size,
  * Shift+G → change grid color.
- Project & Edit (typical):
  * Ctrl+N / Ctrl+O / Ctrl+S / Ctrl+Shift+S for new/open/save/save-as,
  * Ctrl+E for export JSON,
  * Ctrl+Z / Ctrl+Y for undo/redo,
  * Delete to remove selected.

===========================================
File Format
-------------------------------------------
- *.tkui JSON
  * Contains: version, title, width/height, theme, grid config, widget_models.
  * Widget models store id/type/x/y/width/height/colors/text/anchor.
  * Loader updates IdCounters to ensure unique IDs across sessions.

===========================================
Notes
-------------------------------------------
- Window sizing and panel dimensions are governed by Theme.CONSTANTS.
- Movement is clamped so widgets stay fully inside the canvas.
- Attributes panel is visible only for single selection to avoid ambiguity.
- Drag-and-drop is split into preview (live move) and commit (execute command),
  enabling precise, reliable undo/redo across complex drags.
