"""
===========================================
Tkinter GUI Builder - Package Documentation
-------------------------------------------
This package provides a lightweight, canvas-based GUI designer for Tkinter.

It includes:
- A startup flow with an AppController, a setup wizard for theming and initial
  configuration, and a visual Designer window. 
- A canvas for placing widgets as "window items" with pixel-precise control.
- A right-side attributes panel with two-way binding to widget models.
- Selection (single/multi) with rectangle selection and drag gestures.
- A toolbar with common actions (grid toggle, alignment, snapping, file menu).
Widgets are created as Tkinter Canvas “window” items, and a data model keeps
their properties synchronized with the live UI.

===========================================
Module map
-------------------------------------------
"__init__.py":
  Package-level documentation (this file).

"Theme.py":
  Central themes & constants.
  - USER_THEME: initial, user-editable colors used for the designed GUI.
  - PROGRAM_THEME: static program UI colors (titlebar, toolbar, menus, panel).
  - CONSTANTS: sizing, key masks, selection styling, nudge sizes, etc.

"DataModels.py":
  Dataclasses for widget models (LabelWidgetData, EntryWidgetData, ButtonWidgetData)
  with positions, size, colors, and anchor; plus IdCounters for unique IDs.

"ProjectDocument.py":
  Serializable project state (version, title, size, grid, theme, widget_models).
  - to_json(): convert to dict.
  - from_json(): rebuilds models and updates IdCounters to avoid ID collisions.

"App.py":
  Entry point. Creates Tk root, instantiates AppController, and starts mainloop.

"AppController.py":
  Startup window & app lifecycle controller.
  - Custom titlebar (drag + close), and buttons for New/Open/Exit.
  - Maintains app state (e.g., dirty flag via Designer, last directory/path stubs),
    carries a safe copy of USER_THEME for each new project,
  - `prompt_unsaved_changes()` before destructive actions,
  - Launches SetupWizard for new projects and then opens Designer with the
    generated ProjectDocument and selected icon.
  - Supplies `project_callbacks` (new/open/save/save_as/export_json/exit_app) to Designer.

"SetupWizard.py":
  Pre-designer configuration:
  - Window title, width/height validation, and live color picking for user theme.
  - Optional icon selection/preview.
  - Builds a ProjectDocument and returns it via an on_done callback.

"Designer.py":
  Main orchestrator (Designer). Creates and wires:
  - CanvasManager (canvas + grid + keybinds),
  - SelectionManager (selection + rectangle selection + highlighting),
  - WidgetManager (add/move/align/snap/delete + model updates),
  - AttributesPanelManager (dynamic, two-way panel),
  - ToolbarManager (File/Widgets/Grid/Debug menus).
  Holds a shared `callbacks` dictionary that all managers use for actions.
  Manages dirty state (appends "*" to title when there are unsaved changes).

"AttributesPanelManager.py":
  Dynamic attribute panel driven by ATTRIBUTE_CONFIG and DISPLAY_NAMES:
  - Generates labeled rows and appropriate editors (entry/spinbox/color/anchor),
  - Two-way binding: user edits → WidgetManager.update_widget_attribute,
    model/widget changes → silent variable updates in the panel,
  - Computes spinbox limits from canvas size and anchor,
  - Shows when exactly one widget is selected; hides otherwise.

"CanvasManager.py":
  Creates and packs the Canvas with project dimensions and background, handles:
  - Grid visualization (draw/clear/toggle, size & color changes),
  - Global canvas events (context menu, selection wiring),
  - Keybinds for widget movement, snapping, alignment, project actions,
  - Focus management so the canvas receives keystrokes.

"SelectionManager.py":
  Tracks currently selected canvas window items, including:
  - Click/CTRL-toggle, last-selected marker, and outline rendering,
  - Rectangle selection (additive with CTRL),
  - Mouse-drag gesture bookkeeping and forwarding movement deltas
    to the widget-moving callback.

"ToolbarManager.py":
  Provides the top toolbar with:
  - File menu (New/Open/Save/Save as/Export JSON/Exit),
  - Widget menu (Delete/Snap to grid/Align left/right/top/bottom),
  - Grid menu (Visualize/Change size/Change color),
  - Debug menu (Set dirty/Set clean).

"WidgetManager.py":
  The sole mutator of widget models and their corresponding Tk widgets.
  - Create new widgets based on user theme (with clamped initial positions),
  - Build widgets from existing models,
  - Move selected widgets (with canvas-bounds clamping),
  - Snap to grid, align (left/right/top/bottom), and delete (with confirm),
  - Apply attribute changes from the attributes panel and keep outlines in sync.
  Maintains `widget_map` of {canvas_window_id: {"model": model, "widget": tk_widget}}.

===========================================
Core Features
-------------------------------------------
- AppController-driven startup flow with unsaved-changes prompt.
- Canvas-based, pixel-precise placement of widgets as window items.
- Shared callbacks dictionary: managers publish and consume actions without tight coupling.
- Robust selection:
  * single/multi-select with CTRL,
  * rectangle selection,
  * clear visual outlines with last-selected highlight.
- Widget operations:
  * mouse-drag moves (with clamped deltas so items stay inside the canvas),
  * keyboard nudges (small/large),
  * align to last-selected (left/right/top/bottom),
  * snap to grid,
  * delete with confirmation.
- Attributes panel with two-way binding and validation (spinbox limits based on size/anchor).
- Grid visualization controls (toggle, size, color).
- Simple toolbar menus for discoverability of common actions.
- Dirty-state indicator in the Designer title.

===========================================
"""