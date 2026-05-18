# Commit Message Format
## 1 Title
* Concise summary of what changed
* Single line
* Past tense
* Capitalized
* No trailing punctuation

## 2 Description
* Explains what the commit achieves
* One or more full sentences
* Present tense
* No indentation
* Typically starts with "This commit [...]"
* May include an enumeration when the commit introduces or formalizes a convention or structure

## 3 Body
* Hierarchical
* Indented using 3 spaces per level
* Bullet point symbols encode the question being answered
   * \* → What changed?
	* \- → What does the code now do because of that change?
	* \> → What additional clarification is useful?
* Any bullet point that has child bullet points must end with :
* Any level may terminate the hierarchy if additional detail is not necessary
* Every file section must be separated from the previous file section by one empty line

### Hierarchy overview:
```
File:                       Where did something change?
   *Change:                 What changed?
      -Behaviour:           What does the code now do because of that change?
         >Details           What additional clarification is useful?
```

## 3.1 File level
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

## 3.2 Action level
* Describes what changed within the file
* Must name the affected code unit (method, function, class, flag, dictionary etc.) when this adds clarity
* Must also include the class name if the file contains multiple classes or the class name differs from the file name
* Past tense
* Bullet point symbol: \*
* Indentation: 3 spaces
* May include brief context in parenthesis if required to understand the change
>e.g. "Removed _move() (obsolete, as nudge and drag preview are now handled separately)"
* May be decomposed into more specific actions, that each:
   * Represent a concrete part of the action
	* Inherit the verb of the parent unless overridden
	* Use the \* bullet point
	* Are indented one level deeper than the parent bullet point (3 additional spaces)

## 3.3 Behaviour level:
* Describes behaviour that is true after the change
* Present tense
* Bullet point symbol: \-
* Indented one level deeper than the parent bullet point (3 additional spaces)
* May act as an introducer for multiple detail bullets points
>e.g. "Uses:", "Accepts:", "Exposes:", "Defines:" etc.
* May be omitted if the action level already expresses behaviour clearly, allowing the hierarchy to continue with the detail level

## 3.4 Detail level
* Used for providing additional detail about a behaviour
* Bullet point symbol: \>
* Indented one level deeper than the parent bullet point (3 additional spaces)
* May represent:
   * Additional clarification of behaviour (present tense)
   * An enumeration of elements involved in the behaviour (tense neutral)
   >e.g. methods, variables, parameters etc.
	* An enumeration of elements forming the resulting structure (tense neutral)

## 3.5 Sub-detail level
* Used for providing even more fine grained detail
* Recursively nestable
* Bullet point symbol: \>
* Indented one level deeper than the parent bullet point (3 additional spaces)

# Examples
## 1 File structure
```
Added folder example/
```

```
Moved file.txt to archive/
```

```
Renamed old_name.py to new_name.py
```

## 2 Action structure
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

## 3 Subaction structure
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

## 4 Behaviour structure
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
      -Checks signature agains secret key
      -Rejects expired tokens
```

## 5 Detail structure
### Additional clarification of behaviour (present tense):
```
Updated validator.py:
   *Added validation system:
      -Validates user input:
         >Rejects empty values
         >Validates numeric range
         >Ensures string length limits
```
### Enumeration of elements involved in the behaviour (tense neutral):
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

## 6 Detail structure without behaviour
### Enumeration of elements forming the resulting structure (tense neutral):
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