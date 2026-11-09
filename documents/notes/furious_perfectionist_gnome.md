# Furious Perfectionist Gnome

A non-normative note about knowing when a convention is precise enough.

## Background

In my commit message conventions the grammatical subject of the behaviour level may refer to the change itself or the codebase after the change.

```
*Made widget IDs optional during widget construction:
   -Allows widgets to be constructed without assigning an ID in advance
```

Here the subject is implied to be the change.  
The behaviour could be written as "This change allows..."

```
*Replaced manual bookkeeping of grid lines with canvas tags:
   -Creates grid lines with a shared tag
```

Here the subject is implied to be the codebase after the change.  
The behaviour could be written as "The codebase now creates..."

This inconsistency infuriates the perfectionist gnome inside my head, but my rational side has learned that eliminating every ambiguity through added precision can ultimately end up making your convention framework worse.

## Conversation

**FPG:** Furious perfectionist gnome inside my head

**FPG:**	“There is an unresolved semantic distinction!”  
**Me:**	“Correct. It has no practical consequences.”

**FPG:**	“But the convention could be more precise!”  
**Me:**	“Correct. The extra precision would make it longer and less useful.”

**FPG:**	“You know how to fix it!”  
**Me:**	“Correct. I am choosing not to.”

**FPG:**	“YOU COULD ADD A RULE PERMITTING BOTH IMPLICIT SUBJECTS!”  
**Me:**	“I could.”

**FPG:**	“IT WOULD RESOLVE THE AMBIGUITY!”  
**Me:**	“Yes.”

**FPG:**	“THEN WHY AREN'T YOU DOING IT?”  
**Me:**	“Because nobody is confused.”
