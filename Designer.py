import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Dict, Optional
from CanvasManager import CanvasManager
from SelectionManager import SelectionManager
from ToolbarManager import ToolbarManager
from DataModels import *
from Theme import *
from PIL import ImageTk

class Designer:
    def __init__(self, parent: tk.Tk, title: str, width: int, height: int, colors: dict, icon: ImageTk.PhotoImage):
        self.parent = parent
        self.colors = colors
        self.icon = icon
        self.grid_size = GRID_SIZE

        #create window
        self.top = tk.Toplevel(parent)
        self.top.geometry(f"{width}x{height}")

        #create instance of GUIWindow to store dimensions, title and color pallette
        self.gui_window = GUIWindow(title, width, height, self.colors["background"]["bg"])

        #dictionary to map integer IDs to the instances of the widgets
        self.widget_map: Dict[int, BaseWidgetData] = {}

        #last right-click position for insertion
        self.click_x: Optional[int] = None
        self.click_y: Optional[int] = None

        #create title bar
        self._create_title_bar()

        #create instance of CanvasManager
        self.canvas_manager = CanvasManager(
            parent=self.top,
            width=width,
            height=height,
            bg_color=self.colors["background"]["bg"],
            grid_size=GRID_SIZE,
            grid_color=GRID_COLOR
        )

        self.canvas = self.canvas_manager.create_canvas()

        #create instance of SelectionManager to store selected widgets (as integer IDs)
        self.selection_manager = SelectionManager(self.canvas)

        self.canvas_manager.bind_events(
            self._show_menu,
            {
                "press": self.selection_manager.handle_canvas_press,
                "drag": self.selection_manager.handle_canvas_drag,
                "release": lambda e: self.selection_manager.handle_canvas_release(e, self._sync_selected_widgets)
            },
            self._move_selection,
            self._delete_selected_widgets
        )

        #create instance of ToolbarManager to store theme and function callbacks
        self.toolbar_manger = ToolbarManager(
            parent=self.top,
            theme={
                "toolbar_color": TOOLBAR_COLOR,
                "button_color": BUTTON_COLOR,
                "text_color": TEXT_COLOR,
                "menu_color": MENU_COLOR
            },
            callbacks={
                "snap_to_grid": self._snap_to_grid,
                "align_left": self._snap_to_grid,   #currently place holder
                "align_top": self._snap_to_grid,    #currently place holder
                "toggle_grid": self.canvas_manager.toggle_grid
            }
        )

        self.toolbar_manger.create_toolbar()

        self._add_widget_menu()

    #create title bar
    def _create_title_bar(self):
        def start_move(event):
            self._drag_start_x = event.x_root
            self._drag_start_y = event.y_root
            self._win_x = self.top.winfo_x()
            self._win_y = self.top.winfo_y()

        def do_move(event):
            dx = event.x_root - self._drag_start_x
            dy = event.y_root - self._drag_start_y
            self.top.geometry(f"+{self._win_x + dx}+{self._win_y + dy}")

        #create custom title bar
        self.top.overrideredirect(True)
        title_bar = tk.Frame(self.top, bg=TITLE_BAR_COLOR)
        title_bar.pack(fill="x")
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        #add icon
        icon_label = tk.Label(title_bar, image=self.icon, bg=TITLE_BAR_COLOR)
        icon_label.pack(side="left", padx=2, pady=2)
        icon_label.bind("<Button-1>", start_move)
        icon_label.bind("<B1-Motion>", do_move)

        #add title
        title_label = tk.Label(title_bar, text=self.gui_window.title, bg=TITLE_BAR_COLOR, fg=TITLE_BAR_TEXT_COLOR)
        title_label.pack(side="left")
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<B1-Motion>", do_move)

        #add close button
        close_button = tk.Button(title_bar, text=" X ", bg=TITLE_BAR_COLOR, fg=TITLE_BAR_TEXT_COLOR, relief="flat", command=lambda: self.top.destroy())
        close_button.pack(side="right")

    #create add widget menu
    def _add_widget_menu(self):
        self.menu = tk.Menu(self.top, bg=TOOLBAR_COLOR, fg=TEXT_COLOR, tearoff=0)
        self.menu.add_command(label="Add Label", command=self.add_label)
        self.menu.add_command(label="Add Entry", command=self.add_entry)
        self.menu.add_command(label="Add Button", command=self.add_button)

    #post context menu
    def _show_menu(self, event):
        self.click_x, self.click_y = event.x, event.y
        self.menu.post(event.x_root, event.y_root)

    #add new label
    def add_label(self):
        text = simpledialog.askstring("Label Text", "Enter label text:", parent=self.top)
        if text is None:
            return
        widget = tk.Label(
            self.canvas,
            text=text,
            bg=self.colors["label"]["bg"],
            fg=self.colors["label"]["fg"]
        )
        self._create_window_for_widget(widget, LabelWidgetData(text=text))
        self.canvas.focus_set()

    #add new entry
    def add_entry(self):
        widget = tk.Entry(
            self.canvas,
            bg=self.colors["entry"]["bg"],
            fg=self.colors["entry"]["fg"]
        )
        self._create_window_for_widget(widget, EntryWidgetData())

    #add new button
    def add_button(self):
        text = simpledialog.askstring("Button Text", "Enter button text:", parent=self.top)
        if text is None:
            return
        widget = tk.Button(
            self.canvas,
            text=text,
            bg=self.colors["button"]["bg"],
            fg=self.colors["button"]["fg"]
        )
        self._create_window_for_widget(widget, ButtonWidgetData(text=text))
        self.canvas.focus_set()

    #create window for widget
    def _create_window_for_widget(self, widget: tk.Widget, model: BaseWidgetData):
        x = self.click_x if self.click_x is not None else 20
        y = self.click_y if self.click_y is not None else 40

        model.x, model.y = x, y
        model.create_id()

        #append model to GUIWindow.widgets
        self.gui_window.add_widget(model)

        #create window for model
        window_id = self.canvas.create_window(x, y, window=widget, anchor=model.anchor)

        #map window id to model
        self.widget_map[window_id] = model

        def _on_press(e, i=window_id):
            #start drag
            self.selection_manager.start_widget_drag(e)
            #handle widget click (toggle or select_only based on CTRL key)
            return self.selection_manager.handle_widget_click(e, i, self._sync_selected_widgets)

        #start drag and handle selection of widget
        widget.bind("<ButtonPress-1>", _on_press)

        #add or remove widget from selection
        widget.bind("<Control-Button-1>", lambda e, i=window_id: self.selection_manager.handle_widget_ctrl_click(e, i, self._sync_selected_widgets))

        #move widgets based on mouse movement
        widget.bind("<B1-Motion>", lambda e: self.selection_manager.handle_widget_drag(e, self.widget_map, self._group_clamped_delta))

        #reset drag state
        widget.bind("<ButtonRelease-1>", lambda e: self.selection_manager.end_widget_drag())

        #keep outlines in sync when widget resizes
        widget.bind("<Configure>", lambda e, i=window_id: self.selection_manager and self.selection_manager.refresh(i))

    #move selected widgets
    def _move_selection(self, dx, dy):
        if not self.selection_manager:
            return
        dx, dy = self._group_clamped_delta(dx, dy)
        for item_id in self.selection_manager.selected_ids():
            #move widget in canvas
            self.canvas.move(item_id, dx, dy)

            #update model data
            widget = self.widget_map.get(item_id)
            if widget:
                widget.x += dx
                widget.y += dy

            #update highlight
            self.selection_manager.refresh(item_id)

    #compute clamped delta, so that widget cannot be moved outside the GUI window
    def _group_clamped_delta(self, dx: int, dy: int) -> tuple[int, int]:
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx_clamped, dy_clamped = dx, dy

        for item_id in self.selection_manager.selected_ids():
            bbox = self.canvas.bbox(item_id)
            if not bbox:
                continue
            x0, y0, x1, y1 = bbox
            min_dx = -x0
            max_dx = canvas_width - x1
            min_dy = -y0
            max_dy = canvas_height - y1
            dx_clamped = max(min_dx, min(max_dx, dx_clamped))
            dy_clamped = max(min_dy, min(max_dy, dy_clamped))

        return dx_clamped, dy_clamped

    #update selected widgets in GUI window
    def _sync_selected_widgets(self):
        self.gui_window.selected_widgets = [
            self.widget_map[i] for i in self.selection_manager.selected_ids() if i in self.widget_map
        ]

    #snap selected widgets to grid
    def _snap_to_grid(self):
        if not self.selection_manager:
            return
        for item_id in self.selection_manager.selected_ids():
            widget = self.widget_map.get(item_id)
            new_x, new_y = round(widget.x / self.grid_size) * self.grid_size, round(widget.y / self.grid_size) * self.grid_size
            dx, dy = new_x - widget.x, new_y - widget.y

            #move widget in canvas
            self.canvas.move(item_id, dx, dy)

            #update model data
            widget.x, widget.y = new_x, new_y

            #update highlight
            self.selection_manager.refresh(item_id)

    def _delete_selected_widgets(self):
        if not self.selection_manager:
            return
        if messagebox.askyesno("Delete", "Delete selected widgets?"):
            for item_id in [i for i in self.selection_manager.selected_ids() if self.canvas.type(i) == "window"]:
                #delete widget
                self.canvas.delete(item_id)
                #delete model
                self.widget_map.pop(item_id, None)
                #clear selection
                self.selection_manager.clear()