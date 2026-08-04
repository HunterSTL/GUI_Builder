import os
import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from collections.abc import Callable

from model import ProjectDocument, GridConfig, IdCounters
from utility import screen_offset_to_center_window, load_icon, CustomTitlebar, CONSTANTS

class SetupWizard:
    """Collects project settings and constructs a project document."""
    def __init__(
        self,
        parent: tk.Tk,
        user_theme: dict[str, dict[str, str]],
        program_theme: dict[str, dict[str, str]],
        on_done_callback: Callable[[ProjectDocument], None],
        on_cancel_callback: Callable[[], None]
    ) -> None:
        self._parent: tk.Tk = parent
        self._user_theme: dict[str, dict[str, str]] = user_theme
        self._program_theme: dict[str, dict[str, str]] = program_theme
        self._on_done_callback: Callable[[ProjectDocument], None] = on_done_callback
        self._on_cancel_callback: Callable[[], None] = on_cancel_callback

        self._icon: tk.PhotoImage | None = None
        self._icon_path: str | None = None
        self._top: tk.Toplevel = tk.Toplevel(self._parent)
        self._top.config(
            bg=self._program_theme["background"]["color"]
        )
        self._build_setup_ui()

    def close(
        self
    ) -> None:
        """Close the setup wizard window."""
        self._top.destroy()

    def _center_window(
        self
    ) -> None:
        """Center the setup wizard window on screen."""
        self._top.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self._top.winfo_screenwidth(),
            self._top.winfo_screenheight(),
            self._top.winfo_width(),
            self._top.winfo_height()
        )
        self._top.geometry(f"+{x_offset}+{y_offset}")

    def _build_setup_ui(
        self
    ) -> None:
        """Build the setup wizard UI."""
        titlebar = CustomTitlebar(
            parent=self._top,
            title="Tkinter GUI Builder – Setup",
            height=CONSTANTS["titlebar_height"],
            bg_color=self._program_theme["titlebar"]["bg"],
            fg_color=self._program_theme["titlebar"]["fg"],
            icon_path=os.path.join(os.path.dirname(__file__), "icon.ico"),
            on_close=self._on_cancel_callback
        )
        titlebar.frame.grid(row=0, column=0, columnspan=5, sticky="EW")

        label_window_title = tk.Label(
            self._top,
            text="Window Title:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_window_title.grid(row=1, column=0, padx=5, sticky="W")

        self._entry_window_title: tk.Entry = tk.Entry(
            self._top,
            bg=self._program_theme["entry"]["bg"],
            fg=self._program_theme["entry"]["fg"]
        )
        self._entry_window_title.grid(row=1, column=1, columnspan=3, pady=3, sticky="EW")

        label_window_width = tk.Label(
            self._top,
            text="Window Width:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_window_width.grid(row=2, column=0, padx=5, sticky="W")

        self._entry_window_width: tk.Entry = tk.Entry(
            self._top,
            width=15,
            bg=self._program_theme["entry"]["bg"],
            fg=self._program_theme["entry"]["fg"]
        )
        self._entry_window_width.insert(0, "800")
        self._entry_window_width.grid(row=2, column=1, pady=3, sticky="EW")

        label_window_height = tk.Label(
            self._top,
            text="Height:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_window_height.grid(row=2, column=2, padx=5, sticky="E")

        self._entry_window_height: tk.Entry = tk.Entry(
            self._top,
            width=15,
            bg=self._program_theme["entry"]["bg"],
            fg=self._program_theme["entry"]["fg"]
        )
        self._entry_window_height.insert(0, "600")
        self._entry_window_height.grid(row=2, column=3, pady=3, sticky="EW")

        label_background_color = tk.Label(
            self._top,
            text="Background Color:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_background_color.grid(row=3, column=0, padx=5, sticky="W")

        self._label_preview_background: tk.Label = tk.Label(
            self._top,
            bg=self._user_theme["background"]["color"]
        )
        self._label_preview_background.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")

        button_background_color = tk.Button(
            self._top,
            text="Select",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("background", "color")
        )
        button_background_color.grid(row=3, column=3, padx=5, pady=2, sticky="EW")

        label_label_color = tk.Label(
            self._top,
            text="Label Color:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_label_color.grid(row=4, column=0, padx=5, sticky="W")

        self._label_preview_label: tk.Label = tk.Label(
            self._top,
            text="Preview",
            bg=self._user_theme["label"]["bg"],
            fg=self._user_theme["label"]["fg"],
            anchor="w"
        )
        self._label_preview_label.grid(row=4, column=1, columnspan=2, padx=1, sticky="EW")

        button_label_background_color = tk.Button(
            self._top,
            text="Background",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("label", "bg")
        )
        button_label_background_color.grid(row=4, column=3, padx=5, pady=2, sticky="EW")

        button_label_text_color = tk.Button(
            self._top,
            text="Text",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("label", "fg")
        )
        button_label_text_color.grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        label_entry_color = tk.Label(
            self._top,
            text="Entry Color:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_entry_color.grid(row=5, column=0, padx=5, sticky="W")

        self._entry_preview_entry: tk.Entry = tk.Entry(
            self._top,
            bg=self._user_theme["entry"]["bg"],
            fg=self._user_theme["entry"]["fg"]
        )
        self._entry_preview_entry.insert(0, "Example")
        self._entry_preview_entry.grid(row=5, column=1, columnspan=2, sticky="EW")

        button_entry_background_color = tk.Button(
            self._top,
            text="Background",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("entry", "bg")
        )
        button_entry_background_color.grid(row=5, column=3, padx=5, pady=2, sticky="EW")

        button_entry_text_color = tk.Button(
            self._top,
            text="Text",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("entry", "fg")
        )
        button_entry_text_color.grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        label_button_color = tk.Label(
            self._top,
            text="Button Color:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_button_color.grid(row=6, column=0, padx=5, sticky="W")

        self._button_preview_button_color: tk.Button = tk.Button(
            self._top,
            text="Preview",
            bg=self._user_theme["button"]["bg"],
            fg=self._user_theme["button"]["fg"]
        )
        self._button_preview_button_color.grid(row=6, column=1, columnspan=2, sticky="EW")

        button_button_background_color = tk.Button(
            self._top,
            text="Background",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("button", "bg")
        )
        button_button_background_color.grid(row=6, column=3, padx=5, pady=2, sticky="EW")

        button_button_text_color = tk.Button(
            self._top,
            text="Text",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=lambda: self._choose_color("button", "fg")
        )
        button_button_text_color.grid(row=6, column=4, padx=5, pady=2, sticky="EW")

        self._preview_widgets: dict[str, tk.Label | tk.Entry | tk.Button] = {
            "background": self._label_preview_background,
            "label": self._label_preview_label,
            "entry": self._entry_preview_entry,
            "button": self._button_preview_button_color
        }

        label_icon = tk.Label(
            self._top,
            text="Icon:",
            bg=self._program_theme["label"]["bg"],
            fg=self._program_theme["label"]["fg"]
        )
        label_icon.grid(row=7, column=0, padx=5, sticky="W")

        self._icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self._icon = load_icon(
            path=self._icon_path,
            size=(20, 20),
            parent=self._top
        )

        self._label_icon_preview: tk.Label = tk.Label(
            self._top,
            image=self._icon if self._icon else "",
            bg=self._program_theme["label"]["bg"]
        )
        self._label_icon_preview.grid(row=7, column=1, sticky="W")

        button_select_icon = tk.Button(
            self._top,
            text="Select",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=self._select_icon
        )
        button_select_icon.grid(row=7, column=3, padx=5, pady=2, sticky="EW")

        button_create_gui_window = tk.Button(
            self._top,
            text="Launch designer",
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=self._build_project_document
        )
        button_create_gui_window.grid(row=8, column=0, padx=5, pady=5, sticky="W")

        self._center_window()

    def _choose_color(
        self,
        element_type: str,
        attribute: str
    ) -> None:
        """Update a theme color and its preview widget."""
        color = colorchooser.askcolor(parent=self._top)[1]
        if not color:
            return

        self._user_theme[element_type][attribute] = color

        preview_widget = self._preview_widgets[element_type]
        if element_type == "background" and attribute == "color":
            preview_widget.config(bg=color)
        else:
            preview_widget.config({attribute: color})

    def _select_icon(
        self
    ) -> None:
        """Select and preview the project icon."""
        file_path = filedialog.askopenfilename(
            parent=self._top,
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.ico")]
        )

        if not file_path:
            return

        icon = load_icon(
            path=file_path,
            size=(20, 20),
            parent=self._top
        )
        if icon:
            self._icon = icon
            self._icon_path = file_path
            self._label_icon_preview.config(image=self._icon)

    def _build_project_document(
        self
    ) -> None:
        """Validate the project settings and construct a project document."""
        width_input = self._entry_window_width.get()
        height_input = self._entry_window_height.get()

        if not width_input.isdigit() or not height_input.isdigit():
            messagebox.showerror(
                "Input Error",
                "Enter an integer value for window width and height!",
                parent=self._top
            )
            return

        minimum_canvas_width = CONSTANTS["canvas"]["min_width"]
        minimum_canvas_height = CONSTANTS["canvas"]["min_height"]
        maximum_canvas_width = CONSTANTS["canvas"]["max_width"]
        maximum_canvas_height = CONSTANTS["canvas"]["max_height"]
        width = int(width_input)
        height = int(height_input)

        if width < minimum_canvas_width or height < minimum_canvas_height:
            messagebox.showerror(
                "Input Error",
                f"Minimum canvas size: {minimum_canvas_width} x {minimum_canvas_height} pixels!",
                parent=self._top
            )
            return
        elif width > maximum_canvas_width or height > maximum_canvas_height:
            messagebox.showerror(
                "Input Error",
                f"Maximum canvas size: {maximum_canvas_width} x {maximum_canvas_height} pixels!",
                parent=self._top
            )
            return

        title = self._entry_window_title.get()

        project_document = ProjectDocument(
            version=1,
            title=title,
            width=width,
            height=height,
            icon_path=self._icon_path,
            grid=GridConfig(
                size=CONSTANTS["grid_size"],
                color=self._program_theme["grid"]["color"],
                visible=False
            ),
            theme=self._user_theme,
            widget_models=[],
            id_counters=IdCounters()
        )

        self.close()
        self._on_done_callback(project_document)
