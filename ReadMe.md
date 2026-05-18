# Tkinter GUI Builder
A desktop application for visually designing Tkinter user interfaces using a canvas based editor.  
The tool allows creating, positioning and configuring Tkinter widgets, then saving the layout into a structured project file.

## Overview
This project implements a GUI builder for Tkinter using a structured architecture composed of:

* A central application controller
* A designer window for editing UI layouts
* A model layer representing project state
* A command system for undo and redo functionality
* An event system for decoupled communication
* A view and controller separation for UI logic

The application stores layouts in a custom JSON based ```.tkui``` file format.

## Features
### Project Management
* Create new projects via a setup wizard
* Open existing ```.tkui``` project files
* Save and Save As functionality
* Unsaved changes prompt on destructive actions (new, open, exit)

### Widget Editing
Supports the following widget types:
* Label
* Entry
* Button

**Capabilities:**
* Add widgets via right click context menu
* Move widgets (drag or keyboard nudge)
* Resize indirectly via text
* Edit attributes dynamically using the attributes panel
* Snap widgets to grid
* Align widgets (left, right, top, bottom)
* Multi select (Ctrl click or rectangle selection)

### Editing Operations
* Delete
* Cut, copy and paste
* Undo and redo

### Attributes Panel
* Edit widget properties live:
    * Position (x, y)
    * Size (width, height)
    * Text where applicable
    * Colors (bg, fg)
    * Anchor

### Grid System
* Toggle grid visibility
* Change grid size
* Change grid color

## Architecture
```
Application Root
└── AppController
    ├── Tk Root Window
    ├── Global EventBus (app + project events)
    ├── Startup UI
    ├── SetupWizard
    └── Designer (created per project)
        ├── Tk Toplevel Window
        ├── Event System
        │   ├── App EventBus (shared)
        │   ├── Designer EventBus (local)
        │   └── EventRouter (dispatch layer)
        │
        ├── State Layer
        │   ├── AppState
        │   │   ├── ProjectDocument
        │   │   │   ├── GridConfig
        │   │   │   ├── Theme
        │   │   │   ├── WidgetModels
        │   │   │   │   ├── LabelWidgetData
        │   │   │   │   ├── EntryWidgetData
        │   │   │   │   └── ButtonWidgetData
        │   │   │   └── IdCounters
        │   │   └── SelectionState
        │   │
        │   └── DesignerState
        │       └── (dirty flag, last click coords)
        │
        ├── Command System (undo and redo functionality)
        │   ├── CommandStack
        │   ├── Commands
        │   │   ├── MoveWidgets
        │   │   ├── MoveWidgetsTo (drag)
        │   │   ├── DeleteWidgets
        │   │   ├── PasteWidgetsFromClipboard
        │   │   ├── AlignWidgets
        │   │   └── SnapWidgetsToGrid
        │
        ├── Actions Layer (domain semantics)
        │   ├── Actions (facade)
        │   ├── EditActions
        │   │   ├── delete
        │   │   ├── copy
        │   │   ├── paste
        │   │   ├── cut
        │   │   ├── undo
        │   │   ├── redo
        │   │
        │   └── WidgetActions
        │       ├── nudge
        │       ├── drag (start/preview/commit)
        │       ├── snap to grid
        │       └── align
        │
        ├── Controller Layer (input + orchestration)
        │   ├── CanvasController
        │   │   ├── keyboard bindings
        │   │   └── event routing
        │   │
        │   ├── SelectionController
        │   │   ├── click selection
        │   │   ├── rectangle selection
        │   │   └── drag gestures
        │   │
        │   ├── WidgetController
        │   │   ├── render coordination
        │   │   └── attribute mutations
        │   │
        │   ├── AttributesPanelController
        │   │   ├── dynamic UI generation
        │   │   └── input constraints
        │   │
        │   └── ToolbarController
        │       └── menu construction + event wiring
        │
        ├── View Layer (pure Tkinter)
        │   ├── CanvasView
        │   │   └── grid rendering
        │   │
        │   ├── WidgetView
        │   │   ├── widget creation
        │   │   ├── widget ←→ model mapping
        │   │   └── event forwarding
        │   │
        │   ├── SelectionView
        │   │   ├── outlines
        │   │   └── selection rectangle
        │   │
        │   ├── AttributesPanelView
        │   │   └── attribute widgets
        │   │
        │   └── ToolbarView
        │       └── menus + UI shell
        │
        ├── Utility Layer
        │   ├── Geometry
        │   │   ├── bounding boxes
        │   │   ├── clamping
        │   │   └── grid snapping
        │   │
        │   ├── CustomTitlebar
        │   ├── CallTracer
        │   ├── Direction / Edge enums
        │   └── WidgetType enum
        │
        └── Rendering Pipeline
            ├── Full Render
            │   ├── WidgetController.render_full()
            │   ├── CanvasController.render_grid()
            │   └── SelectionController.render_all_outlines()
            │
            └── Soft Render
                ├── WidgetController.render_soft()
                └── SelectionController.render_outline_for()

```

## Running the Application
### Requirements
* Python 3
* Tkinter
* Pillow

### Run
```
python App.py
```

## File Format (.tkui)
Projects are saved as JSON containing:
* Project metadata (title, size, icon)
* Grid configuration
* Theme configuration
* Widget models
* ID counters

## Controls
### Mouse
* Left click → Select widget
* [Ctrl] + click → Add to selection
* Drag → Move widgets
* Drag empty area → Rectangle select
* Right click → Add widget menu

### Keyboard

#### Project
* [Ctrl] + [N] → New project
* [Ctrl] + [O] → Open project
* [Ctrl] + [S] → Save
* [Ctrl] + [Shift] + [S] → Save As

#### App
* [Alt] + [F4] → Exit

#### Edit
* [Ctrl] + [C] → Copy
* [Ctrl] + [V] → Paste
* [Ctrl] + [X] → Cut
* [Ctrl] + [Z] → Undo
* [Ctrl] + [Y] → Redo

#### Widget 
* Arrow keys → Nudge
* [Shift] + Arrow keys → Big nudge
* [Ctrl] + Arrow keys → Align with last selected
* [S] → Snap to grid
* [Delete] → Delete selected widgets

#### Grid
* [G] → Toggle grid
* [Ctrl] + [G] → Change grid size
* [Shift] + [G] → Change grid color

#### Debug
* [Ctrl] + [Shift] + [T] → Toggle call tracing
* [Ctrl] + [D] → Set dirty
* [Ctrl] + [Shift] + [D] → Set clean
* [#] → Print widget count
* [F1] → Print clipboard
* [F2] → Print command stack
* [F3] → Print selection
* [F4] → Print bounding boxes
* [F5] → Print id counters

## Testing
Run unit tests:
```
python UnitTests.py
```

## Summary

This project is a structured Tkinter GUI editor with:

* Centralized state management
* Event driven architecture
* Undo and redo functionality via command pattern
* Clear separation of view, controller and model
