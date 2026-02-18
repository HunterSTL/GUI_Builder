import os
import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from _dataclasses import ProjectDocument, GridConfig
from Geometry import screen_offset_to_center_window
from UIComponents import load_icon, CustomTitlebar

class SetupWizard:
    def __init__(
        self,
        root: tk.Toplevel,
        user_theme: dict,
        program_theme: dict,
        constants: dict,
        on_done_callback,
        exit_callback
    ):
        self.root = root
        self.user_theme = user_theme
        self.program_theme = program_theme
        self.constants = constants
        self.on_done_callback = on_done_callback
        self.exit_callback = exit_callback

        self.icon = None
        self.icon_path = None
        self._win_x = None
        self._win_y = None
        self._drag_start_x = None
        self._drag_start_y = None

        #build setup UI
        self._build_setup_ui()

    #center window
    def _center_window(self):
        self.root.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
            self.root.winfo_width(),
            self.root.winfo_height()
        )
        self.root.geometry(f"+{x_offset}+{y_offset}")

    #build setup UI
    def _build_setup_ui(self):
        #set bg color
        self.root.config(bg=self.program_theme["background"]["color"])

        #create title car
        titlebar = CustomTitlebar(
            parent=self.root,
            title="Tkinter GUI Builder – Setup",
            height=self.constants["titlebar_height"],
            bg_color=self.program_theme["titlebar"]["bg"],
            fg_color=self.program_theme["titlebar"]["fg"],
            icon_path=os.path.join(os.path.dirname(__file__), "icon.ico"),
            on_close=self.exit_callback
        )
        titlebar.frame.grid(row=0, column=0, columnspan=5, sticky="EW")

        #window title
        label_window_title = tk.Label(self.root, text="Window Title:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_window_title.grid(row=1, column=0, padx=5, sticky="W")
        self.entry_window_title = tk.Entry(self.root, bg=self.program_theme["entry"]["bg"], fg=self.program_theme["entry"]["fg"])
        self.entry_window_title.grid(row=1, column=1, columnspan=3, pady=3, sticky="EW")

        #width / height
        label_window_width = tk.Label(self.root, text="Window Width:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_window_width.grid(row=2, column=0, padx=5, sticky="W")
        self.entry_window_width = tk.Entry(self.root, width=15, bg=self.program_theme["entry"]["bg"], fg=self.program_theme["entry"]["fg"])
        self.entry_window_width.insert(0, "800")
        self.entry_window_width.grid(row=2, column=1, pady=3, sticky="EW")

        label_window_height = tk.Label(self.root, text="Height:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_window_height.grid(row=2, column=2, padx=5, sticky="E")
        self.entry_window_height = tk.Entry(self.root, width=15, bg=self.program_theme["entry"]["bg"], fg=self.program_theme["entry"]["fg"])
        self.entry_window_height.insert(0, "600")
        self.entry_window_height.grid(row=2, column=3, pady=3, sticky="EW")

        #background color
        label_background_color = tk.Label(self.root, text="Background Color:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_background_color.grid(row=3, column=0, padx=5, sticky="W")
        self.label_example_background = tk.Label(self.root, bg=self.user_theme["background"]["color"])
        self.label_example_background.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")
        button_background_color = tk.Button(self.root, text="Select", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("background", "color"))
        button_background_color.grid(row=3, column=3, padx=5, pady=2, sticky="EW")

        #label colors
        label_label_color = tk.Label(self.root, text="Label Color:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_label_color.grid(row=4, column=0, padx=5, sticky="W")
        self.label_example_label = tk.Label(self.root, text="Example", bg=self.user_theme["label"]["bg"], fg=self.user_theme["label"]["fg"], anchor="w")
        self.label_example_label.grid(row=4, column=1, columnspan=2, padx=1, sticky="EW")
        button_label_background_color = tk.Button(self.root, text="Background", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("label", "bg"))
        button_label_background_color.grid(row=4, column=3, padx=5, pady=2, sticky="EW")
        button_label_text_color = tk.Button(self.root, text="Text", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("label", "fg"))
        button_label_text_color.grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        #entry colors
        label_entry_color = tk.Label(self.root, text="Entry Color:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_entry_color.grid(row=5, column=0, padx=5, sticky="W")
        self.entry_example_entry = tk.Entry(self.root, bg=self.user_theme["entry"]["bg"], fg=self.user_theme["entry"]["fg"])
        self.entry_example_entry.insert(0, "Example")
        self.entry_example_entry.grid(row=5, column=1, columnspan=2, sticky="EW")
        button_entry_background_color = tk.Button(self.root, text="Background", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("entry", "bg"))
        button_entry_background_color.grid(row=5, column=3, padx=5, pady=2, sticky="EW")
        button_entry_text_color = tk.Button(self.root, text="Text", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("entry", "fg"))
        button_entry_text_color.grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        #button colors
        label_button_color = tk.Label(self.root, text="Button Color:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_button_color.grid(row=6, column=0, padx=5, sticky="W")
        self.button_example_button_color = tk.Button(self.root, text="Example", bg=self.user_theme["button"]["bg"], fg=self.user_theme["button"]["fg"])
        self.button_example_button_color.grid(row=6, column=1, columnspan=2, sticky="EW")
        button_button_background_color = tk.Button(self.root, text="Background", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("button", "bg"))
        button_button_background_color.grid(row=6, column=3, padx=5, pady=2, sticky="EW")
        button_button_text_color = tk.Button(self.root, text="Text", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.choose_color("button", "fg"))
        button_button_text_color.grid(row=6, column=4, padx=5, pady=2, sticky="EW")

        #cache preview widgets
        self.example_widgets = {
            "background": self.label_example_background,
            "label": self.label_example_label,
            "entry": self.entry_example_entry,
            "button": self.button_example_button_color
        }

        #icon
        label_icon = tk.Label(self.root, text="Icon:", bg=self.program_theme["label"]["bg"], fg=self.program_theme["label"]["fg"])
        label_icon.grid(row=7, column=0, padx=5, sticky="W")

        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.icon = load_icon(self.icon_path, (20, 20))
        if self.icon:
            self.label_icon_preview = tk.Label(self.root, image=self.icon, bg=self.program_theme["label"]["bg"])
            self.label_icon_preview.grid(row=7, column=1, sticky="W")
        else:
            self.label_icon_preview = tk.Label(self.root, bg=self.program_theme["label"]["bg"])
            self.label_icon_preview.grid(row=7, column=1, sticky="W")

        button_select_icon = tk.Button(self.root, text="Select", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=lambda: self.select_icon())
        button_select_icon.grid(row=7, column=3, padx=5, pady=2, sticky="EW")

        #create button
        button_create_gui_window = tk.Button(self.root, text="Launch designer", bg=self.program_theme["button"]["bg"], fg=self.program_theme["button"]["fg"], command=self.build_project_document)
        button_create_gui_window.grid(row=8, column=0, padx=5, pady=5, sticky="W")

        self._center_window()

    #actions
    def choose_color(self, element_type: str, attribute: str):
        color = colorchooser.askcolor()[1]
        if not color:
            return

        #update user theme
        self.user_theme[element_type][attribute] = color

        #update the example widget
        example_widget = self.example_widgets[element_type]
        if element_type == "background" and attribute == "color":
            example_widget.config(bg=color)
        else:
            example_widget.config({attribute: color})

    def select_icon(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.ico")])

        if not file_path:
            return

        icon = load_icon(file_path, (20, 20))
        if icon:
            self.icon = icon
            self.icon_path = file_path
            self.label_icon_preview.config(image=self.icon)

    def build_project_document(self):
        width_str = self.entry_window_width.get()
        height_str = self.entry_window_height.get()

        if not width_str.isdigit() or not height_str.isdigit():
            messagebox.showerror("Input Error", "Enter an integer value for window width and height!")
            return

        minimum_canvas_width = self.constants["canvas"]["min_width"]
        minimum_canvas_height = self.constants["canvas"]["min_height"]
        maximum_canvas_width = self.constants["canvas"]["max_width"]
        maximum_canvas_height = self.constants["canvas"]["max_height"]
        width = int(width_str)
        height = int(height_str)

        if width < minimum_canvas_width or height < minimum_canvas_height:
            messagebox.showerror("Input Error", f"Minimum canvas size: {minimum_canvas_width} x {minimum_canvas_height} pixels!")
            return
        elif width > maximum_canvas_width or height > maximum_canvas_height:
            messagebox.showerror("Input Error", f"Maximum canvas size: {maximum_canvas_width} x {maximum_canvas_height} pixels!")
            return

        title = self.entry_window_title.get()

        project_document = ProjectDocument(
            version=1,
            title=title,
            width=width,
            height=height,
            icon_path=self.icon_path,
            grid=GridConfig(
                size=self.constants["grid_size"],
                color=self.program_theme["grid"]["color"],
                visible=False
            ),
            theme=self.user_theme,
            widget_models=[]
        )

        #hand the project_document back to the AppController
        if callable(self.on_done_callback):
            self.on_done_callback(project_document)

        #close wizard window
        self.root.destroy()