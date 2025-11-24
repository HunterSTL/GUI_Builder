import os
import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from theme import (TITLE_BAR_COLOR, TITLE_BAR_TEXT_COLOR, BACKGROUND_COLOR, BUTTON_COLOR, ENTRY_COLOR, TEXT_COLOR, TOOLBAR_COLOR)
from designer import Designer
from PIL import Image, ImageTk

def load_icon(path, size):
    try:
        if path and os.path.exists(path):
            icon = Image.open(path).convert("RGBA")
            icon = icon.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(icon)
    except Exception as e:
        messagebox.showerror("File error", f"File not supported: {e}")
        return None

class SetupWizard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.config(bg=BACKGROUND_COLOR)
        self.root.title("Tkinter GUI Builder – Setup")

        self._create_title_bar()
        self._build_setup_ui()

    #create title bar
    def _create_title_bar(self):
        def start_move(event):
            self._drag_start_x = event.x_root
            self._drag_start_y = event.y_root
            self._win_x = self.root.winfo_x()
            self._win_y = self.root.winfo_y()

        def do_move(event):
            dx = event.x_root - self._drag_start_x
            dy = event.y_root - self._drag_start_y
            self.root.geometry(f"+{self._win_x + dx}+{self._win_y + dy}")

        #create custom title bar
        self.root.overrideredirect(True)
        title_bar = tk.Frame(self.root, bg=TITLE_BAR_COLOR)
        title_bar.grid(row=0, column=0, columnspan=5, sticky="EW")
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        #add icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.icon_setup = load_icon(icon_path, (20, 20))
        if self.icon_setup:
            icon_label = tk.Label(title_bar, image=self.icon_setup, bg=TITLE_BAR_COLOR)
            icon_label.pack(side="left", padx=2, pady=2)
            icon_label.bind("<Button-1>", start_move)
            icon_label.bind("<B1-Motion>", do_move)

        #add title
        title_label = tk.Label(title_bar, text="Tkinter GUI Builder – Setup", bg=TITLE_BAR_COLOR, fg=TITLE_BAR_TEXT_COLOR)
        title_label.pack(side="left")
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<B1-Motion>", do_move)

        #add close button
        close_button = tk.Button(title_bar, text=" X ", bg=TITLE_BAR_COLOR, fg=TITLE_BAR_TEXT_COLOR, relief="flat", command=lambda: self.root.destroy())
        close_button.pack(side="right")

    #build setup UI
    def _build_setup_ui(self):
        #window title
        label_window_title = tk.Label(self.root, text="Window Title:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_window_title.grid(row=1, column=0, padx=5, sticky="E")
        self.entry_window_title = tk.Entry(self.root, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_title.grid(row=1, column=1, columnspan=3, pady=3, sticky="EW")

        #width / height
        label_window_width = tk.Label(self.root, text="Window Width:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_window_width.grid(row=2, column=0, padx=5, sticky="E")
        self.entry_window_width = tk.Entry(self.root, width=15, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_width.insert(0, "800")
        self.entry_window_width.grid(row=2, column=1, pady=3, sticky="EW")

        label_window_height = tk.Label(self.root, text="Height:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_window_height.grid(row=2, column=2, padx=5, sticky="E")
        self.entry_window_height = tk.Entry(self.root, width=15, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_height.insert(0, "600")
        self.entry_window_height.grid(row=2, column=3, pady=3, sticky="EW")

        #colors preview and pickers
        self.colors = {
            "background": {"bg": BACKGROUND_COLOR},
            "label": {"bg": BACKGROUND_COLOR, "fg": TEXT_COLOR},
            "entry": {"bg": ENTRY_COLOR, "fg": TEXT_COLOR},
            "button": {"bg": BUTTON_COLOR, "fg": TEXT_COLOR},
            "toolbar": {"bg": TOOLBAR_COLOR}
        }

        #background color
        label_background_color = tk.Label(self.root, text="Background Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_background_color.grid(row=3, column=0, padx=5, sticky="E")
        self.label_example_background = tk.Label(self.root, bg=self.colors["background"]["bg"])
        self.label_example_background.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")
        button_background_color = tk.Button(self.root, text="Select", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("background", "bg"))
        button_background_color.grid(row=3, column=3, padx=5, pady=2, sticky="EW")

        #label colors
        label_label_color = tk.Label(self.root, text="Label Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_label_color.grid(row=4, column=0, padx=5, sticky="E")
        self.label_example_label = tk.Label(self.root, text="Example", bg=self.colors["label"]["bg"], fg=self.colors["label"]["fg"], anchor="w")
        self.label_example_label.grid(row=4, column=1, columnspan=2, padx=1, sticky="EW")
        button_label_background_color = tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("label", "bg"))
        button_label_background_color.grid(row=4, column=3, padx=5, pady=2, sticky="EW")
        button_label_text_color = tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("label", "fg"))
        button_label_text_color.grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        #entry colors
        label_entry_color = tk.Label(self.root, text="Entry Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_entry_color.grid(row=5, column=0, padx=5, sticky="E")
        self.entry_example_entry = tk.Entry(self.root, bg=self.colors["entry"]["bg"], fg=self.colors["entry"]["fg"])
        self.entry_example_entry.insert(0, "Example")
        self.entry_example_entry.grid(row=5, column=1, columnspan=2, sticky="EW")
        button_entry_background_color = tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("entry", "bg"))
        button_entry_background_color.grid(row=5, column=3, padx=5, pady=2, sticky="EW")
        button_entry_text_color = tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("entry", "fg"))
        button_entry_text_color.grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        #button colors
        label_button_color = tk.Label(self.root, text="Button Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_button_color.grid(row=6, column=0, padx=5, sticky="E")
        self.button_example_button_color = tk.Button(self.root, text="Example", bg=self.colors["button"]["bg"], fg=self.colors["button"]["fg"])
        self.button_example_button_color.grid(row=6, column=1, columnspan=2, sticky="EW")
        button_button_background_color = tk.Button(self.root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("button", "bg"))
        button_button_background_color.grid(row=6, column=3, padx=5, pady=2, sticky="EW")
        button_button_text_color = tk.Button(self.root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("button", "fg"))
        button_button_text_color.grid(row=6, column=4, padx=5, pady=2, sticky="EW")

        #cache preview widgets
        self.example_widgets = {
            "background": self.label_example_background,
            "label": self.label_example_label,
            "entry": self.entry_example_entry,
            "button": self.button_example_button_color
        }

        #icon
        label_icon = tk.Label(self.root, text="Icon:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label_icon.grid(row=7, column=0, sticky="E")

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.icon = load_icon(icon_path, (20, 20))
        if self.icon:
            self.label_icon_preview = tk.Label(self.root, image=self.icon, bg=BACKGROUND_COLOR)
            self.label_icon_preview.grid(row=7, column=1, sticky="W")
        else:
            self.label_icon_preview = tk.Label(self.root, bg=BACKGROUND_COLOR)
            self.label_icon_preview.grid(row=7, column=1, sticky="W")

        button_select_icon = tk.Button(self.root, text="Select", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.select_icon())
        button_select_icon.grid(row=7, column=3, padx=5, pady=2, sticky="EW")

        #create button
        button_create_gui_window = tk.Button(self.root, text="Create GUI Window", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.launch_designer)
        button_create_gui_window.grid(row=8, column=0, padx=5, pady=10, sticky="W")

    #actions
    def choose_color(self, element_type: str, attribute: str):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[element_type][attribute] = color
            self.example_widgets[element_type].config({attribute: color})

    def select_icon(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            icon = load_icon(file_path, (20, 20))
            if icon is not None:
                self.icon = icon
                self.label_icon_preview.config(image=self.icon)

    def launch_designer(self):
        width_str = self.entry_window_width.get()
        height_str = self.entry_window_height.get()

        if not width_str.isdigit() or not height_str.isdigit():
            messagebox.showerror("Input Error", "Enter an integer value for window width and height!")
            return

        title = self.entry_window_title.get()
        width = int(width_str)
        height = int(height_str)

        #hide setup window and launch Designer
        self.root.withdraw()
        Designer(self.root, title, width, height, self.colors, self.icon)