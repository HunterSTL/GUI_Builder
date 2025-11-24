import sys
import os
import tkinter as tk
from tkinter import colorchooser, messagebox
from theme import (BACKGROUND_COLOR, BUTTON_COLOR, ENTRY_COLOR, TEXT_COLOR)
from designer import Designer

class SetupWizard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.config(bg=BACKGROUND_COLOR)
        self.root.title("Tkinter GUI Builder – Setup")

        self._try_set_icon()
        self._try_enable_dark_titlebar()

        self._build_setup_ui()

    #UI
    def _build_setup_ui(self):
        #grid grow
        for c in range(5):
            self.root.grid_columnconfigure(c, weight=1)

        #window title
        tk.Label(self.root, text="Window Title:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
          .grid(row=0, column=0, padx=5, sticky="E")
        self.entry_window_title = tk.Entry(self.root, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_title.grid(row=0, column=1, columnspan=3, pady=3, sticky="EW")

        #width / height
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

        #colors preview and pickers
        self.colors = {
            "background": {"bg": BACKGROUND_COLOR},
            "label": {"bg": BACKGROUND_COLOR, "fg": TEXT_COLOR},
            "entry": {"bg": ENTRY_COLOR, "fg": TEXT_COLOR},
            "button": {"bg": BUTTON_COLOR, "fg": TEXT_COLOR},
        }

        #background
        tk.Label(self.root, text="Background Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
          .grid(row=2, column=0, padx=5, sticky="E")
        self.label_example_background = tk.Label(self.root, bg=self.colors["background"]["bg"])
        self.label_example_background.grid(row=2, column=1, columnspan=2, padx=1, sticky="EW")
        tk.Button(self.root, text="Select", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("background", "bg"))\
          .grid(row=2, column=3, padx=5, pady=2, sticky="EW")

        #label colors
        tk.Label(self.root, text="Label Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
          .grid(row=3, column=0, padx=5, sticky="E")
        self.label_example_label = tk.Label(
            self.root, text="Example", bg=self.colors["label"]["bg"], fg=self.colors["label"]["fg"], anchor="w"
        )
        self.label_example_label.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")
        tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("label", "bg"))\
          .grid(row=3, column=3, padx=5, pady=2, sticky="EW")
        tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("label", "fg"))\
          .grid(row=3, column=4, padx=5, pady=2, sticky="EW")

        #entry colors
        tk.Label(self.root, text="Entry Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
          .grid(row=4, column=0, padx=5, sticky="E")
        self.entry_example_entry = tk.Entry(self.root, bg=self.colors["entry"]["bg"], fg=self.colors["entry"]["fg"])
        self.entry_example_entry.insert(0, "Example")
        self.entry_example_entry.grid(row=4, column=1, columnspan=2, sticky="EW")
        tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("entry", "bg"))\
          .grid(row=4, column=3, padx=5, pady=2, sticky="EW")
        tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("entry", "fg"))\
          .grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        #button colors
        tk.Label(self.root, text="Button Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)\
          .grid(row=5, column=0, padx=5, sticky="E")
        self.button_example_button_color = tk.Button(
            self.root, text="Example", bg=self.colors["button"]["bg"], fg=self.colors["button"]["fg"]
        )
        self.button_example_button_color.grid(row=5, column=1, columnspan=2, sticky="EW")
        tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("button", "bg"))\
          .grid(row=5, column=3, padx=5, pady=2, sticky="EW")
        tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=lambda: self.choose_color("button", "fg"))\
          .grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        #cache preview widgets
        self.example_widgets = {
            "background": self.label_example_background,
            "label": self.label_example_label,
            "entry": self.entry_example_entry,
            "button": self.button_example_button_color,
        }

        #create button
        tk.Button(self.root, text="Create GUI Window", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                  command=self.launch_designer)\
          .grid(row=6, column=0, padx=5, pady=10, sticky="W")

    #Actions
    def choose_color(self, element_type: str, attribute: str):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[element_type][attribute] = color
            self.example_widgets[element_type].config({attribute: color})

    def launch_designer(self):
        width_str = self.entry_window_width.get()
        height_str = self.entry_window_height.get()

        if not width_str.isdigit() or not height_str.isdigit():
            messagebox.showerror("Input Error", "Enter an integer value for window width and height!")
            return

        title = self.entry_window_title.get()
        width = int(width_str)
        height = int(height_str)

        # Hide setup window and launch Designer
        self.root.withdraw()
        Designer(self.root, title, width, height, self.colors)

    #platform niceties
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
            pass  #silently ignore if not supported