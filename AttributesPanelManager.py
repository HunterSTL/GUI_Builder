import tkinter as tk
from tkinter import ttk
from Theme import *

class AttributesPanelManager:
    def __init__(self, root, frame, theme, canvas_width, canvas_height, panel_width, selection_manager, widget_manager):
        self.root = root
        self.frame = frame
        self.theme = theme
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.panel_width = panel_width
        self.selection_manager = selection_manager
        self.widget_manager = widget_manager

        self._visible = False

        self.frame.columnconfigure(0, minsize=50)

    def show(self, model):
        if self._visible:
            #already visible → refresh contents
            self._populate(model)
            return

        self.root.update_idletasks()

        #resize window
        self.root.geometry(f"{self.canvas_width + self.panel_width}x{self.canvas_height}")

        #pack attributes panel
        self.frame.pack(side="right", fill="y")

        self._populate(model)
        self._visible = True

    def hide(self):
        if not self._visible:
            #already hidden → do nothing
            return

        #resize window
        self.root.geometry(f"{self.canvas_width}x{self.canvas_height}")

        #remove attributes panel
        self.frame.pack_forget()

        #clear panel contents
        self._clear_panel()

        self._visible = False

    def _populate(self, model):
        #clear previous widgets
        self._clear_panel()

        row_index = 0

        for attribute, widget_type in ATTRIBUTE_CONFIG[model.type].items():
            #create displayname for each attribute
            self._create_displayname_label(attribute, row_index)
            #create the correct widget based on widget_type
            getattr(self, f"_create_{widget_type}")(model, attribute, row_index)
            row_index += 1

    def _clear_panel(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def _create_displayname_label(self, attribute, row):
        tk.Label(
            self.frame,
            text=DISPLAY_NAMES.get(attribute),
            bg=self.theme.get("background_color"),
            fg=self.theme.get("text_color"),
            pady=3
        ).grid(column=0, row=row, sticky="E")

    def _create_label(self, model, attribute, row):
        tk.Label(
            self.frame,
            text=getattr(model, attribute),
            bg=self.theme.get("background_color"),
            fg=self.theme.get("text_color")
        ).grid(column=1, row=row, sticky="W")

    def _create_entry(self, model, attribute, row):
        entry = tk.Entry(
            self.frame,
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            width=18
        )
        entry.insert(0, getattr(model, attribute))
        entry.grid(column=1, row=row)

    def _create_spinbox(self, model, attribute, row):
        if attribute == "x":
            max_value = self.canvas_width
        elif attribute == "y":
            max_value = self.canvas_height
        else:
            max_value = 0

        attribute_value = tk.IntVar(value=getattr(model, attribute))
        spinbox = tk.Spinbox(
            self.frame,
            from_=0,
            to=max_value,
            width=5,
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            buttonbackground=ENTRY_COLOR,
            increment=1,
            textvariable=attribute_value
        )
        spinbox.grid(column=1, row=row, sticky="W")

    def _create_colorpicker(self, model, attribute, row):
        tk.Label(
            self.frame,
            bg=getattr(model, attribute),
            width=5,
            relief="raised"
        ).grid(column=1, row=row, sticky="W")

    def _create_combobox(self, model, attribute, row):
        if attribute == "anchor":
            options = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"]
            combobox = ttk.Combobox(self.frame, values=options, width=6)
            combobox.set(model.anchor)
            combobox.grid(column=1, row=row, sticky="W")