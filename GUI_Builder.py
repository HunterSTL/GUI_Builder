import os
import sys
import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

#──────────────────────────────────────────────────────────────────────────────
#Constants / Theme
#──────────────────────────────────────────────────────────────────────────────
TITLE_BAR_COLOR = "#202020"
BACKGROUND_COLOR = "#404040"
BUTTON_COLOR = "#505050"
ENTRY_COLOR = "#606060"
TEXT_COLOR = "#FFFFFF"
SELECTION_COLOR = "#33A1FD"

SELECTION_WIDTH = 2
SELECTION_DASH = (3, 2)
SELECTION_PADDING = 3
#──────────────────────────────────────────────────────────────────────────────
#Data Models
#──────────────────────────────────────────────────────────────────────────────
class IdCounters:
    label = 1
    entry = 1
    button = 1

@dataclass
class BaseWidgetData:
    id: Optional[str] = None
    x: int = 0
    y: int = 0
    bg: str = BACKGROUND_COLOR
    fg: str = TEXT_COLOR
    anchor: str = "sw"

@dataclass
class LabelWidgetData(BaseWidgetData):
    text: str = "Label"

    def create_id(self):
        self.id = f"label{IdCounters.label}"
        IdCounters.label += 1

@dataclass
class EntryWidgetData(BaseWidgetData):
    def create_id(self):
        self.id = f"entry{IdCounters.entry}"
        IdCounters.entry += 1

@dataclass
class ButtonWidgetData(BaseWidgetData):
    text: str = "Button"

    def create_id(self):
        self.id = f"button{IdCounters.button}"
        IdCounters.button += 1


@dataclass
class GUIWindow:
    title: str
    width: int
    height: int
    bg_color: str
    widgets: List[BaseWidgetData] = field(default_factory=list)
    selected_widgets: List[BaseWidgetData] = field(default_factory=list)

    def add_widget(self, widget: BaseWidgetData):
        self.widgets.append(widget)
#──────────────────────────────────────────────────────────────────────────────
#Selection Manager (highlight/selection logic)
#──────────────────────────────────────────────────────────────────────────────
class SelectionManager:
    """
    Manages multi-selection of canvas window items and their highlight rectangles.
    """
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self._selected: Set[int] = set()          #selected canvas item IDs (window items)
        self._rects: Dict[int, int] = {}          #window_id -> rectangle_id

    def clear(self):
        for item_id in list(self._selected):
            self._remove_highlight(item_id)
        self._selected.clear()

    def select_only(self, item_id: Optional[int]):
        if item_id is None:
            self.clear()
            return
        for other in list(self._selected):
            if other != item_id:
                self._remove_highlight(other)
        self._selected = {item_id}
        self._ensure_highlight(item_id)

    def toggle(self, item_id: Optional[int]):
        if item_id is None:
            return
        if item_id in self._selected:
            self._remove_highlight(item_id)
            self._selected.remove(item_id)
        else:
            self._selected.add(item_id)
            self._ensure_highlight(item_id)

    def selected_ids(self) -> Set[int]:
        return set(self._selected)

    def refresh(self, item_id: int):
        if item_id in self._selected:
            self._ensure_highlight(item_id)

    def refresh_all(self):
        for item_id in list(self._selected):
            self._ensure_highlight(item_id)

    #Internal helpers
    def _ensure_highlight(self, item_id: int):
        bbox = self.canvas.bbox(item_id)
        if not bbox:
            return
        x1, y1, x2, y2 = bbox
        x1 -= SELECTION_PADDING
        y1 -= SELECTION_PADDING
        x2 += SELECTION_PADDING
        y2 += SELECTION_PADDING

        rect_id = self._rects.get(item_id)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.coords(rect_id, x1, y1, x2, y2)
        else:
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=SELECTION_COLOR,
                width=SELECTION_WIDTH,
                dash=SELECTION_DASH,
                fill=""
            )
            self._rects[item_id] = rect_id
        self.canvas.tag_raise(rect_id)

    def _remove_highlight(self, item_id: int):
        rect_id = self._rects.pop(item_id, None)
        if rect_id and self.canvas.type(rect_id) == "rectangle":
            self.canvas.delete(rect_id)
#──────────────────────────────────────────────────────────────────────────────
#GUI Builder (Controller + View)
#──────────────────────────────────────────────────────────────────────────────
class GUIBuilder:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.config(bg=BACKGROUND_COLOR)
        self.root.title("Tkinter GUI Builder Setup")

        #Data & canvas references
        self.gui_window: Optional[GUIWindow] = None
        self.canvas: Optional[tk.Canvas] = None
        self.selection: Optional[SelectionManager] = None

        #Mapping: canvas window item id -> model object (LabelWidgetData/EntryWidgetData/ButtonWidgetData)
        self.widget_map: Dict[int, BaseWidgetData] = {}

        #Insertion point (updated on right-click)
        self.click_x: Optional[int] = None
        self.click_y: Optional[int] = None

        self._try_set_icon()
        self._try_enable_dark_titlebar()

        #Top controls (window config + palette)
        self._build_setup_ui()
    #──────────────────────────────────────────────────────────────────────────
    #Setup UI
    #──────────────────────────────────────────────────────────────────────────
    def _build_setup_ui(self):
        #Window title
        tk.Label(self.root, text="Window Title:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=0, column=0, padx=5, sticky="E")
        self.entry_window_title = tk.Entry(self.root, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_title.grid(row=0, column=1, columnspan=3, pady=3, sticky="EW")

        #Width / Height
        tk.Label(self.root, text="Window Width:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=1, column=0, padx=5, sticky="E")
        self.entry_window_width = tk.Entry(self.root, width=15, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_width.insert(0, "800")
        self.entry_window_width.grid(row=1, column=1, pady=3, sticky="EW")

        tk.Label(self.root, text="Height:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=1, column=2, padx=5, sticky="E")
        self.entry_window_height = tk.Entry(self.root, width=15, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_height.insert(0, "600")
        self.entry_window_height.grid(row=1, column=3, pady=3, sticky="EW")

        #Colors
        tk.Label(self.root, text="Background Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=2, column=0, padx=5, sticky="E")
        self.label_example_background = tk.Label(self.root, bg=BACKGROUND_COLOR)
        self.label_example_background.grid(row=2, column=1, columnspan=2, padx=1, sticky="EW")
        tk.Button(self.root, text="Select", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("background", "bg"))\
            .grid(row=2, column=3, padx=5, pady=2, sticky="EW")

        tk.Label(self.root, text="Label Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=3, column=0, padx=5, sticky="E")
        self.label_example_label = tk.Label(self.root, text="Example", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        self.label_example_label.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")
        tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("label", "bg"))\
            .grid(row=3, column=3, padx=5, pady=2, sticky="EW")
        tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("label", "fg"))\
            .grid(row=3, column=4, padx=5, pady=2, sticky="EW")

        tk.Label(self.root, text="Entry Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=4, column=0, padx=5, sticky="E")
        self.entry_example_entry = tk.Entry(self.root, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_example_entry.insert(0, "Example")
        self.entry_example_entry.grid(row=4, column=1, columnspan=2, sticky="EW")
        tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("entry", "bg"))\
            .grid(row=4, column=3, padx=5, pady=2, sticky="EW")
        tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("entry", "fg"))\
            .grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        tk.Label(self.root, text="Button Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
            .grid(row=5, column=0, padx=5, sticky="E")
        self.button_example_button_color = tk.Button(self.root, text="Example", bg=BUTTON_COLOR, fg=TEXT_COLOR)
        self.button_example_button_color.grid(row=5, column=1, columnspan=2, sticky="EW")
        tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("button", "bg"))\
            .grid(row=5, column=3, padx=5, pady=2, sticky="EW")
        tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("button", "fg"))\
            .grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        #Color dictionaries & examples
        self.colors = {
            "background": {"bg": BACKGROUND_COLOR},
            "label": {"bg": BACKGROUND_COLOR, "fg": TEXT_COLOR},
            "entry": {"bg": ENTRY_COLOR, "fg": TEXT_COLOR},
            "button": {"bg": BUTTON_COLOR, "fg": TEXT_COLOR},
        }
        self.example_widgets = {
            "background": self.label_example_background,
            "label": self.label_example_label,
            "entry": self.entry_example_entry,
            "button": self.button_example_button_color,
        }

        #Create button
        tk.Button(self.root, text="Create GUI Window", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=self.create_gui_window)\
            .grid(row=6, column=0, padx=5, pady=10)
    #──────────────────────────────────────────────────────────────────────────
    #Platform niceties
    #──────────────────────────────────────────────────────────────────────────
    def _try_set_icon(self):
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def _try_enable_dark_titlebar(self):
        if sys.platform != "win32":
            return
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int(1)),
            )
        except Exception:
            #Silently ignore if not supported
            pass

    #──────────────────────────────────────────────────────────────────────────
    #Palette helpers
    #──────────────────────────────────────────────────────────────────────────
    def choose_color(self, element_type: str, attribute: str):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[element_type][attribute] = color
            self.example_widgets[element_type].config({attribute: color})

    #──────────────────────────────────────────────────────────────────────────
    #Design window + canvas
    #──────────────────────────────────────────────────────────────────────────
    def create_gui_window(self):
        width_str = self.entry_window_width.get()
        height_str = self.entry_window_height.get()
        if not width_str.isdigit() or not height_str.isdigit():
            messagebox.showerror("Input Error", "Enter an integer value for window width and height!")
            return

        title = self.entry_window_title.get()
        width = int(width_str)
        height = int(height_str)

        self.root.withdraw()  #Hide setup window

        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry(f"{width}x{height}")

        canvas = tk.Canvas(top, bg=self.colors["background"]["bg"])
        canvas.pack(fill="both", expand=True)

        #Store for later
        self.gui_window = GUIWindow(title, width, height, self.colors["background"]["bg"])
        self.canvas = canvas
        self.selection = SelectionManager(canvas)
        self.widget_map.clear()

        #Context menu (right click)
        menu = tk.Menu(top, tearoff=0)
        menu.add_command(label="Add Label", command=lambda: self.add_label())
        menu.add_command(label="Add Entry", command=lambda: self.add_entry())
        menu.add_command(label="Add Button", command=lambda: self.add_button())

        def show_menu(event):
            self.click_x, self.click_y = event.x, event.y
            menu.post(event.x_root, event.y_root)

        #Canvas clicks
        canvas.bind("<Button-3>", show_menu)  # right click
        canvas.bind("<Button-1>", self._on_canvas_left_click)
        canvas.bind("<Control-Button-1>", self._on_canvas_ctrl_left_click)

    #──────────────────────────────────────────────────────────────────────────
    #Event handlers (canvas)
    #──────────────────────────────────────────────────────────────────────────
    def _on_canvas_left_click(self, event):
        # Clicking empty canvas clears selection
        item_id = self._find_topmost_window_at(event.x, event.y)
        if item_id is None and self.selection:
            self.selection.clear()
            self._sync_selected_widgets()

    def _on_canvas_ctrl_left_click(self, event):
        # Ctrl+click on empty canvas → no-op (keep selection)
        pass
    #──────────────────────────────────────────────────────────────────────────
    #Widget adders
    #──────────────────────────────────────────────────────────────────────────
    def add_label(self):
        if self.canvas is None or self.gui_window is None:
            return
        text = simpledialog.askstring("Label Text", "Enter label text:")
        if text is None:
            return

        widget = tk.Label(self.canvas, text=text,
                          bg=self.colors["label"]["bg"], fg=self.colors["label"]["fg"])
        self._create_window_for_widget(widget, LabelWidgetData(text=text))

    def add_entry(self):
        if self.canvas is None or self.gui_window is None:
            return
        widget = tk.Entry(self.canvas, bg=self.colors["entry"]["bg"], fg=self.colors["entry"]["fg"])
        self._create_window_for_widget(widget, EntryWidgetData())

    def add_button(self):
        if self.canvas is None or self.gui_window is None:
            return
        text = simpledialog.askstring("Button Text", "Enter button text:")
        if text is None:
            return

        widget = tk.Button(self.canvas, text=text,
                           bg=self.colors["button"]["bg"], fg=self.colors["button"]["fg"])
        self._create_window_for_widget(widget, ButtonWidgetData(text=text))
    #──────────────────────────────────────────────────────────────────────────
    #Widget plumbing
    #──────────────────────────────────────────────────────────────────────────
    def _create_window_for_widget(self, widget: tk.Widget, model: BaseWidgetData):
        #Fallback if user didn’t right-click first
        x = self.click_x if self.click_x is not None else 20
        y = self.click_y if self.click_y is not None else 40

        #Create model id and store model
        model.x, model.y = x, y
        model.create_id()
        self.gui_window.add_widget(model)

        #Place widget on canvas
        window_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)

        #Map window id <-> model
        self.widget_map[window_id] = model

        #Selection: bind events
        widget.bind("<Button-1>", lambda e, i=window_id: self._on_widget_left_click(e, i))
        widget.bind("<Control-Button-1>", lambda e, i=window_id: self._on_widget_ctrl_left_click(e, i))
        #Keep highlight in sync if widget resizes
        widget.bind("<Configure>", lambda e, i=window_id: self.selection and self.selection.refresh(i))

    def _on_widget_left_click(self, event, item_id: int):
        if self.selection:
            self.selection.select_only(item_id)
            self._sync_selected_widgets()
        return "break"  # stop propagation (prevents canvas clearing)

    def _on_widget_ctrl_left_click(self, event, item_id: int):
        if self.selection:
            self.selection.toggle(item_id)
            self._sync_selected_widgets()
        return "break"

    def _sync_selected_widgets(self):
        """Mirror selection to the data model for future features (align, delete, etc.)."""
        if self.gui_window is None or self.selection is None:
            return
        self.gui_window.selected_widgets = [
            self.widget_map[i] for i in self.selection.selected_ids() if i in self.widget_map
        ]

    #──────────────────────────────────────────────────────────────────────────
    #Canvas Helpers
    #──────────────────────────────────────────────────────────────────────────
    def _find_topmost_window_at(self, x: int, y: int) -> Optional[int]:
        if self.canvas is None:
            return None
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):  # last is top-most
            if self.canvas.type(item) == "window":
                return item
        return None
#──────────────────────────────────────────────────────────────────────────────
#Main
#──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    builder = GUIBuilder(root)
    root.mainloop()