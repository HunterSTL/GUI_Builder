import tkinter as tk

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
        for widget in self.frame.winfo_children():
            widget.destroy()

        self._visible = False

    def _populate(self, model):
        #clear previous widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        #test content
        tk.Label(
            self.frame, text="Attributes:",
            bg=self.theme.get("background_color"),
            fg=self.theme.get("text_color")
        ).pack(anchor="w")

        tk.Label(
            self.frame, text=f"Widget: {getattr(model, 'type', 'unknown')}",
            bg=self.theme.get("background_color"),
            fg=self.theme.get("text_color")
        ).pack(anchor="w")
