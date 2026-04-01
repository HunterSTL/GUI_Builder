===========================================
Tkinter GUI Builder – README
-------------------------------------------
A fully‑interactive, canvas‑based Tkinter GUI designer featuring pixel‑accurate 
widget placement, MVC architecture, dynamic attributes editing, multi‑tool 
selection system, custom titlebars, scrollable design surface, and a robust 
undo/redo command engine.
===========================================

Overview
-------------------------------------------
*A high‑precision visual Tkinter interface builder with a state‑driven core.*

 - Modular MVC subsystem design (Canvas, Selection, Widget, Attributes)
 - Central AppState mutation engine with batching and listeners
 - Command‑pattern undo/redo (keyboard + drag‑based)
 - Live widget rendering with soft/full updates
 - Fully custom overrideredirect titlebars
 - Smooth dragging with threshold + preview movement
 - Scrollbars appear only when needed (dynamic viewport logic)
 - Auto‑clamping of widget movement and creation
 - Attributes Panel with validation, anchor‑based limits, and dynamic resizing
 - Project‑based .tkui file format

Quick Start
-------------------------------------------
App.py:
 *Start application*
 - Creates the Tk root window
 - Initializes AppController

AppController:
 *Startup actions*
 - New Project → opens SetupWizard
 - Open Project (.tkui)
 - Save / Save As → writes ProjectDocument JSON
 - Export JSON (raw data)
 - Exit application
 - Keeps user theme and last directory

Designer:
 *Workspace usage*
 - Right‑click canvas → add widgets (Label, Entry, Button)
 - Click / CTRL+Click → select or multiselect
 - Drag widget → threshold + live preview movement
 - Drag empty area → rectangle selection
   > CTRL = additive rectangle selection
 - Scroll via mouse wheel or scrollbars
 - Use Attributes Panel to edit widget properties
 - Undo/redo all movement and attribute changes

===========================================
Module Map
-------------------------------------------

App Entry & Controller
-------------------------------------------
App.py:
 *Entry point*
 - Creates Tk root
 - Starts AppController

AppController.py:
 *Responsibilities*
 - Build startup window (custom titlebar)
 - Handle:
   > new project  
   > open project  
   > save / save as  
   > export JSON  
   > exit  
 - Prompt for unsaved changes
 - Launch SetupWizard or Designer
 - Maintain USER_THEME copies and last directory

Setup Wizard
-------------------------------------------
SetupWizard.py:
 *Collects*
 - Window title
 - Canvas width/height
 - Theme colors (background, label, entry, button)
 - Window icon

 *Provides*
 - Live previews
 - Validation for numeric dimensions
 - Custom titlebar

 *Outputs*
 - ProjectDocument (complete)
 - GridConfig

Designer (Main Editor)
-------------------------------------------
Designer.py:
 *Constructs*
 - CustomTitlebar
 - Toolbar (menus: file, edit, widget, grid, debug)
 - Scrollable canvas viewer + scrollbars
 - Attributes Panel (docked right)

 *Initializes*
 - AppState (model engine)
 - DesignerState (dirty flag, deletion flag, drag command)
 - CanvasView / CanvasController
 - SelectionView / SelectionController
 - WidgetView / WidgetController
 - AttributesPanelView / AttributesPanelController
 - ToolbarManager
 - CommandStack (undo/redo)

 *Manages*
 - Soft + full rendering
 - Grid visibility & appearance
 - Bounded canvas area with live resizing rules
 - Call tracer integration (debug)
 - Context menu for adding new widgets

===========================================
Managers (MVC Subsystems)
-------------------------------------------

Canvas System
-------------------------------------------
CanvasView.py:
 *Canvas view*
 - Owns the drawing canvas
 - Renders/clears grid lines
 - Maintains list of grid line IDs

CanvasController.py:
 *Input router*
 - Binds all keyboard + mouse input
 - Routes selection, movement, drag, alignment, project events
 - Routes snap‑to‑grid and grid styling changes
 - Handles context menu trigger

Selection System
-------------------------------------------
SelectionView.py:
 *Selection rendering*
 - Draws outlines for selected widgets
   > blue = selected  
   > red = last selected  
 - Draws/updates rectangle‑selection rectangle

SelectionController.py:
 *Selection + drag engine*
 - Single selection / toggle selection
 - Rectangle selection
 - Drag threshold detection
 - Incremental drag deltas → sent to MoveWidgetsTo
 - Hit‑testing for topmost widget
 - Normalizes and applies rectangle selection
 - Converts widget IDs ↔ model IDs

Widget System
-------------------------------------------
WidgetView.py:
 *Widget creation & mapping*
 - Create tk widget for Label/Entry/Button
 - Insert widget into canvas window
 - Maintain model_id ↔ widget_id mapping
 - Forward widget mouse events to canvas
 - Live update of text, color, anchor, geometry
 - Delete widgets cleanly

WidgetController.py:
 *Widget mutation logic*
 - Update widget attributes from attributes panel
 - Resize widgets when text changes (geometry recomputation)
 - Delete widgets (model + view)
 - Soft/full render entrypoint for changed models

Attributes Panel
-------------------------------------------
AttributesPanelView.py:
 *Attribute editing UI*
 - Builds rows of labels, entries, spinboxes, color previews, anchor picker
 - Silent‑update mode prevents recursive updates
 - Variable binding to propagate user edits

AttributesPanelController.py:
 *Validation & limits*
 - Builds panel dynamically from ATTRIBUTE_CONFIG
 - Computes x/y/width/height ranges based on anchor and canvas size
 - Updates spinbox limits after geometry/anchor changes

Toolbar Manager
-------------------------------------------
ToolbarManager.py:
 *Toolbar*
 - File menu (new/open/save/export/exit)
 - Edit menu (cut/copy/paste/undo/redo/select‑all)
 - Widgets menu (delete, snap to grid, align tools)
 - Grid menu (visualize/size/color)
 - Debug menu (call tracing, dirty/clean flags, widget count)

===========================================
Command System (Undo/Redo)
-------------------------------------------
BaseCommand.py:
 *Abstract interface*
 - execute()
 - undo()

CommandStack.py:
 *Undo/redo engine*
 - Execute → push undo stack
 - Undo → revert + push redo stack
 - Redo → re‑execute

MoveWidgets.py:
 *Keyboard movement (arrow keys)*
 - Stores original coordinates
 - Applies dx/dy to all selected widgets
 - Undo restores original positions

MoveWidgetsTo.py:
 *Drag‑based movement*
 - Stores original positions at drag start
 - preview_move(dx,dy) for incremental movement
 - freeze_final_positions() at drag end
 - Undo restores original positions

===========================================
Dataclasses
-------------------------------------------
ProjectDocument:
 *Project data*
 - version, title
 - width/height + icon_path
 - GridConfig
 - theme
 - widget_models
 - JSON read/write
 - Restores ID counters

GridConfig:
 *Grid properties*
 - size
 - color
 - visible

Widget Models:
 *LabelWidgetData / EntryWidgetData / ButtonWidgetData*
 - Auto‑incrementing IDs
 - Position/size/anchor/bg/fg/text
 - Dimensions assigned from preview widget measurements

DesignerState:
 *Designer runtime flags*
 - last click coords
 - drag start coords
 - is_dirty
 - is_deleting
 - active MoveWidgetsTo command

SelectionState:
 *Selection set*
 - selected_models
 - last_selected_model

WidgetDragState:
 *Widget drag tracking*
 - is_dragging
 - drag_start_coords
 - last incremental deltas

RectangleSelectionState:
 *Rectangle selection*
 - dragging flag
 - additive flag
 - start coords

===========================================
Utilities & Geometry
-------------------------------------------
UIComponents.py:
 *CustomTitlebar & icon loader*
 - Draggable window frame
 - Close button
 - Icon resizing (LANCZOS)

Geometry.py:
 *Coordinate helpers*
 - allowed_x_range / allowed_y_range (anchor aware)
 - clamp()
 - clamped_delta() for multi-widget bounding boxes
 - screen_offset_to_center_window()
 - nearest_in_bounds_grid_step()

===========================================
Theme & Constants
-------------------------------------------
Theme.py:
 *Themes*
 - USER_THEME (editable)
 - PROGRAM_THEME (static UI)

 *Constants*
 - Window min/max sizes
 - Canvas min/max sizes
 - Titlebar/toolbar sizes
 - Attributes panel size
 - Nudge distances (1px, 10px)
 - Grid size
 - Selection outline style
 - Drag threshold

===========================================
Key Features
-------------------------------------------
 *Complete GUI editing environment*
 - Pixel‑perfect widget placement
 - Anchor‑aware clamping
 - Live Attributes Panel
 - Multi-tier selection tools
 - Undo/redo for all movements
 - Soft/full rendering modes
 - Scrollable design surface
 - Custom titlebars for all windows
 - Drag engine: threshold, preview deltas, undo‑safe

===========================================
Shortcuts & Gestures
-------------------------------------------
 *Selection*
 - Click → select
 - CTRL+Click → toggle
 - Drag empty canvas → rectangle selection
   > CTRL = additive rectangle selection

 *Movement*
 - Arrow keys → 1px nudge
 - Shift+Arrow → 10px nudge

 *Dragging*
 - Drag widget → threshold + preview

 *Alignment*
 - CTRL+Arrow → align to last selected widget

 *Grid*
 - g → toggle visibility
 - CTRL+g → change grid size
 - Shift+G → change grid color

 *Project*
 - CTRL+N → new project
 - CTRL+O → open project
 - CTRL+S → save
 - CTRL+Shift+S → save as
 - CTRL+E → export JSON
 - ALT+F4 → exit

 *Editing*
 - CTRL+Z / CTRL+Y → undo/redo
 - CTRL+A → select all
 - Delete → delete selection

 *Scrolling*
 - Mouse wheel → vertical scroll
 - Shift+Mouse wheel → horizontal scroll

===========================================
Unit Tests
-------------------------------------------
 *TestProjectDocumentRoundtrip*
 - Ensures JSON load/save correctness
 - Restores widget IDs and counters

 *TestAddWidgetFromModel*
 - Confirms widget creation path + geometry measurement

 *TestMoveWidget*
 - Tests movement operations update model + canvas

 *TestUndoRedoMoveWidget*
 - Keyboard movement undo/redo

 *TestUndoRedoMoveWidgetTo*
 - Drag‑based movement undo/redo

===========================================
File Format (.tkui)
-------------------------------------------
 *JSON structure*
 - Project metadata
 - Grid configuration
 - Theme dictionary
 - Widget models
 - ID counters for correct reconstruction

===========================================
Notes
-------------------------------------------
 *Internal behavior*
 - Selection outlines always match widget geometry
 - Attributes Panel visible only when exactly one widget selected
 - Grid redraws when size/color/visibility changes
 - Drag preview uses incremental deltas to maintain stability
 - Scrollbars appear only when canvas exceeds viewport
 - Designer window auto‑sizes to canvas, respecting min/max constraints