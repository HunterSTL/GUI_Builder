import tkinter as tk
from typing import Union

def load_icon(path: str, size: tuple[int, int]):
    import os
    from PIL import Image, ImageTk
    from tkinter import messagebox
    try:
        if path and os.path.exists(path):
            icon = Image.open(path).convert("RGBA")
            icon = icon.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(icon)
    except Exception as e:
        messagebox.showerror("File error", f"File not supported: {e}")
        return None

class CustomTitlebar:
    def __init__(
        self,
        parent: Union[tk.Tk, tk.Toplevel],
        title: str,
        height: int,
        bg_color: str,
        fg_color: str,
        icon_path: str | None,
        on_close
    ):
        self.parent = parent
        self.title = title
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.icon_path = icon_path
        self.on_close = on_close

        self.drag_start_x = None
        self.drag_start_y = None
        self.window_x = None
        self.window_y = None

        #create frame
        self.parent.overrideredirect(True)
        self.frame = tk.Frame(
            self.parent,
            height=self.height,
            bg=self.bg_color
        )
        self.frame.pack_propagate(False)    #ensures height is respected

        #bind drag handlers
        self.frame.bind("<Button-1>", self._start_move)
        self.frame.bind("<B1-Motion>", self._do_move)

        #add icon
        if icon_path:
            self.icon = load_icon(icon_path, (20, 20))

            if self.icon:
                self.icon_label = tk.Label(
                    self.frame,
                    image=self.icon,
                    bg=self.bg_color
                )
                self.icon_label.pack(side="left", padx=2, pady=2)
                self.icon_label.bind("<Button-1>", self._start_move)
                self.icon_label.bind("<B1-Motion>", self._do_move)

        #add text
        self.label = tk.Label(
            self.frame,
            text=self.title,
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.label.pack(side="left")
        self.label.bind("<Button-1>", self._start_move)
        self.label.bind("<B1-Motion>", self._do_move)

        #add close button
        self.close_button = tk.Button(
            self.frame,
            text=" X ",
            bg=self.bg_color,
            fg=self.fg_color,
            relief="flat",
            command=self.on_close
        )
        self.close_button.pack(side="right")

    def _start_move(self, event):
        """store the initial mouse position relative to the titlebar as the drag anchor"""
        self.drag_anchor_x = event.x
        self.drag_anchor_y = event.y

    def _do_move(self, event):
        """move the window by the widget-relative mouse movement since drag start"""
        dx = event.x - self.drag_anchor_x
        dy = event.y - self.drag_anchor_y
        self.parent.geometry(f"+{self.parent.winfo_x() + dx}+{self.parent.winfo_y() + dy}")