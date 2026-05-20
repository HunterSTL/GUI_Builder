# Tkinter GUI Builder
A desktop application for visually designing Tkinter user interfaces using a canvas based editor.  
The tool allows creating, positioning and configuring Tkinter widgets, then saving the layout into a structured project file.

## 1 Overview
This project implements a GUI builder for Tkinter using a structured architecture composed of:

* A central application controller
* A designer window for editing UI layouts
* A model layer representing project state
* A command system for undo and redo functionality
* An event system for decoupled communication
* A view and controller separation for UI logic

The application stores layouts in a custom JSON based ```.tkui``` file format.

## 2 Features
### 2.1 Project Management
* Create new projects via a setup wizard
* Open existing ```.tkui``` project files
* Save and Save As functionality
* Unsaved changes prompt on destructive actions (new, open, exit)

### 2.2 Widget Editing
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

### 2.3 Editing Operations
* Delete
* Cut, copy and paste
* Undo and redo

### 2.4 Attributes Panel
* Edit widget properties live:
    * Position (x, y)
    * Size (width, height)
    * Text where applicable
    * Colors (bg, fg)
    * Anchor

### 2.5 Grid System
* Toggle grid visibility
* Change grid size
* Change grid color

## 3 Architecture
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

## 4 Running the Application
### 4.1 Requirements
* Python 3
* Tkinter
* Pillow

### 4.2 Run
```
python App.py
```

## 5 File Format (.tkui)
Projects are saved as JSON containing:
* Project metadata (title, size, icon)
* Grid configuration
* Theme configuration
* Widget models
* ID counters

## 6 Controls
### 6.1 Mouse
* Left click → Select widget
* [Ctrl] + click → Add to selection
* Drag → Move widgets
* Drag empty area → Rectangle select
* Right click → Add widget menu

### 6.2 Keyboard

#### 6.2.1 Project
* [Ctrl] + [N] → New project
* [Ctrl] + [O] → Open project
* [Ctrl] + [S] → Save
* [Ctrl] + [Shift] + [S] → Save As

#### 6.2.2 App
* [Alt] + [F4] → Exit

#### 6.2.3 Edit
* [Ctrl] + [C] → Copy
* [Ctrl] + [V] → Paste
* [Ctrl] + [X] → Cut
* [Ctrl] + [Z] → Undo
* [Ctrl] + [Y] → Redo

#### 6.2.4 Widget 
* Arrow keys → Nudge
* [Shift] + Arrow keys → Big nudge
* [Ctrl] + Arrow keys → Align with last selected
* [S] → Snap to grid
* [Delete] → Delete selected widgets

#### 6.2.5 Grid
* [G] → Toggle grid
* [Ctrl] + [G] → Change grid size
* [Shift] + [G] → Change grid color

#### 6.2.6 Debug
* [Ctrl] + [Shift] + [T] → Toggle call tracing
* [Ctrl] + [D] → Set dirty
* [Ctrl] + [Shift] + [D] → Set clean
* [#] → Print widget count
* [F1] → Print clipboard
* [F2] → Print command stack
* [F3] → Print selection
* [F4] → Print bounding boxes
* [F5] → Print id counters

## 7 Testing
Run unit tests:
```
python UnitTests.py
```

## 8 Summary

This project is a structured Tkinter GUI editor with:

* Centralized state management
* Event driven architecture
* Undo and redo functionality via command pattern
* Clear separation of view, controller and model
