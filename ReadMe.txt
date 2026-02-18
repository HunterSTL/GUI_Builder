===========================================
Tkinter GUI Builder – README
-------------------------------------------
A fully interactive, canvas‑based Tkinter GUI designer featuring pixel‑accurate
widget placement, modular architecture, dynamic attributes editing, selection
tools, custom draggable titlebars, a scrollable design surface, and a robust
undo/redo system.
===========================================


Overview
-------------------------------------------
*A high‑precision visual Tkinter interface builder with a state‑driven core.*

   -Modular Managers for clean architecture
   -Shared callback map for decoupled interaction
   -Live widget rendering with full or soft updates
   -Custom overrideredirect titlebars
   -Smooth drag system with thresholds + preview deltas
   -Scrollbars appear only when needed
   -Attributes Panel with validation and dynamic limits


Quick Start
-------------------------------------------
App.py:
*Start application*
   -Creates Tk root window
   -Initializes AppController

AppController:
*Startup actions*
   -New Project
   -Open Project
   -Save / Save As
   -Export JSON
   -Exit application
   -Manages theme copies and last directory

Designer:
*Workspace usage*
   -Right-click canvas → add widgets
   -Click / CTRL+Click → select or multiselect
   -Drag widget → threshold + preview movement
   -Drag empty area → rectangle selection
      >CTRL = additive rectangle selection
   -Scroll via mouse wheel or scrollbars
   -Use Attributes Panel to edit widgets

===========================================
Module Map
-------------------------------------------

App Entry & Controller
-------------------------------------------
App.py:
*Entry point*
   -Creates Tk root
   -Starts AppController

AppController.py:
*Responsibilities*
   -Build startup window
   -Handle:
      >new project
      >open project
      >save / save as
      >export JSON
      >exit
   -Prompt for unsaved changes
   -Launch SetupWizard or Designer
   -Keep a clean copy of USER_THEME

Setup Wizard
-------------------------------------------
SetupWizard.py:
*Collects*
   -Window title
   -Canvas width/height
   -Theme colors
   -Window icon

*Provides*
   -Live previews of colors
   -Theming for background, labels, entries, buttons
   -Input validation for dimensions

*Outputs*
   -ProjectDocument
   -GridConfig for the canvas

Designer (Main Editor)
-------------------------------------------
Designer.py:
*Constructs*
   -CustomTitlebar
   -Toolbar
      >file menu
      >edit menu
      >widget menu
      >grid menu
      >debug menu
   -Scrollable canvas viewer
   -Attributes panel

*Initializes*
   -CanvasManager
   -SelectionManager
   -WidgetManager
   -AttributesPanelManager
   -ToolbarManager

*Maintains*
   -DesignerState
      >dirty flag
      >deleting state
      >active drag command
      >last click coords

*Loads*
   -All widget models into the canvas
   -Grid visibility and properties

*Controls*
   -Undo/redo system (CommandStack)
   -Soft vs full rendering
   -Scrollbar visibility logic
   -Window sizing based on canvas + constraints

===========================================
Managers (Core Editing Logic)
-------------------------------------------

CanvasManager.py:
*Canvas system*
   -Creates the design canvas
   -Draws and clears grid lines
   -Computes scrollregion
   -Shows/hides scrollbars as needed
   -Binds keyboard shortcuts:
      >1px/10px movement
      >alignment
      >grid tools
      >copy/paste/cut
      >undo/redo
      >project actions

SelectionManager.py:
*Selection engine*
   -Single selection
   -Toggle selection
   -Multi-selection
   -Rectangle selection
      >CTRL = additive rectangle selection
   -Find top‑most widget at click

*Drag system*
   -Movement threshold detection
   -Incremental drag deltas
   -WidgetDragState tracking
   -Re-entry protection for drag events

*Outlines*
   -Draws selection rectangles
      >blue = selected
      >red = last selected
   -Refreshes outlines on size/position change

WidgetManager.py:
*Widget creation & updates*
   -Create widgets from user actions or project models
   -Insert new widgets into canvas
   -Store model↔widget mapping
   -Update:
      >x / y position
      >width / height
      >text
      >colors (bg/fg)
      >anchor
   -Forward widget events back to canvas
   -Delete widgets cleanly

AttributesPanelManager.py:
*Attribute editing UI*
   -Creates UI controls from ATTRIBUTE_CONFIG
   -Provides:
      >text entries
      >validated spinboxes
      >color preview blocks
      >anchor selector
   -Silent-update mode to avoid recursive calls
   -Updates spinbox limits after size/anchor changes

ToolbarManager.py:
*Top toolbar construction*
   -File menu
   -Edit menu
   -Widgets menu
   -Grid menu
   -Debug menu
   -Menus call into Designer callbacks

===========================================
Commands (Undo/Redo System)
-------------------------------------------

BaseCommand:
*Abstract interface*
   -execute()
   -undo()

CommandStack:
*Undo/redo engine*
   -Execute command and push to undo stack
   -Undo → pop & revert
   -Redo → reapply executed commands

MoveWidgets:
*Keyboard movement command*
   -Store original widget positions
   -Apply (dx, dy) delta per widget
   -Undo restores original

MoveWidgetsTo:
*Drag-based movement*
   -preview_move(dx, dy) during drag
   -freeze_final_positions() when drag ends
   -Undo restores original pre-drag positions

===========================================
Dataclasses
-------------------------------------------

ProjectDocument:
*Project-level data*
   -version
   -title
   -width / height
   -icon_path
   -theme
   -GridConfig
   -widget_models list
   -JSON serialization & deserialization
   -Restores ID counters

GridConfig:
*Grid properties*
   -size
   -color
   -visibility

WidgetModels:
*Widget definitions*
   -BaseWidgetData
   -LabelWidgetData
   -EntryWidgetData
   -ButtonWidgetData
   -create_id()
   -Store positioning, colors, text, size, anchor

DesignerState:
*Designer runtime state*
   -last click coords
   -drag start coords
   -window coords
   -is_dirty flag
   -is_deleting
   -active drag command

RectangleSelectionState:
*Rectangle selection info*
   -rectangle object id
   -start coords
   -dragging/additive flags

WidgetDragState:
*Drag tracking*
   -start coords
   -end coords
   -accumulated deltas
   -drag active flag

===========================================
Utilities & Geometry
-------------------------------------------

UIComponents.py:
*load_icon*
   -Loads PNG/JPG/ICO files
   -Converts to proper Tk PhotoImage
   -Resizes with high-quality resampling

*CustomTitlebar*
   -Fully custom draggable title bar
   -Text + icon + close button
   -Used for startup window, setup wizard, and designer

Geometry.py:
*Coordinate and boundary helpers*
   -allowed_x_range / allowed_y_range
      >anchor‑aware boundary calculation
   -clamp(value, min, max)
   -clamped_delta(dx, dy) to keep widgets inside canvas
   -screen_offset_to_center_window()

===========================================
Theme & Constants
-------------------------------------------

Theme.py:
*Themes*
   -USER_THEME (customizable)
   -PROGRAM_THEME (static UI theme)

*Constants*
   -Window min/max sizes
   -Canvas min/max sizes
   -Titlebar / toolbar sizes
   -Attributes panel width
   -Nudge distances (1px, 10px)
   -Grid size
   -Selection outline styling
   -Drag activation threshold

===========================================
Key Features
-------------------------------------------

*Complete GUI building environment*
   -Pixel‑perfect widget placement
   -Accurate snap‑to‑grid tools
   -Single/multi/toggle/rectangle selection
   -Live Attributes Panel with validation
   -Undo/redo for all movement operations
   -Soft and full rendering systems
   -Keyboard and mouse workflows
   -Scrollable canvas
   -Custom titlebars for all windows

===========================================
Shortcuts & Gestures
-------------------------------------------

*Selection*
   -Click → select
   -CTRL+Click → toggle
   -Drag empty canvas → rectangle selection
      >CTRL keeps existing selection

*Movement*
   -Arrow keys → 1px nudge
   -Shift+Arrow → 10px nudge

*Dragging*
   -Drag widget → threshold + preview

*Alignment*
   -CTRL+Arrow → align to last selected

*Grid*
   -g → toggle visibility
   -CTRL+g → change grid size
   -Shift+G → change grid color

*Project*
   -CTRL+N → new project
   -CTRL+O → open project
   -CTRL+S → save
   -CTRL+Shift+S → save as
   -CTRL+E → export JSON
   -ALT+F4 → exit

*Editing*
   -CTRL+Z / CTRL+Y → undo/redo
   -CTRL+A → select all
   -Delete → delete widgets

*Scrolling*
   -Mouse wheel → vertical scroll
   -Shift+Mouse wheel → horizontal scroll

===========================================
Unit Tests
-------------------------------------------

*TestProjectDocumentRoundtrip*
   -Verifies accurate JSON save/load
   -Checks restoration of widget models and ID counters

*TestAddWidgetFromModel*
   -Confirms correct creation of widgets from models

*TestMoveWidget*
   -Ensures movement operations update both model and canvas

*TestUndoRedoMoveWidget*
   -Validates undo/redo for keyboard‑based movement

*TestUndoRedoMoveWidgetTo*
   -Validates drag‑movement undo/redo workflow

===========================================
File Format (.tkui)
-------------------------------------------

*Stored as JSON containing*
   -Project metadata
   -Grid configuration
   -Theme settings
   -List of widget models
   -ID counters for reconstruction

===========================================
Notes
-------------------------------------------

*Internal behavior details*
   -Selection outlines always follow widget geometry
   -Attributes Panel visible only when exactly one widget is selected
   -Grid redraw is dynamic on color/size/visibility changes
   -Incremental drag deltas provide stable preview and undo‑safety
   -Scrollbars appear only when canvas exceeds viewport
===========================================