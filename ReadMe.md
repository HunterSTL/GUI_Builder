# Tkinter GUI Builder

A desktop application for visually designing Tkinter user interfaces with a canvas-based editor.  
It supports creating, selecting, positioning, aligning, styling and organizing widgets, with project persistence through a validated JSON-based `.tkui` format.

## Features

### Project management

* Create projects through a setup wizard
* Configure the project title, canvas dimensions, colors and icon
* Open existing `.tkui` project files
* Save projects or save them under a new name
* Write project files atomically to reduce the risk of file corruption
* Prompt before creating, opening, or exiting when unsaved changes exist
* Indicate unsaved changes with an asterisk in the designer window title

### Supported widgets

* Label
* Entry
* Button

Widgets can be added from the canvas context menu.  
New labels and buttons prompt for their initial text, while widget colors are inherited from the project theme.

### Selection and movement

* Select a widget with the left mouse button
* Add or remove widgets from the selection with `Ctrl` + click
* Select enclosed widgets by dragging a rectangle across an empty canvas area
* Select all widgets with `Ctrl` + `A`
* Drag one or more selected widgets
* Nudge selected widgets with the arrow keys
* Align selected widgets to the last selected widget
* Snap selected widgets to the nearest valid grid position
* Keep widgets within the canvas during movement, alignment, snapping, pasting, resizing and anchor changes

The last selected widget is used as the alignment reference and is shown with a distinct selection outline.

### Editing

* Add and delete widgets
* Cut, copy and paste widgets
* Paste copied widgets at the current pointer position
* Undo and redo command-based changes
* Edit widget attributes live in the attributes panel

Supported attributes depend on the widget type and include:

* Widget ID, read-only
* X and Y coordinates
* Width and height
* Text for labels and buttons
* Background and foreground colors
* Anchor

### Grid

* Show or hide the grid
* Change the grid size
* Change the grid color

### Debugging

* Application call tracing
* Live widget count output
* Clipboard output
* Command stack output
* Selection output
* Widget bounding-box output
* ID-counter output

## Requirements

* Python 3.10 or newer
* Tkinter
* Pillow

## Running the application

Run the application from the project root:

```
python App.py
```

The startup window provides three options:

* **Open project** opens an existing `.tkui` file
* **New project** opens the project setup wizard
* **Exit** closes the application

## Creating a project

The setup wizard collects:

* Project title
* Canvas width and height
* Canvas background color
* Default label background and text colors
* Default entry background and text colors
* Default button background and text colors
* Optional project icon

The canvas must be between `200 x 200` and `5000 x 5000` pixels.  
After the settings are valid, select **Launch designer**.

## Using the designer

### Adding widgets

Right-click the canvas and choose one of the following commands:

* **Add Label**
* **Add Entry**
* **Add Button**

Labels and buttons request text before creation.  
The widget is placed at the right-click position and clamped to the canvas if necessary.

### Selecting widgets

* Left-click a widget to select it exclusively
* Hold `Ctrl` while clicking to toggle it in the current selection
* Drag across an empty area to select all fully enclosed widgets
* Hold `Ctrl` while rectangle-selecting to add enclosed widgets to the current selection
* Click an empty area to clear the selection

The attributes panel is available only when exactly one widget is selected.

### Editing attributes

When one widget is selected, use the attributes panel to edit its properties.  
Changes are rendered live and committed as one undoable edit when the interaction finishes.

Changing text can update the required widget dimensions.  
Changes to dimensions or anchors can also adjust the widget position to keep it inside the canvas.

### Copying and pasting

Copy stores serialized widget snapshots in the designer clipboard.  
Paste places copies relative to the current pointer position, assigns new IDs, preserves the arrangement of multiple copied widgets and clamps the group to the canvas.

## Controls

### Mouse

| Input | Action |
| --- | --- |
| Left-click widget | Select widget |
| `Ctrl` + left-click widget | Toggle widget in selection |
| Drag selected widget | Move the current selection |
| Drag empty canvas area | Rectangle-select enclosed widgets |
| `Ctrl` + drag empty canvas area | Add enclosed widgets to selection |
| Right-click canvas | Open the add-widget menu |
| Mouse wheel | Scroll vertically |
| `Shift` + mouse wheel | Scroll horizontally |

### Project and application

| Shortcut | Action |
| --- | --- |
| `Ctrl` + `N` | New project |
| `Ctrl` + `O` | Open project |
| `Ctrl` + `S` | Save project |
| `Ctrl` + `Shift` + `S` | Save project as |
| `Alt` + `F4` | Exit application |

### Editing and selection

| Shortcut | Action |
| --- | --- |
| `Delete` | Delete selected widgets |
| `Ctrl` + `C` | Copy selected widgets |
| `Ctrl` + `V` | Paste at the pointer position |
| `Ctrl` + `X` | Cut selected widgets |
| `Ctrl` + `Z` | Undo |
| `Ctrl` + `Y` | Redo |
| `Ctrl` + `A` | Select all widgets |

### Widget positioning

| Shortcut | Action |
| --- | --- |
| Arrow key | Nudge selection by 1 pixel |
| `Shift` + arrow key | Nudge selection by 10 pixels |
| `Ctrl` + left arrow | Align left edges |
| `Ctrl` + right arrow | Align right edges |
| `Ctrl` + up arrow | Align top edges |
| `Ctrl` + down arrow | Align bottom edges |
| `S` | Snap selection to grid |

Alignment uses the last selected widget as the reference.

### Grid

| Shortcut | Action |
| --- | --- |
| `G` | Show or hide grid |
| `Ctrl` + `G` | Change grid size |
| `Shift` + `G` | Change grid color |

### Debug

| Shortcut | Action |
| --- | --- |
| `Ctrl` + `Shift` + `T` | Toggle call tracing |
| `#` | Print live widget count |
| `F1` | Print clipboard |
| `F2` | Print command stack |
| `F3` | Print selection |
| `F4` | Print widget bounding boxes |
| `F5` | Print ID counters |

## Project file format

Projects use the `.tkui` extension and contain UTF-8 JSON.  
Version `1` has the following top-level structure:

```
{
  "version": 1,
  "title": "Example Project",
  "width": 800,
  "height": 600,
  "icon_path": "icon.ico",
  "grid": {
    "size": 10,
    "color": "#888888",
    "visible": false
  },
  "theme": {
    "background_color": "#404040",
    "label_color": "#404040",
    "label_text_color": "#FFFFFF",
    "entry_color": "#606060",
    "entry_text_color": "#FFFFFF",
    "button_color": "#505050",
    "button_text_color": "#FFFFFF"
  },
  "widgets": [],
  "id_counters": {
    "label": 1,
    "entry": 1,
    "button": 1
  }
}
```

Widget entries contain their type, ID, coordinates, colors, dimensions and anchor.  
Labels and buttons also contain text.

Project loading validates:

* Required and unexpected keys
* Project format version
* Project title and canvas dimensions
* Grid values
* Theme colors
* Widget types and attributes
* Widget dimensions and coordinates
* Anchor values
* Duplicate widget IDs
* ID-counter values

Invalid or corrupted files are rejected before they become application state.

## Architecture

The application follows a layered, event-driven MVC design extended with centralized state mutation and command-based undo and redo.

```
App.py
└── AppController
    ├── Startup window
    ├── Project lifecycle and persistence
    ├── Application EventBus
    ├── SetupWizard
    └── Designer
        ├── EventRouter
        ├── Designer EventBus
        ├── Actions
        │   ├── EditActions
        │   └── WidgetActions
        ├── CommandStack
        │   ├── AddWidget
        │   ├── DeleteWidgets
        │   ├── DragWidgets
        │   ├── EditWidget
        │   ├── NudgeWidgets
        │   ├── PasteWidgetsFromClipboard
        │   ├── AlignWidgets
        │   └── SnapWidgetsToGrid
        ├── AppState
        │   └── ProjectDocument
        │       ├── GridConfig
        │       ├── ProjectTheme
        │       ├── Widget models
        │       └── IdCounters
        ├── CanvasController
        ├── Components
        │   ├── Toolbar
        │   └── AttributesPanel
        └── Views
            ├── CanvasView
            ├── WidgetView
            └── SelectionView
```

### Data flow

Persistent state changes follow this direction:

```
User input
→ CanvasController or Toolbar
→ EventRouter
→ Designer event handler
→ Action
→ CommandStack
→ Command
→ AppState
→ Designer state-change subscriber
→ View update
```

### Main responsibilities

#### AppController

- Owns the root window and application-wide event bus
- Coordinates new, open, save, save-as and exit operations
- Manages the active setup wizard and designer
- Handles unsaved-change prompts

#### Designer

- Constructs and coordinates the editor
- Connects events to actions
- Subscribes to `AppState` changes
- Performs incremental rendering
- Owns transient editor data such as the clipboard and last right-click position

#### AppState

- Owns the active `ProjectDocument`
- Applies all mutations to owned widget models
- Tracks dirty, removed, selected and grid-changed state
- Resolves widgets by ID to avoid stale-reference mutations
- Batches related mutations into one notification
- Provides widget and selection query APIs

#### Actions

Actions interpret editor intent, reject no-op operations, prepare commands and execute them through the command stack.

#### Commands

Commands snapshot the state required for deterministic execution, undo and redo.  
Interactive commands, such as dragging and attribute editing, apply live changes and record their final state before entering command history.

#### Views

- `CanvasView` owns the inner design canvas and grid rendering
- `WidgetView` creates and updates Tk widgets while maintaining identity mappings
- `SelectionView` renders selection outlines and the rectangle-selection marquee

## Project structure

```
GUI_Builder/
├── App.py
├── AppController.py
├── AppState.py
├── Designer.py
├── SetupWizard.py
├── actions/
├── commands/
├── components/
├── controller/
├── documents/
├── events/
├── model/
├── tests/
│   ├── unit/
│   └── validation/
├── utility/
└── view/
```

Additional development conventions are documented in:

* `documents/CodingConventions.md`
* `documents/CommitMessageConventions.md`

## Testing

### Unit tests

From the project root, run:

```
python tests/unit/UnitTests.py
```

The unit suite covers project serialization, widget rendering and movement and undo/redo behavior for core commands.

### Validation tests

Run the validation suite with:

```
python tests/validation/ValidationTestSuite.py
```

The validation suite checks input boundaries, domain invariants, error messages, unsupported operations and inconsistent rendering mappings.

