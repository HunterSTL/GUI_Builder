# Tkinter GUI Builder
A desktop application for visually designing Tkinter user interfaces with a canvas-based editor.  
It supports creating, selecting, positioning, aligning, styling and organizing widgets, with project persistence through a validated JSON-based `.tkui` format.

## Requirements
* Python 3.10 or newer
* Tkinter
* Pillow

## Running the application
Run the application from the project root:

```
python app.py
```

The startup window provides three options:

* `Open project` opens an existing `.tkui` file
* `New project` opens the project setup wizard
* `Exit` closes the application

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
After the settings are valid, select `Launch designer`.

## Using the designer
### Adding widgets

Right-click the canvas and choose one of the following commands:

* `Add Label`
* `Add Entry`
* `Add Button`

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
Copy stores serialized widgets in the designer clipboard.  
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
| Right-click during drag | Abort gesture |
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

### Properties
| Shortcut | Action |
| --- | --- |
| `Ctrl` + `T` | Change project title |

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
Version `1` has the following structure:

```
{
  "version": 1,
  "title": "Example Project",
  "width": 800,
  "height": 600,
  "icon_path": "icon.ico",
  "grid": {},
  "theme": {},
  "widgets": [],
  "id_counters": {}
}
```

### Top-level sections
* `grid` stores grid settings
* `theme` stores project-wide widget colors
* `widgets` contains all widget definitions
* `id_counters` stores the next available ID value for each widget type

Widget entries contain their type, ID, coordinates, colors, dimensions and anchor.  
Labels and buttons also contain text.

### Validation
Project files are validated before loading to detect invalid or corrupted data.

**Validation includes:**
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
The application follows a layered MVC architecture extended with a centralized mutation engine, an event system and a command system.

```
app.py
└── AppController
    ├── Startup Window
    ├── SetupWizard
    ├── Project Loading / Saving
    ├── Application EventBus
    └── Designer
        ├── EventRouter
        ├── Designer EventBus
        ├── AppState
        │   └── ProjectDocument
        │       ├── GridConfig
        │       ├── ProjectTheme
        │       ├── IdCounters
        │       └── Widget[]
        │           ├── LabelWidget
        │           ├── EntryWidget
        │           └── ButtonWidget
        ├── CommandStack
        ├── ActionGroups
        │   ├── EditActions
        │   ├── WidgetActions
        │   ├── GridActions
        │   └── PropertiesActions
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
User Input
→ Controller
→ Event
→ Designer
→ Action
→ Commands
→ CommandStack
→ AppState
→ View  
```

### Main responsibilities
#### AppController
* Owns the root window and application-wide event bus
* Coordinates new, open, save, save-as and exit operations
* Manages the active setup wizard and designer
* Handles unsaved-change prompts

#### Designer
* Constructs and coordinates the editor
* Connects events to actions
* Subscribes to `AppState` changes
* Performs incremental rendering
* Owns transient editor data such as the clipboard and last right-click position

#### AppState
* Owns the active `ProjectDocument`
* Applies all mutations to owned widgets
* Tracks dirty and removed widgets as well as selection and grid changes
* Resolves widgets by ID to avoid mutating stale references
* Batches related mutations into one notification
* Provides widget and selection query APIs

#### Actions
* Interpret editor intent
* Reject no-op operations
* Prepare commands
* Execute commands through the command stack

#### Commands
Commands snapshot the state required for deterministic execution, undo and redo.  
Interactive commands, such as dragging and attribute editing, apply live changes and record their final state before entering command history.

#### Views
* `CanvasView` owns the inner design canvas and grid rendering
* `WidgetView` creates and updates Tk widgets while maintaining identity mappings
* `SelectionView` renders selection outlines and the rectangle-selection marquee

## Project structure

```
GUI_Builder/
├── app.py
├── app_controller.py
├── app_state.py
├── designer.py
├── run_tests.py
├── setup_wizard.py
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

* `documents/coding_conventions.md`
* `documents/commit_message_conventions.md`

## Testing
Run the test suites from the project root:

```
python run_tests.py
```

### Unit tests
The unit test suite covers project serialization, widget rendering and movement and undo/redo behavior for commands.

### Validation tests
The validation test suite checks input boundaries, domain invariants, error messages, unsupported operations and inconsistent rendering mappings.

