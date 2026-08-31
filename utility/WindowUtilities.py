import tkinter as tk
import sys
import ctypes

from .FileUtilities import load_icon

def force_dark_title_bar(
    window: tk.Tk | tk.Toplevel
) -> None:
    """Force a dark title bar on windows."""
    window.update_idletasks()
    if sys.platform != "win32":
        return

    use_dark_mode = ctypes.c_int(1)

    try:
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.windll.user32.GetParent(window.winfo_id()),
            20,
            ctypes.byref(use_dark_mode),
            ctypes.sizeof(use_dark_mode)
        )
    except Exception:
        pass

def set_title_bar_icon(
    window: tk.Tk | tk.Toplevel,
    path: str | None
) -> None:
    """Set the icon in the title bar to the image at the given path."""
    if not path:
        return

    photo = load_icon(
        path=path,
        size=(20, 20)
    )
    if photo:
        window.iconphoto(False, photo)

def set_minimum_window_size_from_ui(
    window: tk.Tk | tk.Toplevel,
    padding: int = 0
) -> None:
    """Set the minimum window size required to display the UI plus padding."""
    window.update_idletasks()
    window.wm_minsize(
        window.winfo_reqwidth() + padding,
        window.winfo_reqheight() + padding
    )

def center_window(
    window: tk.Tk | tk.Toplevel
) -> None:
    """Center the window on screen."""
    window.update_idletasks()
    x_offset = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
    y_offset = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
    window.geometry(f"+{x_offset}+{y_offset}")
