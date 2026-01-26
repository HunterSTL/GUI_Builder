"""
===========================================
Tkinter GUI Builder – Package Documentation
-------------------------------------------
This package provides a lightweight, canvas-based GUI designer for Tkinter.

It includes:
- A startup flow with an AppController, a setup wizard for theming and initial
  configuration, and a visual Designer window.
- A canvas for placing widgets as Tkinter Canvas “window items” with
  pixel-precise control.
- A right-side attributes panel with two-way binding to widget models.
- Selection (single/multi) with rectangle selection and drag gestures.
- A toolbar with common actions (file operations, grid control, alignment,
  snapping, edit actions).

Widgets are represented by dataclass-based models and rendered as live Tk
widgets embedded in a Canvas. The Designer acts as the central orchestrator,
coordinating all managers via an explicit callback system.
===========================================

Module map
-------------------------------------------
"__init__.py":
 Package-level documentation (this file).

"Theme.py":
 Central themes & constants.
 - USER_THEME: initial, user-editable colors used for the designed GUI.
 - PROGRAM_THEME: static program UI colors (titlebar, toolbar, menus, panels).
 - CONSTANTS: sizing, key masks, selection styling, nudge sizes, etc.

"DataModels.py":
 Dataclasses for widget models (LabelWidgetData, EntryWidgetData,
 ButtonWidgetData) including position, size, colors, anchor, and ID.
 Includes IdCounters to ensure unique widget IDs across project reloads.

"ProjectDocument.py":
 Serializable project state container.
 - Stores version, title, window size, grid configuration, theme, and widget
   models.
 - to_json(): converts the project into a JSON-serializable dict.
 - from_json(): rebuilds a ProjectDocument and updates IdCounters to prevent
   ID collisions when loading saved projects.

"App.py":
 Application entry point.
 - Creates the Tk root window.
 - Instantiates AppController.
 - Starts the Tk mainloop.

"AppController.py":
 Startup window and application lifecycle controller.
 - Custom titlebar (drag + close).
 - Buttons for New Project, Open Project, and Exit.
 - Manages save paths, last directory, and unsaved-changes prompting.
 - Holds a safe per-project copy of USER_THEME.
 - Launches SetupWizard for new projects and opens Designer with the resulting
   ProjectDocument and optional icon.
 - Supplies project_callbacks (new/open/save/save_as/export_json/exit_app)
   to the Designer.

"SetupWizard.py":
 Pre-designer configuration dialog.
 - Window title and size input with validation.
 - Live color picking for the user theme.
 - Optional icon selection and preview.
 - Builds a ProjectDocument and returns it via an on_done callback.

"Designer.py":
 Main application controller and orchestrator.
 - Creates and wires:
   * CanvasManager (canvas creation, grid rendering, keybindings),
   * SelectionManager (selection state, rectangle selection, outlines),
   * WidgetManager (canvas widget creation, movement, deletion, attribute
     application),
   * AttributesPanelManager (dynamic attributes UI),
   * ToolbarManager (menus and command wiring).
 - Owns the shared callbacks dictionary used by all managers.
 - Acts as the single authority for:
   * widget mutation,
   * model updates,
   * dirty/clean state,
   * grid state synchronization.
 - Appends "*" to the window title when there are unsaved changes.

"AttributesPanelManager.py":
 Dynamic attributes panel driven by ATTRIBUTE_CONFIG and DISPLAY_NAMES.
 - Generates labeled rows and appropriate editors (entry, spinbox, color,
   anchor selector).
 - Two-way binding:
   * user edits emit attribute_changed callbacks,
   * model changes trigger silent variable updates in the panel.
 - Computes spinbox limits based on canvas size and widget anchor.
 - Shown only when exactly one widget is selected.

"CanvasManager.py":
 Manages the Tkinter Canvas.
 - Creates and packs the canvas using project dimensions and background color.
 - Handles grid rendering (draw, clear, refresh) based on project state.
 - Binds global canvas events:
   * context menu,
   * selection gestures,
   * keyboard shortcuts for movement, alignment, grid control, and project
     actions.
 - Ensures the canvas reliably receives keyboard focus.

"SelectionManager.py":
 Tracks currently selected canvas window items.
 - Supports single and multi-selection with CTRL.
 - Rectangle selection (additive with CTRL).
 - Maintains last-selected state for alignment and highlighting.
 - Renders selection outlines and forwards drag deltas for widget movement.

"ToolbarManager.py":
 Provides the top toolbar UI.
 - File menu: New, Open, Save, Save As, Export JSON, Exit.
 - Edit menu: Cut, Copy, Paste, Undo, Redo, Select All (some actions stubbed).
 - Widget menu: Delete, Snap to Grid, Align (left/right/top/bottom).
 - Grid menu: Visualize grid (checkbox-bound), Change size, Change color.
 - Debug menu: Set dirty / Set clean.
 - Uses a BooleanVar to keep grid menu state synchronized with the project.

"WidgetManager.py":
 Low-level widget and canvas adapter.
 - Creates canvas window items from models or live widgets.
 - Maintains widget_map:
   {canvas_window_id: {"model": model, "widget": tk_widget}}
 - Applies attribute changes to widgets (position, size, text, colors, anchor).
 - Moves and deletes canvas items on request.
 - Keeps selection outlines in sync with widget changes.
===========================================

Core Features
-------------------------------------------
- AppController-driven startup flow with unsaved-changes prompts.
- JSON-based project persistence (safe, human-readable).
- Canvas-based, pixel-precise widget placement using window items.
- Explicit callback-based communication between managers.
- Robust selection system:
  * single/multi-select,
  * rectangle selection,
  * last-selected highlighting.
- Widget operations:
  * mouse-drag movement with clamped deltas,
  * keyboard nudging (small/large),
  * alignment to last-selected widget,
  * snap to grid,
  * delete with confirmation.
- Attributes panel with validation and dynamic limits.
- Grid visualization controls (toggle, size, color).
- Toolbar-driven access to common editor actions.
- Clear dirty-state indicator in the Designer title.
===========================================
"""