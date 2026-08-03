# Coding and Architecture Conventions
This document defines the architectural and coding conventions used throughout the GUI_Builder codebase.  
The goal of these conventions is to make the codebase coherent, readable and architecturally sound.

## 1 Core Principles
Principles that apply globally and must not be violated.

**Single source of truth:**  
AppState owns application state and all mutations of models owned by AppState must go through AppState

**Unidirectional data flow:**  
User Input → Controller → Event → Designer → Action → Commands → CommandStack → AppState → View

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
Represents application data such as ProjectDocument and WidgetModels.

* Must only contain data, serialization logic and identity management (IDs)
* May depend on standard library modules, dataclasses, enums and helpers that do not depend on application state or UI
* Must not depend on anything else
* Model IDs must be treated as immutable and created exactly once

### 2.2 View
Responsible for rendering model state.

* Must only contain Tk rendering code
* Must not mutate models

### 2.3 Controller
Translates user input (mouse, keyboard and menu interactions) into domain intent.

* Must emit events via EventRouter
* Must not mutate models
* Must not perform rendering
* Must not execute commands directly

### 2.4 AppState
The central mutation engine responsible for applying all mutations to models owned by AppState.

* Must apply all state changes to models owned by AppState
* Must reject mutations for unknown model IDs
* Must resolve models by ID before mutating them to avoid mutating stale model references
* Must track dirty state
* Must track dirty and removed models
* Must track selection and grid changes
* Must notify subscribers after state changes
* Must provide batching for grouped mutations
* Must provide O(1) model lookup by ID

**Notification system:**  
* `dirty_model_ids` must contain the IDs of all modified models
* `removed_model_ids` must contain the IDs of all removed models
* The `selection_change` flag must indicate selection outline and attributes panel refresh requirements
* The `grid_change` flag must indicate grid refresh requirements
* After notifications complete, all transient flags must be reset and all transient change sets must be cleared

### 2.5 Event System
Defines how events are emitted and dispatched across components.

#### 2.5.1 Events
Namespaced strings that describe concrete actions.

* Must follow the format: \<namespace>.\<action>[.\<subaction>]
* Must be lowercase
* Must be emitted exclusively through EventRouter

**Allowed namespaces:**
* app.*
* project.*
* selection.*
* edit.*
* widget.*
* grid.*
* debug.*

#### 2.5.2 EventBus
Maps events to subscribers and dispatches them to all subscribers.  

* Must allow subscription of callable functions
* Must call all subscribers when an event is emitted
* Must not stop dispatching if a subscriber raises an error
* Must collect subscriber errors and raise a combined error after dispatch

##### 2.5.2.1 App EventBus
Global event bus owned by the AppController and used for application level events.

* Must persist for the entire application lifetime
* App events must start with `app.*` or `project.*`

##### 2.5.2.2 Designer EventBus
Local event bus scoped to a Designer instance and used for editor specific events.

* Must be destroyed along with the Designer to avoid calling handlers that reference destroyed objects

#### 2.5.3 EventRouter
Routes emitted events to the appropriate EventBus.

* Must provide a single interface for emitting events
* Must route events to the correct EventBus based on namespace

#### 2.6 Designer
Responsible for orchestrating the interaction between events, actions, state and rendering.

* Must act as the central coordination layer between systems
* Must subscribe to events and map them to the corresponding actions
* Must subscribe to AppState notifications and trigger rendering in response to state changes
* Must manage transient UI specific state (e.g. last right click position)
* Must delegate to the action system instead of executing commands directly
* Must not own persistent project state

### 2.7 Action System
Defines how editor actions (e.g. delete, copy, nudge, align, undo) are structured and executed through action groups.

#### 2.7.1 Actions (Facade)
Provides structured access to all available actions via action groups.

* Must aggregate all action groups
* Must provide a single access point for all action groups

#### 2.7.2 Action Groups
Organize related editor actions.

* Must only receive the dependencies required to execute actions
* Must expose editor actions only through methods

#### 2.7.3 Action
A method defined on an action group that implements a concrete editor action.

* Must represent concrete editor actions
* Must validate whether an action should run (e.g. selection must not be empty)
* Must return early for no-op or invalid user intent when no error is required
* Must create the appropriate command for the action
* Must execute commands through CommandStack

### 2.8 Command System
Defines how state changes are applied and reversed.

#### 2.8.1 Command
Defines a concrete state change and specifies how it is executed and undone.

* Must not depend on external mutable state
* Must preserve deterministic order for all affected models
* Must only receive required operation parameters and an AppState reference for model mutations
* Must snapshot all required model state (original and final positions, attribute snapshots, clipboard data etc.)
* Must be executed exclusively through CommandStack
* All attributes must be private (prefixed with underscore)
* Snapshotted data must be treated as immutable
* `execute()` must only apply stored parameters or snapshotted final state
* `undo()` must restore state exclusively from the snapshotted original state

##### 2.8.1.1 Deterministic Command
Command that is fully defined at construction time.

* Both the original and final state must be snapshotted during construction (if required)
* The public API must only consist of `execute()`, `undo()` and optional predicate methods (e.g. `has_effect()`)

##### 2.8.1.2 Interactive Command
Command that is finalized through user interaction (e.g. dragging or attribute editing).

* The original state must be snapshotted during construction
* Intermediate changes may be applied during the interaction
* The final state must be snapshotted explicitly during finalization
* Finalization must occur before execution
* The public API may expose additional lifecycle methods required to support the interaction, such as:
   * `apply_drag_delta()`
   * `apply_attribute_changes()`
   * `record_final_positions()`
   * `record_final_snapshot()`

#### 2.8.2 Command Stack
Maintains a command history and provides undo and redo functionality.

* Must maintain consistent undo and redo history

### 2.9 Rendering
Updates the UI to reflect the current model state.

* Must be driven exclusively by AppState changes
* Must be incremental
* The Designer must subscribe to AppState notifications and update the UI based on the provided change flags and changed model IDs
* Dirty models must cause their widgets to be updated
* Dirty selected models must additionally cause their selection outlines to be updated
* Removed models must cause their widgets and selection outlines to be deleted
* Selection changes must refresh selection outlines and the attributes panel
* Grid changes must re-render the grid

## 3 AppState Ownership
Begins when a model is added through `AppState.add_model()`.

* Models that are not yet owned by AppState may be constructed, positioned, assigned IDs and otherwise prepared before being added to AppState
* Once a model is added through **AppState.add_model()**, all further mutations of that model must go through AppState

**Incorrect after AppState ownership:**
```
model.x += dx
model.y += dy
```
**Correct after AppState ownership:**
```
self.app_state.offset_model_position(model, dx, dy)
```
**Allowed before AppState ownership:**
```
model.x += x_offset
model.y += y_offset
self.app_state.add_model(model)
```

## 4 Batching
Coalesces multiple mutations into a single state change notification.

* Any operation that mutates multiple models or performs multiple related mutations must use AppState batching 
* Batching must guarantee that subscribers are notified only once

**Example:**
```
with self.app_state.batch():
    for model in selected_models:
        self.app_state.offset_model_position(model, dx, dy)
```

## 5 Comments
Explain local implementation details that are not clear from the code itself.

* Must not include a space after the `#` marker
* Must not explain what the code already says
* Must be short and specific
* Comment style must be consistent

### 5.1 Comments Above Code
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
measurement_model = copy(self._active_edit_model)
measurement_model.text = value
width, height = self._measure_preview_widget_callback(measurement_model)

#compute allowed x and y range and clamp model coordinates
min_x, max_x = allowed_x_range(self._app_state.project.width, width, self._active_edit_model.anchor)
min_y, max_y = allowed_y_range(self._app_state.project.height, height, self._active_edit_model.anchor)
x = clamp(self._active_edit_model.x, min_x, max_x)
y = clamp(self._active_edit_model.y, min_y, max_y)
```

### 5.2 Inline Comments
Explain why something non-obvious is required.

* Must document reasoning, constraints or edge cases that are not obvious from the code itself
* Must be horizontally aligned with other inline comments of the same scope

**Examples:**
```
self._dirty_model_ids: set[str] = set()   #IDs of models that changed
self._removed_model_ids: set[str] = set() #IDs of models that were removed
self.selection_change: bool = False       #signals whether the selection outlines need to be re-rendered
self.grid_change: bool = False            #signals whether the grid needs to be re-rendered
```
```
self._batch_depth = 0   #tracks batch depth so only the outermost batch notifies (batches can be nested)
```
```
self._model_by_id = {}  #{model.id: model} for O(1) lookup; maintained in add_/remove_widget()
```

## 6 Docstrings
Describe the purpose and contract of modules, classes and functions.

* Must describe what the object represents or what the function does
* Must not duplicate implementation details already clear from the function body
* May be omitted for private helpers when the name and implementation are self-explanatory

### 6.1 Class Docstrings
Describe the responsibility of the class.

* Must describe the role of the class within the architecture
* Must not describe implementation details or list every method

### 6.2 Function Docstrings
Describe the behaviour of the function.

* Must describe what the function does
* Must mention important side effects

## 7 Type Annotations
Define expected types.

* All function parameters must be annotated
* All function return types must be annotated
* All class attributes must be annotated
* All instance attributes must be annotated when initialized
* Callback types must use `Callable`
* Optional values must be explicit using `| None`
* Generic collection types such as `dict` or `list` must be further specified (e.g. `dict[str, tuple[int, int]]`)
* `Any` or `object` must only be used when the values are intentionally unrestricted or when a more precise annotation would reduce readability

### 7.1 Attribute Annotations
Define the expected type of attributes.

* Must be added when attributes are declared
* Must be added when instance attributes are initialized

### 7.2 Return Annotations
Define the expected return value of functions.

* Must use `-> None` when no value is returned

## 8 Function Signatures
Define the typed interface of functions.

* Must use a consistent vertical style by default
* Each parameter must be placed on its own line
* The closing parenthesis and return annotation must be placed on the final signature line
* This is a default and not an absolute rule as readability may override it

**Example:**
```
def set_model_position(
    self,
    model: BaseWidgetData,
    x: int,
    y: int
) -> None:
```

## 9 Private Members
Implementation details that are not part of a class's intentional public API.

* Must be the default for anything that does not need to be accessed outside the class
* Must be prefixed with an underscore
* Must not be accessed outside the class

**Allowed exceptions:**
* Tests may access private members when validating internal behaviour
* Helper classes that are implementation details of the same module may access private members of the owning class

## 10 Error Handling
Detects and rejects invalid or inconsistent state.

* Invalid or inconsistent state must raise errors instead of failing silently
* Untrusted data must be validated at input boundaries
* Internal code must enforce domain invariants
* Internal code must not validate parameters that callers are responsible for providing
* Programmer errors should not be converted into custom validation errors
* Expected no-op or invalid actions should return early instead of raising errors

### 10.1 Input Boundaries
Process untrusted data before it becomes application state.

* Must reject missing, malformed or corrupted data

**Examples:**
* Project deserialization
* Widget model deserialization
* User input parsing

### 10.2 Domain Invariants
Define conditions that must remain true for the application to work correctly.

* Must be enforced by internal code that relies on them

**Examples:**
* A widget's anchor can only be `n`, `ne`, `e`, `se`, `s`, `sw`, `w`, `nw` or `center`
* Widgets must be smaller than the canvas
* Widget IDs must be unique

## 11 Error Messages
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
get_model_from_model_id(): invalid value
```
```
Unknown type
```

**Correct:**
```
AppState - subscription failed: subscriber must be callable
```
```
WidgetController - widget update failed: missing widget for model "label_1"
```
```
Designer - widget creation failed: unsupported type "slider"
```

## 12 Dirty State
Indicates whether unsaved changes exist.

* Must be owned by AppState
* Must be set after any mutation that actually changes persistent project state
* Must not be set on no-op mutations (setting an attribute to its current value)
* Must be cleared after a successful save
* Must be visually represented in the UI
