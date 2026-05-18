# Coding and Architecture Conventions
This document defines the architectural and coding conventions used throughout the GUI_Builder codebase.  
The goal of these conventions is to make the codebase predictable, readable and architecturally sound.

## 1 Core Principles
These principles apply globally and must not be violated.

**Single source of truth:**  
All application state lives in AppState and all model mutations go through AppState

**Unidirectional data flow:**  
User Input → Controller → Event → Action → Commands → CommandStack → AppState → View

**Deterministic behaviour:**  
Given the same inputs, the system must always produce the same results

**No hidden mutations:**  
All state changes must be explicit and observable

## 2 Architecture
The codebase follows a layered MVC architecture extended with a centralized mutation engine, an event system and a command system.  
Each component has clearly defined responsibilities and allowed dependencies.

### 2.1 Model
Represents application data such as the ProjectDocument, WidgetModels, SelectionState etc.

* Contains only data, serialization logic and identity management (IDs)
* Model IDs are immutable and created exactly once

### 2.2 View
Responsible for rendering model state.

* Must only contain Tk rendering code
* Must not mutate models
* May cache mappings (e.g. model ←→ widget IDs)

### 2.3 Controller
Interprets user input and translates it into domain intent.

* Handles mouse, keyboard and menu interactions
* Emits events via EventRouter
* Must not mutate models
* Must not perform rendering

### 2.4 AppState
AppState is the central mutation engine responsible for applying all model mutations.

* Applies all state changes to models
* Tracks dirty models and structural changes
* Notifies subscribers about state changes
* Provides batching for grouped mutations
* Provides fast model lookup

**Notification system:**  
* Subscribers are notified after mutations
* During notification **dirty_model_ids**, **structural_change** and **selection_change** define what changed
* After the notification completes these flags are reset

### 2.5 Command System
The command system encapsulates undoable domain operations.

#### 2.5.1 Commands
Encapsulate user intent and provide deterministic undo and redo behaviour.

* Store operation parameters (IDs, movement deltas) and snapshotted model state (original and final positions, clipboard data)
* Must only receive required operation parameters and an AppState reference to mutate the model
* All attributes must be private (prefixed with underscore)
* Snapshotted data must be treated as immutable
* **execute()** must only apply stored parameters or snapshotted final state
* **undo()** must restore state exclusively from the snapshotted original state
* Affected model IDs must be stored as a list created during construction to ensure deterministic order

##### 2.5.1.1 Deterministic Commands
Commands that are fully defined at construction time.

* Both the original and final state (if required) must be snapshotted during construction
* The public API must only consist of **execute()**, **undo()** and optional predicate methods (e.g. **has_effect()**)

##### 2.5.1.2 Interactive Commands 
Commands that are finalized through user interaction. (e.g. dragging)

* The original state must be snapshotted during construction
* The final state must be snapshotted explicitly during finalization
* The public API may expose additional methods required to support the interaction (e.g. preview, commit)

#### 2.5.2 Command Stack
Maintains a command history and provides undo and redo functionality.

* Provides **execute()**, **undo()** and **redo()**
* All command execution must go through the CommandStack so that history and redo state remain consistent

### 2.6 Event System
The event system enables decoupled communication between components.

#### 2.6.1 Events
Events are namespaced strings that describe concrete actions.

Namespaces include:
* app.*
* project.*
* selection.*
* edit.*
* widget.*
* grid.*
* debug.*

#### 2.6.2 EventBus
Maps events to subscribers and dispatches them.  
Provides **subscribe()**, **unsubscribe()** and **emit()**.

##### 2.6.2.1 App EventBus
Global event bus owned by the AppController.

* Persists for the entire application lifetime
* Used for application level events
* App events must start with **app.\*** or **project.\***

##### 2.6.2.2 Designer EventBus
Local event bus scoped to a Designer instance.

* Destroyed along with the Designer
* Used for editor specific events

#### 2.6.3 EventRouter
Routes emitted events to the appropriate EventBus.

* Provides a single interface for emitting events
* Determines routing based on event namespace
* Events must be emitted exclusively through EventRouter

### 2.7 Rendering
Rendering is driven exclusively by AppState changes.  
The Designer decides what rendering strategy to use based on the flags provided by AppState.

#### 2.7.1 Full Render
Rebuilds the entire UI state.

* Triggered on structural changes (creation, deletion, grid changes) and large updates
* Fully rebuilds all widgets, selection outlines and the grid

#### 2.7.2 Soft Render
Updates only affected widgets.

* Triggered by updates to individual models
* Updates only affected widgets and outlines

## 3 Comments
### 3.1 Comments Above Code
Comments above code explain what the code does as a sequence of logical steps.  
They should allow a reader to understand the intent of the code without reading every line.

**Example:**
```
def _change_grid_size(self):
    #prompt for new grid size
    new_grid_size = simpledialog.askinteger(
        "Grid size",
        "Enter new grid size:",
        minvalue=5,
        maxvalue=100,
        parent=self.parent
    )
    if new_grid_size is None:
        return

    #update grid size in ProjectDocument
    self.app_state.set_grid_size(new_grid_size)

    #set AppState to dirty
    self._set_dirty()
```

### 3.2 Inline Comments
Inline comments explain why something non obvious is required.  
They document reasoning, constraints or edge cases that are not obvious from the code itself.

**Examples:**
```
def _delete(self):
    if self.state.is_deleting:  #prevents concurrent delete calls
        return
    ...
```
```
self.structural_change = False	#signals whether a full re-render is necessary
```
```
self._batch_depth = 0		    #tracks batch depth so only the outer most batch notifies (batches can be nested)
```
```
self._model_by_id = {}		    #{model.id: model} for O(1) lookup; maintained in add_/remove_widget()
```

## 4 Model Mutation
### 4.1 Single Source of Truth
All model mutation must go through AppState.  
Direct model mutation is forbidden outside AppState.

**Incorrect:**
```
model.x += dx
model.y += dy
```
**Correct:**
```
self.app_state.move_widget_by(model, dx, dy)
```

### 4.2 Batching
Any operation that mutates multiple models or performs multiple related mutations must use AppState batching.  
Batching guarantees that subscribers are only notified once and that rendering remains efficient.

**Example:**
```
with self.app_state.batch():
    for model_id in self.app_state.selection_currently_selected():
        model = self.app_state.get_model_from_model_id(model_id)
        self.app_state.move_widget_to(model, new_x, new_y)
```

## 5 Private Members
Any private method or attribute must be prefixed with an underscore.  
Private members must not be accessed across architectural layers.

## 6 Raising Errors
Errors must be raised explicitly and follow a consistent structure:  
\<Domain>: \<description>

* Use domain concepts (e.g. Model, Widget, Project)
* Avoid implementation details (class or method names)
* Short and specific
* No trailing punctuation
* Prefer explicit errors over silent failure

**Incorrect:**
```
AppState: unknown id
```
```
get_model(): invalid value
```
```
Unknown type
```

**Correct:**
```
Model: unknown id "label_1"
```
```
Widget: invalid type "Slider"
```
```
Project: invalid "width" value "abc"
```