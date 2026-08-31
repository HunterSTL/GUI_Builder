import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from collections.abc import Callable

def load_icon(
    path: str,
    size: tuple[int, int],
    parent: tk.Misc | None = None
) -> ImageTk.PhotoImage | None:
    """Load and resize an icon, displaying an error dialog if loading fails."""
    try:
        if path and os.path.exists(path):
            icon = Image.open(path).convert("RGBA")
            icon = icon.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(icon)
    except Exception as e:
        messagebox.showerror(
            "File error",
            f"File not supported: {e}",
            parent=parent
        )
        return None


class CustomTitlebar:
    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        title: str,
        height: int,
        bg_color: str,
        fg_color: str,
        icon_path: str | None,
        on_close: Callable[[], None]
    ) -> None:
        self._parent: tk.Tk | tk.Toplevel = parent
        self._title: str = title
        self._height: int = height
        self._bg_color: str = bg_color
        self._fg_color: str = fg_color
        self._icon_path: str | None = icon_path
        self._on_close: Callable[[], None] = on_close

        self._parent.overrideredirect(True)

        self._drag_anchor_x: int | None = None
        self._drag_anchor_y: int | None = None
        self._window_x: int | None = None
        self._window_y: int | None = None

        self._frame: tk.Frame = tk.Frame(
            self._parent,
            height=self._height,
            bg=self._bg_color
        )
        self._frame.pack_propagate(False)    #ensures height is respected
        self._frame.bind("<Button-1>", self._start_move)
        self._frame.bind("<B1-Motion>", self._do_move)

        if self._icon_path:
            icon = load_icon(
                path=icon_path,
                size=(20, 20),
                parent=self._parent
            )

            if icon:
                self._icon_label = tk.Label(
                    self._frame,
                    image=icon,
                    bg=self._bg_color
                )
                self._icon_label.pack(side="left", padx=2, pady=2)
                self._icon_label.bind("<Button-1>", self._start_move)
                self._icon_label.bind("<B1-Motion>", self._do_move)

        self._label: tk.Label = tk.Label(
            self._frame,
            text=self._title,
            bg=self._bg_color,
            fg=self._fg_color
        )
        self._label.pack(side="left")
        self._label.bind("<Button-1>", self._start_move)
        self._label.bind("<B1-Motion>", self._do_move)

        self._close_button: tk.Button = tk.Button(
            self._frame,
            text=" X ",
            bg=self._bg_color,
            fg=self._fg_color,
            relief="flat",
            command=self._on_close
        )
        self._close_button.pack(side="right")

    def _start_move(
        self,
        tk_event: tk.Event
    ) -> None:
        """Store the initial mouse position relative to the titlebar as the drag anchor."""
        self._drag_anchor_x = tk_event.x
        self._drag_anchor_y = tk_event.y

    def _do_move(
        self,
        tk_event: tk.Event
    ) -> None:
        """Move the window by the widget relative mouse movement since drag start."""
        dx = tk_event.x - self._drag_anchor_x
        dy = tk_event.y - self._drag_anchor_y
        self._parent.geometry(f"+{self._parent.winfo_x() + dx}+{self._parent.winfo_y() + dy}")
