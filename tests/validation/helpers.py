import tkinter as tk

from app_state import AppState
from commands import (
    DragWidgets,
    EditWidget
)
from designer import Designer
from events import EventBus
from model import (
    LabelWidget,
    ProjectDocument,
    ProjectTheme
)

FIRST_CANVAS_ITEM_ID = 2

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

WIDGET_WIDTH = 100
WIDGET_HEIGHT = 20

def create_valid_project_data(
    **overrides
) -> dict[str, object]:
    project_data = {
        "version": 1,
        "title": "TITLE",
        "width": CANVAS_WIDTH,
        "height": CANVAS_HEIGHT,
        "grid": {
            "size": 10,
            "color": "#ffffff",
            "visible": False
        },
        "theme": ProjectTheme().to_dict(),
        "widgets": [],
        "id_counters": {
            "label": 1,
            "entry": 1,
            "button": 1
        }
    }
    project_data.update(overrides)
    return project_data

def create_valid_widget_data(
    **overrides
) -> dict[str, object]:
    widget_data = {
        "type": "label",
        "id": "ID",
        "x": 100,
        "y": 100,
        "bg": "#000000",
        "fg": "#ffffff",
        "width": WIDGET_WIDTH,
        "height": WIDGET_HEIGHT,
        "anchor": "sw",
        "text": "TEXT"
    }
    widget_data.update(overrides)
    return widget_data

def create_valid_widget(
    **overrides
) -> LabelWidget:
    widget_data = create_valid_widget_data(**overrides)
    widget_data.pop("type")
    return LabelWidget(**widget_data)

def create_edit_widget_command() -> EditWidget:
    return EditWidget(
        widget=create_valid_widget(),
        app_state=AppState(ProjectDocument())
    )

def create_drag_widgets_command() -> DragWidgets:
    return DragWidgets(
        widgets=(create_valid_widget(),),
        app_state=AppState(ProjectDocument())
    )

def create_designer() -> Designer:
    root = tk.Tk()
    root.withdraw()

    original_deiconify = tk.Toplevel.deiconify
    tk.Toplevel.deiconify = lambda self: None   #temporarily deactivates Toplevel.deiconify to prevent the designer window from showing during tests

    try:
        designer = Designer(
            parent=root,
            project_document=ProjectDocument(),
            app_event_bus=EventBus()
        )
    except Exception:
        root.destroy()
        raise
    finally:
        tk.Toplevel.deiconify = original_deiconify

    return designer

def destroy_designer(
    designer: Designer
) -> None:
    root = designer.top.master
    root.destroy()
