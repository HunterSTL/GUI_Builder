# Commit Message Conventions

```
Commit Message Conventions
├── Purpose
├── Message structure
│   ├── Title
│   ├── Description
│   └── Body
│       ├── Levels
│       │   ├── File level (trace format only)
│       │   ├── Action level
│       │   ├── Behaviour level
│       │   └── Detail level (trace format only)
│       ├── Summary format
│       │   ├── Hierarchy overview
│       │   ├── Usage
│       │   ├── Format specific action rules
│       │   └── Examples
│       └── Trace format
│           ├── Hierarchy overview
│           ├── Usage
│           ├── Format specific action rules
│           ├── Recursive decomposition
│           ├── Behaviour as detail introducer
│           ├── Grouping identical changes
│           └── Structure templates
│               ├── File structure (F)
│               ├── Action structure (FA)
│               ├── Behaviour structure (FAB)
│               └── Detail structure (FABD)
├── Complete examples
│   ├── Summary example
│   └── Trace example
└── Commit scope
```

##### Note:
This tree reflects the document's conceptual structure.  
Section numbering below is flattened to avoid excessive depth.

## 1 Purpose
This document defines the structure and rules used for commit messages throughout the codebase.  
The purpose of these conventions is to make commit history clear, consistent and understandable.

To balance readability, traceability and documentation effort, two formats for the commit message body are defined:  
The summary format is a lightweight format for communicating conceptual changes with minimal implementation details.  
The trace format is a detailed format for documenting low level changes with precise implementation traceability.

## 2 Message structure
Every commit message must contain a title, description and body.

### 2.1 Title
The commit title describes the primary change.

* Single line
* Capitalized
* Past tense
* No trailing punctuation

### 2.2 Description
The commit description provides context, intent and rationale.

* One or more full sentences
* Present tense
* Typically starts with "This commit..."
* May include an enumeration when needed for clarity

### 2.3 Body
The commit body provides structured detail about the commit's changes.

* Hierarchical
* Summary format or trace format
* Capitalized lines
* 3 spaces per indentation level
* Bullet point symbols encode the question being answered:
   * `*` → What changed?
	* `-` → What does the code now do because of that change?
	* `>` → What additional clarification is useful? (trace format only)
* Any bullet point that has child bullet points must end with a colon (:)
* All direct child bullet points of the same parent must use the same bullet point symbol
* Any level may terminate the hierarchy if additional detail is not necessary

## 3 Levels
The commit body is built from semantic levels that each answer a different question about the change.

##### The summary format uses:
* Action level
* Behaviour level

##### The trace format uses:
* File level
* Action level (recursive)
* Behaviour level
* Detail level (recursive)

### 3.1 File level (trace format only)
The file level describes which file was affected and how.  
Any file section must be separated from the previous file section by one empty line.

##### File bullet points:
* Full relative file path including the file extension
* Trailing "/" when referring to a directory
* Past tense
* No indentation

##### Allowed verbs:
* Added
* Removed
* Updated
* Renamed
* Moved
* Replaced

### 3.2 Action level
The action level describes concrete changes of the commit and may include brief context in parentheses if required to understand the change.

##### Action bullet points:
* One coherent change
* Bullet point symbol: `*`
* Past tense
* Express intent whenever possible

### 3.3 Behaviour level
The behaviour level describes behaviour resulting from a change.

##### Behaviour bullet points:
* Behaviour that is a direct result of the action bullet point
* Bullet point symbol: `-`
* Present tense

### 3.4 Detail level (trace format only)
The detail level provides additional detail about a behaviour.

##### Detail bullet points:
* Clarify behaviour or enumerate elements
* Bullet point symbol: `>`
* Present tense when clarifying behaviour
* Tense neutral when enumerating elements

## 4 Summary format
The summary format documents conceptual changes, intent and resulting behaviour.  
It should make the commit understandable without requiring implementation tracing.  
Its shallow hierarchy keeps commit messages easy to scan and allows changes to be understood quickly.

### 4.1 Hierarchy overview
```
*Action:                   What changed?
   -Behaviour              What does the code now do because of that change?
```

### 4.2 Usage
##### The summary format is the default body format for commit messages and should be used when:
* The commit can be understood from its conceptual changes
* Code unit tracing is not necessary
* Implementation details would add noise
* The commit should provide concise, intent focused documentation of conceptual changes

### 4.3 Format specific action rules
* Action bullet points must describe the conceptual change rather than identify the code unit containing it (method, class, flag, dictionary etc.)
* Independent changes must be expressed as separate action bullet points even if they affect the same code unit
* Omit minor supporting changes (e.g. fixing a typo) unless they are relevant to understanding the commit

### 4.4 Examples
```
*Added input validation:
   -Rejects malformed data before processing
```
```
*Introduced authentication layer:
   -Validates user credentials before granting access
   -Rejects expired authentication tokens
```
```
*Renamed configuration keys for consistency
*Reorganized project documentation
```

## 5 Trace format
The trace format documents low level changes, intent and resulting behaviour, including the affected files and code units.  
It should allow the reader to understand changes at arbitrary depth, from a high level overview to a self contained description.  
Its deeper hierarchy preserves implementation traceability by making the location of each change explicit.

### 5.1 Hierarchy overview
```
File:                            Where did the change occur?
   *Action:                      What changed?
      -Behaviour:                What does the code now do because of that change?
         >Detail                 What additional clarification is useful?
```

### 5.2 Usage
##### The trace format should be used when:
* The commit cannot be understood from its conceptual changes alone
* Code unit tracing provides value
* Implementation details clarify the change
* The commit should provide detailed, self contained documentation of low level changes

### 5.3 Format specific action rules
* Action bullet points must identify the code unit containing the change
* Action bullet points must also include the class name if the file contains multiple classes or the class name differs from the file name
* Independent changes to the same code unit must be grouped under one action bullet point
* Omit mechanical changes (e.g. call site updates) unless they are relevant to understanding the commit

### 5.4 Recursive decomposition
Action and detail bullet points may be recursively decomposed when additional structure improves clarity.  
Child action bullet points inherit the intent of the parent action unless overridden.  
Behaviour bullet points do not recursively decompose, but may introduce multiple detail bullet points.

### 5.5 Behaviour as detail introducer
Behaviour bullet points may introduce detail bullet points when the behaviour enumerates multiple elements.  
This is used when listing those elements inline would reduce readability.

##### Examples:
* Uses:
* Accepts:
* Exposes:
* Defines:
* Provides:

### 5.6 Grouping identical changes
Identical changes to multiple code units should be grouped under one action bullet point to avoid repetition and to keep the repeated change self contained.

This grouping rule takes precedence over the normal trace format rules that:
* Action bullet points must identify the code unit containing the change
* Independent changes to the same code unit must be grouped under one action bullet point

When grouping identical changes, the action bullet point identifies the repeated change, while the child bullet points enumerate all affected code units, including code units with unrelated changes documented elsewhere.

##### Incorrect:
The group is incomplete because validation for `method1()` is documented elsewhere.
```
Updated api.py:
   *Updated method1():
      *Removed obsolete fallback
      *Improved error handling
      *Added validation
   *Added validation to API:
      *method2()
      *method3()
```

##### Correct:
```
Updated api.py:
   *Updated method1():
      *Removed obsolete fallback
      *Improved error handling
   *Added validation to API:
      *method1()
      *method2()
      *method3()
```

Inline grouping may also be used for a small number of code units.  
Structured grouping should be preferred when grouping many code units.

##### Inline example:
```
Updated command.py:
   *Updated execute() and undo() to add validation
```

##### Structured example:
```
Updated api.py:
   *Added request logging:
      *create_user()
      *update_user()
      *delete_user()
      *get_user()
```

### 5.7 Structure templates
Structure templates define valid patterns for file sections.  
They act as building blocks for constructing a complete trace body.  
The acronym next to each structure template indicates the hierarchy levels used by the structure.

##### Each letter represents one level:
F = File  
A = Action  
B = Behaviour  
D = Detail

##### Example:
The detail structure has the acronym "FABD", meaning it includes file, action, behaviour and detail levels.

#### 5.7.1 File structure (F)
##### Examples:
```
Added directory example/
```
```
Moved file.txt to archive/
```
```
Renamed old_name.py to new_name.py
```

#### 5.7.2 Action structure (FA)
##### Examples:
```
Updated file.py:
   *Refactored data processing logic
```
```
Updated configuration.py:
   *Renamed variable endpoint to base_url
   *Removed unused constant DEFAULT_TIMEOUT
```

##### Examples (recursive):
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

#### 5.7.3 Behaviour structure (FAB)
##### Examples:
```
Updated service.py:
   *Added caching layer:
      -Stores results to prevent repeated computation
      -Invalidates cache on update
```
```
Updated authenticator.py:
   *Added token validation:
      -Checks signature against secret key
      -Rejects expired tokens
```

##### Examples (recursive):
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

#### 5.7.4 Detail structure (FABD)
##### Examples:
```
Updated validator.py:
   *Added validation system:
      -Validates user input:
         >Rejects empty values
         >Validates numeric range
         >Ensures string length limits
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

##### Examples (recursive):
```
Updated config.py:
   *Updated configuration structures:
      -Defines:
         >Connection:
            >timeout
            >retry_count
         >Authentication:
            >username
            >password
```
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

## 6 Complete examples
### 6.1 Summary example
```
Added import row validation

This commit prevents malformed import rows from reaching the import processing pipeline.

*Added import row validation:
   -Rejects rows with missing required fields before processing
   -Rejects rows with invalid field types before processing
   -Reports validation failures using the existing import error format
*Added validation test coverage:
   -Verifies missing required fields are rejected
   -Verifies invalid field types are rejected
```

### 6.2 Trace example
```
Added import row validation

This commit prevents malformed import rows from reaching the import processing pipeline.

Updated src/import/parser.py:
   *Added validate_import_row():
      -Rejects malformed rows before processing:
         >Missing required fields
         >Invalid field types
      -Reports validation failures using the existing import error format
   *Updated parse_import_row():
      -Uses validate_import_row() before processing import rows

Updated tests/import/test_parser.py:
   *Added import row validation tests:
      -Verifies missing required fields are rejected
      -Verifies invalid field types are rejected
```

## 7 Commit scope
Commits should represent one coherent change whenever practical.

A commit does not need to be perfectly minimal or perfectly pure.  
Related updates to documentation, tests, comments or supporting systems may be included when they belong to the same change.

Commit scope should balance atomicity, readability and practical completeness.  
Documentation and tests should generally be updated together with the change, unless doing so would make the commit too broad.

Unrelated changes should be split into separate commits.  
The goal is not to make every commit as small as possible, but to keep each commit coherent, understandable and useful.
