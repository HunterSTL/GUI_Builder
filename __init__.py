"""
===========================================
Tkinter GUI Builder - Package Documentation
------------------------------------------------------------------------
This package provides a lightweight, canvas-based GUI designer for Tkinter.
It includes:
- A setup wizard for theming and initial configuration
- A visual designer window with a canvas for placing widgets
- A right-side attributes panel with two-way binding
- Selection and drag gestures for widget manipulation
- A toolbar with common actions (grid toggle, alignment, snapping)

Widgets are placed as "window items" on a Tkinter Canvas, and a data model
keeps their properties synchronized with the live UI.
===========================================
Module map
------------------------------------------------------------------------
"Theme.py":
    Central theme & constants (colors, selection styling, grid, nudge sizes),
    plus "ATTRIBUTE_CONFIG" and "DISPLAY_NAMES" for building the attributes panel.

"DataModels.py":
    Defines dataclasses for GUIWindow and widgets (Label, Entry, Button).
    Tracks attributes like x/y position, width, height, colors, and anchor.
    Includes ID counters for unique widget naming.

"SetupWizard.py":
    Provides a configuration wizard for setting window title, size, colors,
    and icon before launching the Designer.

"Designer.py":
    The main orchestrator. Creates and wires managers:
    CanvasManager, SelectionManager, WidgetManager, ToolbarManager,
    and AttributesPanelManager. Handles context menus, keyboard nudges,
    and selection changes.

"CanvasManager.py":
    Creates and packs the main Canvas, toggles grid visualization,
    and binds global canvas events (context menu, selection, keyboard moves).

"SelectionManager.py":
    Manages widget selection, draws outlines, handles rectangle selection,
    and supports drag operations. Updates model positions and refreshes
    the attributes panel during moves.

"WidgetManager.py":
    Adds widgets (Label, Entry, Button) to the canvas as window items.
    Maintains a widget map linking canvas IDs to models and Tk widgets.
    Applies attribute changes and supports snapping and deletion.

"AttributesPanelManager.py":
    Builds the attributes panel dynamically based on widget type.
    Implements two-way binding: panel changes update the model and widget,
    and widget moves update the panel silently.

"ToolbarManager.py":
    Creates a toolbar with menus for widget actions and grid toggling.

"App.py":
    Entry point. Launches the SetupWizard and starts the Tkinter main loop.

"__init__.py":
    Provides package-level documentation and re-exports main classes for convenience.
===========================================
Core Features
------------------------------------------------------------------------
- Two-way binding between attributes panel and widgets
- Pixel-based positioning and sizing via Canvas window items
- Live updates during drag and keyboard nudges
- Extensible architecture for adding new widget types and attributes
===========================================
"""