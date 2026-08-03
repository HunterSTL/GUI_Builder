## 1. [Done] No error handling on file I/O in `open_project` (data loss / crash risk)

In `AppController.open_project`, the file is read with a bare `open` / `json.load` and no try/except. If the file is malformed JSON, or `ProjectDocument.from_json` raises a `ValueError` (which it explicitly does for bad width/height), the exception bubbles up uncaught and crashes the app with a traceback instead of showing a user-facing dialog. The same applies to `save_project` and `save_project_as` — an `OSError` (permissions, disk full) is completely silent to the user.

```python
with open(file_path, "r", encoding="utf-8") as file:
    file_contents = json.load(file)   # no try/except
```

Every file I/O path needs a `try/except` with a `messagebox.showerror`.

---

## 2. [Done] `save_project` can silently corrupt or lose work when `self.designer` is `None`

In `AppController.save_project`, there is no guard for `self.designer` being `None`. If somehow `save_project` is called (e.g. via the event bus) when no designer is open, `self.designer.app_state.project.to_json()` raises an `AttributeError`. The unsaved changes prompt in `new_project` / `open_project` calls `save_project` if the user answers "Save", and `save_project_as` does the same. If that path is hit while `self.designer` is being torn down (race or re-entrancy), the save silently fails and returns without saving.

---

## 3. [Done] The `SetupWizard` does not close or re-show the startup window on cancel/close

When `new_project` is called, `self.root.withdraw()` hides the startup window, then the wizard is created. If the user closes the wizard via the X button, `exit_callback` (`exit_app`) destroys `self.root` entirely. There is no path where the user cancels the wizard and returns to the startup window. Closing the wizard quits the whole application, which is unexpected and non-standard. A "Cancel" button or a wizard-close handler that calls `self.root.deiconify()` is needed.

---

## 4. [Done] The `attribute.changed` event is subscribed but bypassed — the callback is double-wired

In `Designer._subscribe_functions_to_events`:
```python
self.designer_event_bus.subscribe("attribute.changed", self._on_attribute_changed)
```
But `AttributesPanelView` is constructed with `on_attribute_changed_callback=self._on_attribute_changed`, so it calls `_on_attribute_changed` directly. The event subscription for `attribute.changed` is dead code — nothing emits that event through the router. This is an architecture violation: the panel bypasses the event system entirely and calls the Designer method directly. According to the project's own conventions, controllers must emit events via `EventRouter`.

---

## 5. [Done] `EventBus.emit` stops dispatching to remaining subscribers when one raises an error

The conventions document explicitly states: *"Must not stop dispatching if a subscriber raises an error."* But the implementation wraps the loop in try/except and re-raises immediately:

```python
for function in subscribers:
    try:
        function(**kwargs)
    except Exception as e:
        raise ValueError(...) from e   # stops iteration
```

If subscriber #1 of three raises, subscribers #2 and #3 never fire. This violates the stated contract and will cause unpredictable behavior in multi-subscriber scenarios.

---

## 6. [Done] `MoveWidgetsTo.execute()` is a no-op if called before `freeze_final_positions()`

`MoveWidgetsTo` is an interactive command. If `freeze_final_positions()` is never called before `execute()`, `_final_positions` is an empty dict and `execute()` silently does nothing. There is no guard or assertion. This is exploitable via redo — if `freeze_final_positions` was skipped due to a bug, redo would silently not move anything. The command should raise if executed with an empty `_final_positions`.

---

## 7. Bounding box computation uses integer division and introduces drift on odd sizes with non-NW anchors

In `Geometry.compute_model_bounding_box` and `allowed_x_range` / `allowed_y_range`, centering is computed as:
```python
left = x - (width // 2)
right = x + (width - (width // 2))
```
For a widget with width=5: left = x-2, right = x+3. For width=6: left = x-3, right = x+3. This is asymmetric and means the bounding box right edge is always ≥ left edge, but the center point is not exactly `x`. When snap-to-grid and align operations use these boxes iteratively, odd-pixel-width widgets will accumulate position drift on each snap/align cycle.

---

## 8. [Done] Paste always places widgets at their copied coordinates — no offset

`PasteWidgetsFromClipboard` restores widgets to their exact original x,y coordinates from the clipboard. Pasting multiple times results in all pastes stacking exactly on top of each other. There is no paste offset (e.g. +10/+10 per paste as is standard in most GUI editors). The user has no visual feedback that the paste happened at all.

---

## 9. Cut does not confirm deletion but delete does

`EditActions.cut` calls `self.copy()` then `DeleteWidgets` directly without calling `confirm_delete_callback`. So deleting one widget via Delete asks for confirmation, but cutting it via Ctrl+X does not. This is inconsistent. While not asking for confirmation on cut is arguably standard UX, it violates the codebase's own deletion contract since the same `DeleteWidgets` command is used in both cases.

---

## 10. `selection_handle_click` with non-additive mode does not deselect other widgets

In `AppState.selection_handle_click`:
```python
if is_additive:
    self.selection_toggle(model_id)
else:
    if not self.selection_contains(model_id):
        self.selection_select_only(model_id)
```
If the user clicks a widget that is already selected (non-additive), nothing happens — the other selected widgets remain selected. Standard behavior is: non-additive click on any widget replaces the selection with just that widget. This means after a multi-select, clicking one of the already-selected widgets in non-additive mode does not reduce the selection to just that widget.

---

## 11. [Done] `_update_attributes_panel_visibility` is called only on `selection_change`, not on every `_on_changed_state`

After a `set_model_attribute` call (e.g. changing text from the panel), `dirty_model_ids` is populated and `_on_changed_state` runs `_do_soft_render`. But `_update_attributes_panel_visibility` — which calls `attributes_panel_controller.refresh(model)` — is only called when `state.selection_change` is True. If the model changes in a way that affects panel state (e.g. anchor changes the spinbox limits) but selection_change is False, the panel is not updated until the next selection event. The panel's spinbox limits can therefore show stale valid ranges.

---

## 12. [Done] `WidgetController.update_widget_attribute` bypasses the command stack

Attribute changes from the attributes panel call `WidgetController.update_widget_attribute`, which calls `app_state.set_model_attribute` directly. These changes are not wrapped in a `Command` and are therefore not undoable. The user can undo a drag (MoveWidgets) but cannot undo a color change or text change made via the panel. This is a significant usability gap.

---

## 13. [Done] Color picker in `AttributesPanelView.create_colorpicker` is a static label, not interactive

The method is named `create_colorpicker` and the `AttributesPanelController` routes `"colorpicker"` attributes (bg, fg) to it, but it only creates a `tk.Label` showing the current color with no click handler. Colors cannot be changed from the panel at all. The only way to set initial colors is in the SetupWizard. The comment in the code itself says "not fully implemented."

---

## 14. [Done] `allowed_x_range` / `allowed_y_range` return negative max values for oversized widgets

If a widget is wider than the canvas (e.g. a very long label), `allowed_x_range` returns `(0, canvas_width - widget_width)` where `canvas_width - widget_width` is negative. `clamp` is then called with `min=0, max=<negative>`, making the max less than the min. `clamp` returns `max(0, min(<negative>, clamped))` which returns 0, but a widget placed at 0 extends beyond the canvas. There is no check that `min <= max` before clamping.

---

## 15. [Done] `AttributesPanelController._compute_spinbox_limits` returns `None` implicitly for unknown attributes

```python
def _compute_spinbox_limits(self, attribute, model) -> tuple[int, int]:
    if attribute == "x":
        ...
    elif attribute == "y":
        ...
    elif attribute == "width":
        ...
    elif attribute == "height":
        ...
    # no else, no return
```
For any attribute that doesn't match the four branches, the method returns `None`. This is then unpacked as `min_value, max_value = self._compute_spinbox_limits(...)` in `_populate`, which raises a `TypeError: cannot unpack non-iterable NoneType`. Adding a new spinbox attribute would silently break panel construction.

---

## 16. `CustomTitlebar._do_move` uses widget-relative coordinates, causing jitter during drag

```python
def _do_move(self, event):
    dx = event.x - self.drag_anchor_x
    dy = event.y - self.drag_anchor_y
    self.parent.geometry(f"+{self.parent.winfo_x() + dx}+{self.parent.winfo_y() + dy}")
```
`event.x` and `event.y` are relative to the titlebar frame widget, not the screen. When the window moves, the widget moves with it, so on the next motion event `event.x` is still relative to the new widget position. This causes oscillation and jitter during fast drags rather than smooth movement. The correct approach is to use `event.x_root` / `event.y_root` (screen-absolute) and subtract the initial screen-absolute grab point.

---

## 17. `CanvasView.render_grid` is O(n) deletion via ID list, not tag-based

Grid lines are deleted by iterating `self.grid_lines` list individually. If the canvas has many items, this is slower than `self.canvas.delete("grid_tag")`. More importantly, if the canvas is recreated (full render), the `grid_lines` list is not cleared, so subsequent `_clear_grid` calls try to delete stale IDs that no longer exist (which Tk silently ignores, but the list grows without bound if grid is toggled many times on large canvases).

Actually checking: `render_full` in `WidgetView` destroys widgets but not the canvas itself, and `grid_lines` is a member of `CanvasView` which persists. On `_do_full_render`, `canvas_controller.render_grid()` is called, which calls `_clear_grid()` (using the existing ID list) then `_draw_grid()`. This actually works correctly since the grid lines are canvas items (not widgets), so they survive `widget_view.render_full`. The stale-list concern only applies if the canvas object itself were ever recreated, which it is not. This is a lower severity issue — the list never grows unboundedly because `_clear_grid` always clears it. However, using a tag would still be cleaner.

---

## 18. [Done] `Designer._on_changed_state` uses a magic number `10` for the full-render threshold

```python
if state.structural_change or len(state.dirty_model_ids) > 10:
    self._do_full_render()
```
The threshold of 10 is hardcoded with no explanation or constant. This means with 9 dirty models, 9 soft renders run (which may be slower than one full render), and with 11, a full render runs. The threshold is not in `CONSTANTS` and has no documented rationale for why 10 was chosen.

---

## 19. [Done] The `attribute.changed` event namespace is missing from the allowed namespaces

The conventions document lists these allowed namespaces: `app.*`, `project.*`, `selection.*`, `edit.*`, `widget.*`, `grid.*`, `debug.*`. The event `attribute.changed` is subscribed in `Designer._subscribe_functions_to_events` but `attribute` is not a defined namespace. The `EventRouter` routes it to the designer bus (correct), but it violates the namespace contract in the conventions.

---

## 20. `SetupWizard.build_project_document` uses `isdigit()` which rejects valid negative or float input with no useful error message

`width_str.isdigit()` returns False for empty string, negative numbers, and floats. The error shown is the generic "Enter an integer value" message. This is fine for a width (which must be positive), but the error message doesn't distinguish "you typed letters" from "you left it blank", which is poor UX.

---

## 21. `SelectionView.render_outline_for` is called for non-selected models with no guard

`SelectionController.render_outline_for` delegates directly to `SelectionView.render_outline_for`. The view method will create a new outline rectangle for any model ID regardless of whether it's actually selected. If somehow this method is called with a model_id not in the selection set, a spurious outline appears until the next `render_all_outlines` clears it. There is no assertion that `model_id` is currently selected.

---

## 22. `WidgetView.render_soft` does not update `width` and `height` on canvas `itemconfig` if they are `None`

If a model has `width=None` or `height=None` (which `BaseWidgetData` allows as defaults), `render_soft` passes `None` to `self.canvas.itemconfig(widget_id, width=None, height=None)`, which Tk interprets as zero, collapsing the widget visually. The model validation happens only at add-time via the preview widget path, but models restored from a corrupt or hand-edited `.tkui` file could have null dimensions.

---

## 23. [Done] `ProjectDocument.from_json` does not validate canvas dimensions against the min/max constants

The constants define `MINIMUM_CANVAS_WIDTH=200`, `MAXIMUM_CANVAS_WIDTH=5000`. `from_json` validates that width and height are valid integers but does not enforce these bounds. A `.tkui` file with `"width": 1` loads without error and opens a 1-pixel canvas. The SetupWizard validates this, but the open-file path does not.

---

## 24. [Done] `AppState.get_model_bounding_box_from_model_ids` consumes the iterator twice

```python
first_model_id = next(iter(model_ids))
...
for model_id in model_ids:
    if model_id == first_model_id:
        continue
```
`model_ids` is typed as `Iterable[str]`. If the caller passes a generator or one-time iterator, `next(iter(model_ids))` exhausts the first element and then the `for model_id in model_ids` loop starts from the same already-advanced iterator. In practice, callers pass `frozenset` which is re-iterable, so this does not currently fail. But the type annotation is wrong and could cause a silent bug if the signature is later called with a generator.

---

## 25. `CallTracer` uses `sys.setprofile` globally, which affects all threads

`CallTracer.enable()` calls `sys.setprofile(self._profiler)`. This sets the profiling function for the calling thread only (the main thread), which is correct. However, the `threading.local()` depth counter is per-thread, and if Tkinter ever calls anything on another thread, those calls will not be traced. More importantly, `sys.setprofile` is a global call — if any other library also uses `setprofile`, `CallTracer` will silently override it. This is a debug tool so the severity is low, but it's worth noting.

---

## 26. `AppState.batch()` swallows all exceptions but still calls `_notify` on clean exit — then suppresses further exceptions in `__exit__`

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    state._batch_depth -= 1
    if state._batch_depth == 0 and state._pending_notify:
        state._pending_notify = False
        state._notify()
    return False  # propagate exceptions
```
`return False` means exceptions propagate, which is correct. The comment says "so notify → re-render doesn't happen on exceptions." But `_pending_notify` could be True even when an exception is occurring — if an earlier batched mutation succeeded and set `_pending_notify`, and then a later mutation raises, `_notify()` will still be called in the except path because `return False` propagates the exception but `_notify()` has already been called. The subscriber callbacks then run with potentially inconsistent state mid-exception.

---

## 27. Debug menu is shipped in the production build with no way to disable it

The "Debug" menu is fully visible and functional in the shipped toolbar. Users can see and access "Set dirty", "Set clean", "Print command stack", etc. These are meaningful debug affordances that expose internal state, and there is no flag, environment variable, or build-time toggle to remove them.

---

## 28. `ToolbarView` stores menus in a dict but `_get_menu` raises `KeyError` with no message for unknown menu names

```python
def _get_menu(self, menu_name):
    return self._menus[menu_name][1]
```
A typo in menu name in `ToolbarController.build_toolbar` produces a raw `KeyError` with no error message. This should raise a `ValueError` following the codebase's own error-raising convention.

---

## 29. [Done] `ValidationTests.py` is not a test runner — it runs at import time and has global side effects

The validation tests file executes `run_all_test_groups()` at module level. Importing this file triggers UI creation, a `Designer` window, and all test cases. The `test_add_model_with_missing_id` test mutates shared state without cleanup. Several tests leave behind widget state in the shared `app_state`. The file is designed to be run as a script, but its design (global `app_state`, `designer` variables at module scope) makes it fragile and impossible to integrate with a normal test runner like pytest.

---

## 30. Unit tests create `tk.Tk()` instances without calling `root.destroy()` at teardown

Each of `TestAddWidgetFromModel`, `TestMoveWidget` creates `root = tk.Tk()` and `root.withdraw()` but never calls `root.destroy()` in teardown or in a `finally` block. When running the test suite, multiple `Tk` instances accumulate and are only destroyed when Python exits. On some platforms (particularly macOS) this can cause intermittent display server errors or test hangs.

---

## 31. `AppController` does not restore the startup window when the Designer is closed with unsaved changes and the user cancels

If the user opens the Designer, tries to exit (triggering the unsaved changes dialog), clicks Cancel, the Designer stays open. This is correct. But if the user closes the Designer some other way (e.g. via OS-level window close on the Toplevel), `exit_app` is emitted and the dialog fires. If the user cancels at the dialog, the Designer Toplevel was already sent a close request and the startup window remains hidden with no way to reopen it. The app is effectively frozen.

---

## 32. `WidgetView._bind_widget_events` uses `event.x_root - canvas.winfo_rootx()` which is wrong under scrolling

When the canvas is scrolled (via the viewer scrollbar), the canvas's origin is offset. `winfo_rootx()` returns the canvas's screen X position, but not accounting for scroll offset. For large canvases that are scrolled, widget events forwarded to the canvas will report incorrect coordinates. The correct conversion requires `canvas.canvasx(x)` applied to the already-computed canvas-relative coordinate, but the forwarding code uses screen coordinates directly.

---

## 33. `IdCounters` counters are stored in the `ProjectDocument` but are also incremented on paste operations, coupling ID generation to undo/redo

When `PasteWidgetsFromClipboard.execute()` is called, it calls `model.create_id(self._app_state.project.id_counters)`, which increments the counter. On undo, the model is removed but the counter is not decremented. On redo, the model is re-added with the same stored ID. This means after paste → undo → paste of a different widget → redo of the first paste, the ID counters are higher than the actual number of widgets. This is technically safe (no duplicate IDs) but the counters drift upward permanently and the numbering becomes non-sequential in the file.

---

## 34. `Theme.py` exports unused module-level constants as bare names before building the dict

`user_BACKGROUND_COLOR`, `user_TITLEBAR_COLOR` etc. are module-level variables that are only used to build `USER_THEME`. They are exported as part of the module namespace. Any code that does `from Theme import *` would pick up these implementation-detail variables. They should either be used only inside the dict literal or prefixed with `_` to mark them private.

---

## 35. `SelectionController` uses `grab_set` / `grab_release` on the canvas without error recovery

```python
try:
    self.canvas.grab_set()
except Exception:
    pass
```
The bare `except Exception: pass` silently swallows any error from `grab_set`. If `grab_set` fails, the drag continues without an input grab, meaning mouse events can be consumed by other windows. This can cause broken drag states. The error is suppressed with no logging.