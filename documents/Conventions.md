# Coding and Architecture Conventions
This document defines the architectural and coding conventions used throughout the GUI_Builder codebase.  
The goal of these conventions is to make the codebase coherent, readable and architecturally sound.

## 1 Core Principles
These principles apply globally and must not be violated.

**Single source of truth:**  
All application state must live in AppState and all model mutations must go through AppState

**Unidirectional data flow:**  
User Input → Controller → Event → Designer → Action → Commands → CommandStack → AppState → View

**Deterministic behaviour:**  
Given the same inputs, the system must always produce the same results

**No hidden mutations:**  
All state changes must be explicit and observable

## 2 Architecture
The codebase follows a layered MVC architecture extended with a centralized mutation engine, an event system and a command system.  
Each component has clearly defined responsibilities and allowed dependencies.

### 2.1 Model
Represents application data such as ProjectDocument, WidgetModels, SelectionState etc.

* Must only contain data, serialization logic and identity management (IDs)
* Model IDs are immutable and created exactly once

### 2.2 View
Responsible for rendering model state.

* Must only contain Tk rendering code
* Must not mutate models
* May cache mappings (e.g. model ←→ widget IDs)

### 2.3 Controller
Translates user input (mouse, keyboard and menu interactions) into domain intent.

* Must emit events via EventRouter
* Must not mutate models
* Must not perform rendering

### 2.4 AppState
AppState is the central mutation engine responsible for applying all model mutations.

* Must apply all state changes to models
* Must track dirty models and structural changes
* Must notify subscribers after state changes
* Must provide batching for grouped mutations
* Must provide O(1) model lookup by ID

**Notification system:**  
* **dirty_model_ids** must contain the IDs of all modified models
* The **structural_change** flag must indicate full re-render requirements
* The **selection_change** flag must indicate outline refresh requirements
* After notifications complete, all flags must be reset and **dirty_model_ids** must be cleared

### 2.5 Event System
The event system defines how events are emitted and dispatched across components.

#### 2.5.1 Events
Events are namespaced strings that describe concrete actions.

* Must follow the format: \<namespace>.\<action>[.\<subaction>]
* Must be lowercase

**Allowed namespaces:**
* app.*
* project.*
* selection.*
* edit.*
* widget.*
* grid.*
* debug.*

#### 2.5.2 EventBus
EventBus maps events to subscribers and dispatches them to all subscribers.  

* Must allow subscription and unsubscription of functions
* Must call all subscribers when an event is emitted
* Must not stop dispatching if a subscriber raises an error

##### 2.5.2.1 App EventBus
Global event bus owned by the AppController and used for application level events.

* Must persist for the entire application lifetime
* App events must start with **app.\*** or **project.\***

##### 2.5.2.2 Designer EventBus
Local event bus scoped to a Designer instance, used for editor specific events.

* Must be destroyed along with the Designer

#### 2.5.3 EventRouter
EventRouter routes emitted events to the appropriate EventBus.

* Must provide a single interface for emitting events
* Must route events to the correct EventBus based on namespace
* Events must be emitted exclusively through EventRouter

#### 2.6 Designer
The Designer is responsible for orchestrating the interaction between events, actions, state and rendering.

* Must act as the central coordination layer between systems
* Must subscribe to events and map them to the corresponding actions
* Must trigger rendering in response to AppState notifications
* Must manage UI specific state (e.g. dirty flag, last click position)
* Must delegate to the action system instead of executing commands directly

### 2.7 Action System
The action system defines how editor actions (e.g. delete, copy, nudge, align, undo) are structured and executed through action groups.

#### 2.7.1 Actions (Facade)
The Actions facade provides structured access to all available actions via action groups.

* Must aggregate all action groups
* Must provide a single access point for all action groups

#### 2.7.2 Action Groups
Action groups organize related editor actions.

* Must only receive the dependencies required to execute actions
* Must expose editor actions only through methods

#### 2.7.3 Action
An action is a method defined on an action group that implements a concrete editor action.

* Must represent concrete editor actions
* Must create the appropriate command for the action
* Must validate whether an action should run (e.g. selection must not be empty)
* May return affected model IDs if required by the caller (e.g. for UI updates)

### 2.8 Command System
The command system defines how state changes are applied and reversed.

#### 2.8.1 Commands
A command defines a concrete state change and specifies how it is executed and undone.

* Must not depend on external mutable state
* Must store all required operation parameters (IDs, movement deltas)
* Must snapshot all required model state (original and final positions, clipboard data)
* Must only receive required operation parameters and an AppState reference (for model mutations)
* All attributes must be private (prefixed with underscore)
* Snapshotted data must be treated as immutable
* **execute()** must only apply stored parameters or snapshotted final state
* **undo()** must restore state exclusively from the snapshotted original state
* Affected model IDs must be stored as a list created during construction to ensure deterministic order

##### 2.8.1.1 Deterministic Commands
Commands that are fully defined at construction time.

* Both the original and final state must be snapshotted during construction (if required)
* The public API must only consist of **execute()**, **undo()** and optional predicate methods (e.g. **has_effect()**)

##### 2.8.1.2 Interactive Commands 
Commands that are finalized through user interaction (e.g. dragging).

* The original state must be snapshotted during construction
* The final state must be snapshotted explicitly during finalization
* Finalization must occur before execution
* The public API may expose additional methods required to support the interaction (e.g. preview, commit)

#### 2.8.2 Command Stack
Maintains a command history and provides undo and redo functionality.

* Commands must be executed exclusively through CommandStack
* CommandStack must maintain consistent undo and redo history

### 2.9 Rendering
Rendering updates the UI to reflect the current model state.

* Rendering must be driven exclusively by AppState changes
* The Designer must subscribe to AppState notifications and decide what rendering strategy to use based on the provided flags

#### 2.9.1 Full Render
Full render rebuilds the entire UI from the current model state.

* Must be triggered on structural changes (creation, deletion, grid changes) and large updates
* Must rebuild all widgets, selection outlines and the grid

#### 2.9.2 Soft Render
Soft render only updates widgets affected by the model changes.

* Must update all widgets referenced by **dirty_model_ids**
* Must not rebuild unaffected widgets

## 3 Comments

* Must not include a space after the '#' marker
* Comment style must be consistent

### 3.1 Comments Above Code
* Must describe what the code does as a sequence of logical steps
* Must allow a reader to understand the intent without reading every line

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
* Must explain why something non obvious is required
* Must document reasoning, constraints or edge cases that are not obvious from the code itself

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
self._batch_depth = 0		    #tracks batch depth so only the outermost batch notifies (batches can be nested)
```
```
self._model_by_id = {}		    #{model.id: model} for O(1) lookup; maintained in add_/remove_widget()
```

## 4 Model Mutation
### 4.1 Single Source of Truth
* All application state must live in AppState
* All model mutation must go through AppState

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
* Any operation that mutates multiple models or performs multiple related mutations must use AppState batching 
* Batching must guarantee that subscribers are notified only once

**Example:**
```
with self.app_state.batch():
    for model_id in self.app_state.selection_currently_selected():
        model = self.app_state.get_model_from_model_id(model_id)
        self.app_state.move_widget_to(model, new_x, new_y)
```

## 5 Private Members
* Any private method or attribute must be prefixed with an underscore
* Private members must not be accessed across architectural layers

## 6 Raising Errors
* Invalid or inconsistent state must raise errors instead of failing silently
* Must use domain concepts (e.g. Model, Widget, Project)
* Must avoid implementation details (class or method names)
* Must be short and specific
* Must not use trailing punctuation
* Must follow the format: \<Domain> - \<operation> failed: \<reason> [\<key values>]

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
Model - lookup failed: unknown ID "label_1"
```
```
Widget - creation failed: invalid type "slider"
```
```
Project - creation failed: invalid width "abd"
```

## 7 Dirty State
Dirty state indicates whether unsaved changes exist.

* Dirty state must be set after any state change
* Dirty state must be cleared after a successful save
* Dirty state must be visually represented in the UI
