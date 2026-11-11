# Coding and Architecture Conventions
This document defines the architectural and coding conventions used throughout the GUI_Builder codebase.  
The goal of these conventions is to make the codebase coherent, readable and architecturally sound.

## 1 Core Principles
Principles that apply globally and must not be violated.

**Single source of truth:**  
AppState owns application state and all mutations of AppState owned models must go through AppState

**Unidirectional data flow:**  
User Input → Controller → Event → Designer → Action → Commands → CommandStack → AppState → View  
The flow defines the direction of data, not a list of steps that every operation must use.

**Deterministic behaviour:**  
Given the same inputs, the system must always produce the same results

**No hidden mutations:**  
All state changes must be explicit and observable

**Minimum viable complexity:**  
Code must use the simplest structure that preserves correctness, readability and robustness.

## 2 Architecture
The codebase follows a layered MVC architecture extended with a centralized mutation engine, an event system and a command system.  
Each component has clearly defined responsibilities and allowed dependencies.

### 2.1 Model
Represents application data such as `ProjectDocument` and `Widget`.

* Must only contain data, serialization logic and identity management (IDs)
* May depend on standard library modules, dataclasses, enums and helpers that do not depend on application state or UI
* Must not depend on anything else

#### 2.1.1 Widget IDs
Uniquely identify `Widget` instances.

* Must be unique within a project
* Must be created and assigned exactly once
* Must not be modified after a widget has been added to the project

### 2.2 View
Responsible for rendering model state.

* Must only contain Tk rendering code
* Must not mutate models

### 2.3 Controller
Translates user input (mouse, keyboard and menu interactions) into domain intent.

* Must emit events via `EventRouter`
* Must not mutate models
* Must not perform rendering
* Must not execute commands directly

### 2.4 AppState
The central mutation engine responsible for applying all mutations to `AppState` owned models.

* Must apply all state changes to `AppState` owned models
* Must reject mutations for unknown `Widget` IDs
* Must resolve `Widget` instances by ID before mutating them to avoid mutating stale references
* Must track dirty and removed `Widget` instances
* Must track selection and grid changes
* Must notify subscribers after state changes
* Must provide batching for grouped mutations
* Must provide O(1) `Widget` lookup by ID

#### 2.4.1 Notification System
Notifies `AppState` subscribers of state changes.

* Must contain the IDs of all modified `Widget` instances in `dirty_widget_ids`
* Must contain the IDs of all removed `Widget` instances in `removed_widget_ids`
* Must indicate selection outline and attributes panel refresh requirements with the `selection_change` flag
* Must indicate grid refresh requirements with the `grid_change` flag
* Must reset all transient flags and clear all transient change sets after notifications complete

### 2.5 Event System
Defines how events are emitted and dispatched across components.

#### 2.5.1 Event
Namespaced string that represents a concrete domain intent.

* Must follow the format: \<namespace>.\<action>[.\<subaction>]
* Must be lowercase
* Must be emitted exclusively through `EventRouter`

**Allowed namespaces:**
* `app.*`
* `project.*`
* `selection.*`
* `edit.*`
* `widget.*`
* `grid.*`
* `properties.*`
* `debug.*`

#### 2.5.2 EventBus
Dispatches emitted events to their handlers.  

* Must allow registration of a callable handler for an event
* Must call the registered handler when the event is emitted

##### 2.5.2.1 App EventBus
Global event bus owned by `AppController` and used for application-level events.

* Must persist for the entire application lifetime
* App events must start with `app.*` or `project.*`

##### 2.5.2.2 Designer EventBus
Local event bus scoped to a `Designer` instance and used for editor-specific events.

* Must be destroyed along with `Designer` to avoid calling handlers that reference destroyed objects

#### 2.5.3 EventRouter
Routes emitted events to the appropriate `EventBus`.

* Must provide a single interface for emitting events
* Must route events to the corresponding `EventBus` based on namespace

### 2.6 Action System
Defines how concrete domain intents (e.g. delete, copy, nudge, align, undo) are represented and executed as actions.

#### 2.6.1 Action
A method defined on an action group that implements a concrete domain intent.

* Must implement a concrete domain intent
* Must validate whether an action should run (e.g. selection must not be empty)
* Must return early for no-op or invalid user intent when no error is required
* Must create the appropriate command for the action
* Must execute commands through `CommandStack`

#### 2.6.2 Action Group
Encapsulates the implementation of related actions.

* Must only receive the dependencies required to execute actions
* Must expose editor actions only through methods

#### 2.6.3 Action Groups (Facade)
Provides structured access to all action groups.

* Must aggregate all action groups
* Must provide a single access point for all action groups

### 2.7 Command System
Defines how state changes are applied and reversed.

#### 2.7.1 Command
Defines a concrete state change and specifies how it is executed and undone.

* Must not depend on external mutable state
* Must preserve deterministic order for all affected `Widget` instances
* Must only receive required operation parameters and an `AppState` reference for model mutations
* Must snapshot all required application state (e.g. original and final positions, attribute snapshots, clipboard data)
* Must be executed exclusively through `CommandStack`
* Must keep all attributes private (prefixed with underscore)
* Must treat snapshotted data as immutable
* `execute()` must only apply stored parameters or snapshotted final state
* `undo()` must restore state exclusively from the snapshotted original state

##### 2.7.1.1 Deterministic Command
Command that is fully defined at construction time.

* Both the original and final state must be snapshotted during construction (if required)
* The public API must only consist of `execute()`, `undo()` and optional predicate methods (e.g. `has_effect()`)

##### 2.7.1.2 Interactive Command
Command that is finalized through user interaction (e.g. dragging or attribute editing).

* Must snapshot the original state during construction
* May apply intermediate changes during the interaction
* Must snapshot the final state explicitly during finalization
* Must finalize before execution
* May expose additional lifecycle methods required to support the interaction, such as:
   * `apply_drag_delta()`
   * `apply_attribute_changes()`
   * `record_final_positions()`
   * `record_final_snapshot()`

#### 2.7.2 Command Stack
Maintains a command history and provides undo and redo functionality.

* Must maintain consistent undo and redo history
* Must derive dirty state from command history
* Must invalidate the clean history position when clearing the redo history makes the saved state unreachable

### 2.8 Designer
Responsible for orchestrating the interaction between events, actions, state and rendering.

* Must act as the central coordination layer between systems
* Must subscribe handlers to their corresponding events
* Must subscribe to `AppState` notifications and update the UI based on the provided flags and change sets
* Must manage transient UI specific state (e.g. last right click position)
* Must delegate to the action system instead of executing commands directly
* Must not own persistent project state

## 3 Rendering
Updates the UI to reflect the current application state and active user interactions.

* Must be driven exclusively by `AppState` changes when representing application state 
* Must be incremental when representing application state
* May respond directly to events when displaying temporary UI elements during an active user interaction
* Must update Tk widgets for dirty `Widget` instances
* Must additionally update selection outlines for dirty `Widget` instances when they are selected
* Must delete Tk widgets and selection outlines for removed `Widget` instances
* Must refresh selection outlines and the attributes panel when the selection changes
* Must update the grid when grid settings change

## 4 Widget Ownership
Determines how `Widget` instances may be mutated based on whether `AppState` owns them.

### 4.1 Unowned Widgets
Have not yet been added through `AppState.add_widget()`

* May be constructed, positioned and otherwise prepared directly

**Allowed:**
```
widget.x += dx
widget.y += dy
self.app_state.add_widget(widget)
```

### 4.2 Owned Widgets
Have been added through `AppState.add_widget()`

* Must only be mutated through `AppState`

**Incorrect:**
```
self.app_state.add_widget(widget)
widget.x += dx
widget.y += dy
```

**Correct:**
```
self.app_state.add_widget(widget)
self.app_state.offset_widget_position(widget, dx, dy)
```

## 5 Batching
Coalesces multiple mutations into a single state change notification.

* Must be used for any operation that mutates multiple `Widget` instances or performs multiple related mutations
* Must guarantee that subscribers are notified only once

**Example:**
```
with self.app_state.batch():
    for widget in selected_widgets:
        self.app_state.offset_widget_position(widget, dx, dy)
```

## 6 Comments
Explain local implementation details that are not clear from the code itself.

* Must not include a space after the `#` marker
* Must not explain what the code already says
* Must be short and specific
* Must use a consistent comment style

### 6.1 Comments Above Code
Summarize a meaningful implementation step.

* Must summarize a meaningful step that spans multiple lines
* Should be used when a block is too small to extract into a separate function but still benefits from a named logical step

**Incorrect:**
```
#create toolbar
self.toolbar_controller.build_toolbar()

#bind events to canvas
self.canvas_controller.bind_events()

#create context menu (right click) for creating new widgets
self._create_context_menu()
```
**Correct:**
```
#compute new dimensions
measurement_text = text if text is not None else ""
width, height = self._measure_preview_tk_widget_callback(widget_type, measurement_text)

#compute allowed x and y range and clamp widget coordinates
min_x, max_x = allowed_x_range(
    canvas_width=self._app_state.project.width,
    widget_width=width,
    anchor="sw"
)
min_y, max_y = allowed_y_range(
    canvas_height=self._app_state.project.height,
    widget_height=height,
    anchor="sw"
)
x = clamp(coordinates[0], min_x, max_x)
y = clamp(coordinates[1], min_y, max_y)
```

### 6.2 Inline Comments
Explain why something non-obvious is required.

* Must document reasoning, constraints or edge cases that are not obvious from the code itself
* Must be horizontally aligned with other inline comments of the same scope

**Examples:**
```
self._dirty_widget_ids: set[str] = set()      #IDs of widgets that changed
self._removed_widget_ids: set[str] = set()    #IDs of widgets that were removed
self.selection_change: bool = False           #signals whether the selection outlines need to be re-rendered
self.grid_change: bool = False                #signals whether the grid needs to be re-rendered
```
```
self._batch_depth = 0    #tracks batch depth so only the outermost batch notifies (batches can be nested)
```
```
self._widget_by_id = {}  #{widget.id: widget} for O(1) lookup; maintained in add_/remove_widget()
```

## 7 Docstrings
Describe the purpose and contract of modules, classes and functions.

* Must describe what the object represents or what the function does
* Must not duplicate implementation details already clear from the function body
* May be omitted for private helpers when the name and implementation are self-explanatory

### 7.1 Class Docstrings
Describe the responsibility of the class.

* Must describe the role of the class within the architecture
* Must not describe implementation details or list every method

### 7.2 Function Docstrings
Describe the behaviour of the function.

* Must describe what the function does
* Must mention important side effects

## 8 Type Annotations
Define expected types.

* Must be used for all function parameters
* Must be used for all function return types
* Must be used for all class attributes
* Must be used for all instance attributes when initialized
* Must use `Callable` for callback types
* Must explicitly use `| None` for optional values
* Must further specify generic collection types such as `dict` or `list` (e.g. `dict[str, tuple[int, int]]`)
* Must only use `Any` or `object` when the values are intentionally unrestricted or when a more precise annotation would reduce readability

### 8.1 Attribute Annotations
Define the expected type of attributes.

* Must be added when attributes are declared
* Must be added when instance attributes are initialized

### 8.2 Return Annotations
Define the expected return value of functions.

* Must be added to every function
* Must use `-> None` when no value is returned

## 9 Function Signatures
Define the typed interface of functions.

* Must use a consistent vertical style by default
* Must place each parameter on its own line
* Must place the closing parenthesis and return annotation on the final signature line

**Allowed exception:**
* Readability may override this rule

**Example:**
```
def set_widget_position(
    self,
    widget: Widget,
    x: int,
    y: int
) -> None:
```

## 10 Private Members
Implementation details that are not part of a class's intentional public API.

* Must be the default for anything that does not need to be accessed outside the class
* Must be prefixed with an underscore
* Must not be accessed outside the class

**Allowed exceptions:**
* Tests may access private members when validating internal behaviour
* Helper classes that are implementation details of the same module may access private members of the owning class

## 11 Imports
Bring code from other modules into the current file.

* Must be sorted alphabetically, including imported names
* Must use multi-line format when importing two or more names from the same module or package
* Must be grouped into standard library imports and project imports, separated by an empty line
* Package imports must only be used from outside the package
* Relative imports must only be used inside the `__init__.py` file of packages

## 12 Errors
Represent invalid or inconsistent state.

* Must be raised for invalid or inconsistent state instead of failing silently
* Must not be raised for expected no-op actions and instead return early
* Programmer errors must not be replaced with custom validation errors

### 12.1 Validation
Detects and rejects invalid or inconsistent state.

* Must not occur for parameters that callers are responsible for providing

#### 12.1.1 Input Validation
Validates untrusted data before it becomes application state.

* Must occur at input boundaries
* Must reject missing, malformed or corrupted data

**Examples:**
* Project deserialization
* Widget deserialization
* User input parsing

#### 12.1.2 Domain Invariant Validation
Validates conditions that must remain true for the application to work correctly.

* Must occur within the internal code responsible for maintaining the relevant domain invariant

**Examples:**
* A widget's anchor can only be `n`, `ne`, `e`, `se`, `s`, `sw`, `w`, `nw` or `center`
* Widgets must be smaller than the canvas
* Widget IDs must be unique

### 12.2 Error Messages
Describe the reason an error was raised.

* Must list the module that raises the error
* Must list the operation that failed (e.g. model creation, selection update, widget lookup)
* Must list the reason for the failure
* Must avoid low level implementation details (e.g. Python internals, function names)
* Must be short and specific
* Must not use trailing punctuation
* Must follow the format: \<Module> - \<operation> failed: \<reason> [\<key values>]

**Incorrect:**
```
AppState: unknown id
```
```
get_widget_from_widget_id(): invalid value
```
```
Unknown type
```

**Correct:**
```
AppState - subscription failed: subscriber must be callable
```
```
ProjectDocument - project data deserialization failed: missing required attribute "id_counters"
```
```
Geometry - computation failed: invalid anchor "nnw"
```

## 13 Dirty State
Indicates whether unsaved changes exist.

* Must be owned by `CommandStack`
* Must be derived from the command history
* Must be visually represented in the UI

## 14 Collections
Store multiple values with defined ordering, mutability and uniqueness characteristics.

* Must use lists for ordered, mutable collections that permit duplicates
* Must use tuples for ordered, immutable collections that permit duplicates
* Must use sets for unordered, mutable collections that enforce uniqueness
* Must use frozensets for unordered, immutable collections that enforce uniqueness
