# Commit Message Format
This document defines the structure and conventions used for commit messages throughout the GUI_Builder codebase.  
The goal of these conventions is to make commit history clear and consistent.  
They allow an arbitrarily deep understanding of changes, from a high level overview to a complete description.

## 1 Structure
### 1.1 Title
* Concise summary of what changed
* Single line
* Past tense
* Capitalized
* No trailing punctuation

### 1.2 Description
* Explains what the commit achieves
* One or more full sentences
* Present tense
* No indentation
* Typically starts with "This commit [...]"
* May include an enumeration when the commit introduces or formalizes a convention or structure

### 1.3 Body
* Hierarchical
* Indented using 3 spaces per level
* Bullet point symbols encode the question being answered
   * \* → What changed?
	* \- → What does the code now do because of that change?
	* \> → What additional clarification is useful?
* Any bullet point that has child bullet points must end with :
* Any level may terminate the hierarchy if additional detail is not necessary
* Every file section must be separated from the previous file section by one empty line

#### Hierarchy overview:
```
File:                   Where did something change?
   *Change:             What changed?
      -Behaviour:       What does the code now do because of that change?
         >Details:      What additional clarification is useful?
```

#### 1.3.1 File level
* Describes which file was affected and how
* Full relative file path including file extension
* Past tense
* No indentation
* Capitalized
* Allowed verbs:
	* Added
	* Removed
	* Updated
	* Renamed
	* Moved

#### 1.3.2 Action level
* Describes what changed within the file
* Must name the affected code unit (method, function, class, flag, dictionary etc.) when this adds clarity
* Must also include the class name if the file contains multiple classes or the class name differs from the file name
* Past tense
* Bullet point symbol: \*
* Indentation: 3 spaces
* May include brief context in parenthesis if required to understand the change
>e.g. "Removed _move() (obsolete, as nudge and drag preview are now handled separately)"

#### 1.3.3 Behaviour level:
* Describes behaviour that results from the change
* Present tense
* Bullet point symbol: \-
* Indented one level deeper than the parent bullet point (3 additional spaces)
* May act as an introducer for multiple detail bullet points
>e.g. "Uses:", "Accepts:", "Exposes:", "Defines:" etc.
* May be omitted if the action level already expresses behaviour clearly, allowing the hierarchy to continue with the detail level

#### 1.3.4 Detail level
* Used for providing additional detail about a behaviour
* Bullet point symbol: \>
* Indented one level deeper than the parent bullet point (3 additional spaces)
* May represent:
   * Additional clarification of behaviour (present tense)
   * An enumeration of elements involved in the behaviour (tense neutral)
   >e.g. methods, variables, parameters etc.
	* An enumeration of elements forming the resulting structure (tense neutral)

#### 1.3.5 Sub-detail level
* Used for providing even more fine grained detail
* Recursively nestable
* Bullet point symbol: \>
* Indented one level deeper than the parent bullet point (3 additional spaces)

## 2 General rules

### 2.1 Express intent in action level
* The action level must include both the change and its intent whenever possible
* The behaviour level should only be used if the intent cannot be expressed clearly in the action

#### Avoid:
```
*Updated method():
   -Handles edge cases in selection logic
```

#### Prefer:
```
*Updated method() to handle edge cases in selection logic
```

### 2.2 One logical change per action
* Each action should represent a single coherent change
* Independent changes must be expressed as separate actions even if they affect the same code unit

### 2.3 Behaviour describes the change
* Behaviour must always belong to a specific action or sub-action
* Behaviour must describe the result of the exact change it is nested under and must not apply to multiple actions

### 2.4 One bullet type per indentation level
* Different bullet types must not be mixed at the same indentation level
* If both actions and behaviour are needed, split them into separate actions

#### Incorrect:
```
*Updated method():
   *Updated logic:
      -Now validates input before processing
      *Refined logic
      *Simplified control flow
```

#### Correct:
```
*Updated method() to handle edge cases:
   -Now validates input before processing
*Updated method() implementation:
   *Refined logic
   *Simplified control flow
```

### 2.5 Action decomposition
* Actions may be decomposed into more specific sub-actions that represent a concrete part of the action
* Sub-actions inherit the intent (verb) of the parent unless overridden
* Sub-actions must use the \* bullet point and be indented one level deeper than the parent (3 additional spaces)

### 2.6 Grouping identical changes
* Identical changes to multiple code units of the same file must be grouped into a single action
* The correct grouping style must be chosen based on the number of elements
* Structured grouping is preferred as it scales and preserves readability
* Grouping identical changes is a specific form of action decomposition

#### Inline grouping:
* Used when grouping a small number of elements
```
*Updated execute() and undo() to replace usage of AppState mutation API
```

#### Structured grouping:
* Used when grouping more than 3 elements or when readability would suffer
* Code units must be represented as sub-actions
```
*Updated tests to replace usage of AppState mutation API:
   *TestAddWidgetFromModel
   *TestMoveWidget
   *TestUndoRedoDeleteWidget
```

### 2.7 Action target
* The subject of an action must identify the actual target of the change, not just the code unit containing it
* The code unit should be used as context unless it is itself the element being changed

#### Incorrect:
```
*Updated __init__() to refine comments
*Updated method() to fix typo in doctring
*Updated process_data() to add logging
```
#### Correct:
```
*Refined comments in __init__()
*Fixed typo in method() docstring
*Added logging to process_data()
```

## 3 Structure templates
A structure template defines a valid pattern for commit message blocks that fully conforms to the convention.  
They act as building blocks for constructing complete commit messages.  
The acronym next to each structure template indicates the hierarchy levels used by the structure.

Each letter represents one level:  
F = File  
A = Action  
S = Sub-action  
B = Behaviour  
D = Detail

The full structure, for example, has the acronym FASBD, meaning it includes file, action, sub-action, behaviour and detail levels.
### 3.1 File structure (F)
```
Added folder example/
```

```
Moved file.txt to archive/
```

```
Renamed old_name.py to new_name.py
```

### 3.2 Action structure (FA)
```
Updated file.py:
   *Refactored data processing logic
```
```
Updated configuration.py:
   *Renamed variable endpoint to base_url
   *Removed unused constant DEFAULT_TIMEOUT
```

```
Updated renderer.py:
   *Replaced legacy drawing logic with canvas renderer
   *Adjusted import paths for utility functions
```

### 3.3 Sub-action structure (FAS)
```
Updated parser.py:
   *Added supported formats:
      *json
      *xml
      *yaml
```

```
Updated math.py:
   *Added algebra API:
      *add(a, b)
      *subtract(a, b)
      *multiply(a, b)
      *divide(a, b)
```

```
Updated file_processor.py:
   *Implemented file processing pipeline:
      *Added file reading using buffered streams
      *Added parsing step for structured input
      *Added transformation logic for normalized output
      *Added writing step for processed files
   *Updated process_file() to use the new pipeline
   *Removed inline processing logic
```

### 3.4 Behaviour structure (FAB)
```
Updated service.py:
   *Added caching layer:
      -Stores results to prevent repeated computation
      -Invalidates cache on update
```

```
Updated cache.py:
   *Added in-memory cache:
      -Stores results keyed by request parameters
      -Expires entries after configured timeout
```

```
Updated authenticator.py:
   *Added token validation:
      -Checks signature against secret key
      -Rejects expired tokens
```

### 3.5 Behaviour structure with sub-actions (FASB)
```
Updated parser.py:
   *Improved error handling:
      *Added validation for input format:
         -Prevents invalid data from being processed
      *Aligned error messages with output schema
      *Renamed exception types for consistency
```

```
Updated authenticator.py:
   *Extended authentication flow:
      *Added token validation step:
         -Rejects expired or malformed tokens
      *Aligned error responses with API format
      *Removed deprecated session check
```

### 3.6 Detail structure (FABD)
#### Additional clarification of behaviour (present tense):
```
Updated validator.py:
   *Added validation system:
      -Validates user input:
         >Rejects empty values
         >Validates numeric range
         >Ensures string length limits
```
#### Enumeration of elements involved in the behaviour (tense neutral):
```
Updated network.py:
   *Added request handling:
      -Builds and sends HTTP request:
         >Authentication headers
         >Serialized request body
      -Processes responses:
         >Retry mechanism
         >Error logging
```

```
Updated session.py:
   *Added session management:
      -Manages user sessions:
         >Session creation on login
         >Session termination on logout
      -Maintains session state:
         >User ID
         >Timestamp
```

### 3.7 Detail structure without behaviour (FAD)
#### Enumeration of elements forming the resulting structure (tense neutral):
```
Updated config.py:
   *Updated configuration structures:
      >Connection:
         >timeout
         >retry_count
      >Authentication:
         >username
         >password
```

```
Updated layout.py:
   *Defined layout sections:
      >Header:
         >title
         >navigation
      >Content:
         >main_area
         >sidebar
```

### 3.8 Full structure (FASBD)
```
Updated renderer.py:
   *Refactored layout pipeline:
      *Extracted layout calculation into calculate_layout()
      *Added validation for layout constraints:
         -Ensures elements remain within bounds:
            >Clamps positions to container size
            >Prevents negative dimensions
   *Updated layout update logic:
      -Applies layout changes consistently:
         >Ensures deterministic rendering order
         >Prevents intermediate invalid states
```
