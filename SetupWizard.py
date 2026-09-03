import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from collections.abc import Callable

from model import ProjectDocument, GridConfig, IdCounters, ProjectTheme
from utility import load_icon, force_dark_title_bar, set_title_bar_icon, set_minimum_window_size_from_ui, center_window
from utility.AppTheme import WINDOW_COLOR, LABEL_COLOR, LABEL_TEXT_COLOR, ENTRY_COLOR, ENTRY_TEXT_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR
from utility.Constants import CANVAS_MIN_WIDTH, CANVAS_MIN_HEIGHT, CANVAS_MAX_WIDTH, CANVAS_MAX_HEIGHT


class SetupWizard:
    """Collects project settings and constructs a project document."""
    def __init__(
        self,
        parent: tk.Tk,
        on_done_callback: Callable[[ProjectDocument], None],
        on_cancel_callback: Callable[[], None]
    ) -> None:
        self._on_done_callback: Callable[[ProjectDocument], None] = on_done_callback
        self._on_cancel_callback: Callable[[], None] = on_cancel_callback

        self._project_theme: ProjectTheme = ProjectTheme()

        self._icon: tk.PhotoImage | None = None
        self._icon_path: str = "icon.ico"

        self._top: tk.Toplevel = tk.Toplevel(parent)
        self._top.withdraw()    #prevents flashing from applying the dark title bar by starting out withdrawn

        self._build_setup_ui()

        self._top.title("Setup")
        self._top.config(bg=WINDOW_COLOR)
        self._top.wm_protocol("WM_DELETE_WINDOW", self._on_cancel_callback)

        force_dark_title_bar(window=self._top)
        set_minimum_window_size_from_ui(window=self._top, padding=50)
        set_title_bar_icon(window=self._top, path="icon.ico")
        center_window(window=self._top)

        self._top.deiconify()

    def close(
        self
    ) -> None:
        """Close the setup wizard window."""
        self._top.destroy()

    def _build_setup_ui(
        self
    ) -> None:
        """Build the setup wizard UI."""
        centered_frame = tk.Frame(
            master=self._top,
            bg=WINDOW_COLOR
        )
        centered_frame.grid(row=0, column=0)
        self._top.columnconfigure(0, weight=1)
        self._top.rowconfigure(0, weight=1)

        label_window_title = tk.Label(
            centered_frame,
            text="Window Title:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_window_title.grid(row=0, column=0, padx=5, sticky="W")

        self._entry_window_title: tk.Entry = tk.Entry(
            centered_frame,
            bg=ENTRY_COLOR,
            fg=ENTRY_TEXT_COLOR
        )
        self._entry_window_title.grid(row=0, column=1, columnspan=3, pady=3, sticky="EW")

        label_window_width = tk.Label(
            centered_frame,
            text="Window Width:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_window_width.grid(row=1, column=0, padx=5, sticky="W")

        self._entry_window_width: tk.Entry = tk.Entry(
            centered_frame,
            width=15,
            bg=ENTRY_COLOR,
            fg=ENTRY_TEXT_COLOR
        )
        self._entry_window_width.insert(0, "800")
        self._entry_window_width.grid(row=1, column=1, pady=3, sticky="EW")

        label_window_height = tk.Label(
            centered_frame,
            text="Height:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_window_height.grid(row=1, column=2, padx=5, sticky="E")

        self._entry_window_height: tk.Entry = tk.Entry(
            centered_frame,
            width=15,
            bg=ENTRY_COLOR,
            fg=ENTRY_TEXT_COLOR
        )
        self._entry_window_height.insert(0, "600")
        self._entry_window_height.grid(row=1, column=3, pady=3, sticky="EW")

        label_background_color = tk.Label(
            centered_frame,
            text="Background Color:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_background_color.grid(row=2, column=0, padx=5, sticky="W")

        self._label_preview_background: tk.Label = tk.Label(
            centered_frame,
            bg=self._project_theme.background_color
        )
        self._label_preview_background.grid(row=2, column=1, columnspan=2, padx=1, sticky="EW")

        button_background_color = tk.Button(
            centered_frame,
            text="Select",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="background_color",
                preview_widget=self._label_preview_background,
                preview_option="bg"
            )
        )
        button_background_color.grid(row=2, column=3, padx=5, pady=2, sticky="EW")

        label_label_color = tk.Label(
            centered_frame,
            text="Label Color:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_label_color.grid(row=3, column=0, padx=5, sticky="W")

        self._label_preview_label: tk.Label = tk.Label(
            centered_frame,
            text="Preview",
            bg=self._project_theme.label_color,
            fg=self._project_theme.label_text_color,
            anchor="w"
        )
        self._label_preview_label.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")

        button_label_background_color = tk.Button(
            centered_frame,
            text="Background",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="label_color",
                preview_widget=self._label_preview_label,
                preview_option="bg"
            )
        )
        button_label_background_color.grid(row=3, column=3, padx=5, pady=2, sticky="EW")

        button_label_text_color = tk.Button(
            centered_frame,
            text="Text",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="label_text_color",
                preview_widget=self._label_preview_label,
                preview_option="fg"
            )
        )
        button_label_text_color.grid(row=3, column=4, padx=5, pady=2, sticky="EW")

        label_entry_color = tk.Label(
            centered_frame,
            text="Entry Color:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_entry_color.grid(row=4, column=0, padx=5, sticky="W")

        self._entry_preview_entry: tk.Entry = tk.Entry(
            centered_frame,
            bg=self._project_theme.entry_color,
            fg=self._project_theme.entry_text_color
        )
        self._entry_preview_entry.insert(0, "Example")
        self._entry_preview_entry.grid(row=4, column=1, columnspan=2, sticky="EW")

        button_entry_background_color = tk.Button(
            centered_frame,
            text="Background",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="entry_color",
                preview_widget=self._entry_preview_entry,
                preview_option="bg"
            )
        )
        button_entry_background_color.grid(row=4, column=3, padx=5, pady=2, sticky="EW")

        button_entry_text_color = tk.Button(
            centered_frame,
            text="Text",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="entry_text_color",
                preview_widget=self._entry_preview_entry,
                preview_option="fg"
            )
        )
        button_entry_text_color.grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        label_button_color = tk.Label(
            centered_frame,
            text="Button Color:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_button_color.grid(row=5, column=0, padx=5, sticky="W")

        self._button_preview_button_color: tk.Button = tk.Button(
            centered_frame,
            text="Preview",
            bg=self._project_theme.button_color,
            fg=self._project_theme.button_text_color
        )
        self._button_preview_button_color.grid(row=5, column=1, columnspan=2, sticky="EW")

        button_button_background_color = tk.Button(
            centered_frame,
            text="Background",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="button_color",
                preview_widget=self._button_preview_button_color,
                preview_option="bg"
            )
        )
        button_button_background_color.grid(row=5, column=3, padx=5, pady=2, sticky="EW")

        button_button_text_color = tk.Button(
            centered_frame,
            text="Text",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=lambda: self._choose_color(
                theme_attribute="button_text_color",
                preview_widget=self._button_preview_button_color,
                preview_option="fg"
            )
        )
        button_button_text_color.grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        label_icon = tk.Label(
            centered_frame,
            text="Icon:",
            bg=LABEL_COLOR,
            fg=LABEL_TEXT_COLOR
        )
        label_icon.grid(row=6, column=0, padx=5, sticky="W")

        self._icon = load_icon(
            path=self._icon_path,
            size=(20, 20)
        )

        self._label_icon_preview: tk.Label = tk.Label(
            centered_frame,
            image=self._icon if self._icon else "",
            bg=LABEL_COLOR
        )
        self._label_icon_preview.grid(row=6, column=1, sticky="W")

        button_select_icon = tk.Button(
            centered_frame,
            text="Select",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=self._select_icon
        )
        button_select_icon.grid(row=6, column=3, padx=5, pady=2, sticky="EW")

        button_create_gui_window = tk.Button(
            centered_frame,
            text="Launch designer",
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=self._build_project_document
        )
        button_create_gui_window.grid(row=7, column=0, padx=5, pady=5, sticky="W")

    def _choose_color(
        self,
        theme_attribute: str,
        preview_widget: tk.Label | tk.Entry | tk.Button,
        preview_option: str
    ) -> None:
        """Update a theme color and its preview widget."""
        color = colorchooser.askcolor(parent=self._top)[1]
        if not color:
            return

        setattr(self._project_theme, theme_attribute, color)
        preview_widget.config({preview_option: color})

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
            size=(20, 20)
        )

        if not icon:
            return

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

        width = int(width_input)
        height = int(height_input)

        if width < CANVAS_MIN_WIDTH or height < CANVAS_MIN_HEIGHT:
            messagebox.showerror(
                "Input Error",
                f"Minimum canvas size: {CANVAS_MIN_WIDTH} x {CANVAS_MIN_HEIGHT} pixels!",
                parent=self._top
            )
            return
        elif width > CANVAS_MAX_WIDTH or height > CANVAS_MAX_HEIGHT:
            messagebox.showerror(
                "Input Error",
                f"Maximum canvas size: {CANVAS_MAX_WIDTH} x {CANVAS_MAX_HEIGHT} pixels!",
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
            grid=GridConfig(),
            theme=self._project_theme,
            widgets=[],
            id_counters=IdCounters()
        )

        self.close()
        self._on_done_callback(project_document)
