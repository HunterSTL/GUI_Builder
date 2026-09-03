import json
import os.path
import tkinter as tk
from tkinter import messagebox, filedialog

from events import EventBus
from model import ProjectDocument
from utility import force_dark_title_bar, set_title_bar_icon, set_minimum_window_size_from_ui, center_window, atomic_write_json
from utility.AppTheme import WINDOW_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR

from Designer import Designer
from SetupWizard import SetupWizard


class AppController:
    """Manages application startup and exit, project files and Designer instances."""
    def __init__(
        self,
        root: tk.Tk
    ) -> None:
        self._root: tk.Tk = root

        self._app_event_bus: EventBus = EventBus()      #persists across Designer instances
        self._register_event_handlers()

        self._save_path: str | None = None
        self._last_directory: str | None = None
        self._designer: Designer | None = None
        self._setup_wizard: SetupWizard | None = None

        self._build_startup_ui()

        self._root.title("Startup")
        self._root.config(bg=WINDOW_COLOR)
        self._root.wm_protocol("WM_DELETE_WINDOW", self._exit_app)

        force_dark_title_bar(window=self._root)
        set_title_bar_icon(window=self._root, path="icon.ico")
        set_minimum_window_size_from_ui(window=self._root, padding=50)
        center_window(window=self._root)

        self._root.deiconify()

    def _build_startup_ui(
        self
    ) -> None:
        """Build the startup UI with [New], [Open] and [Exit] buttons."""
        centered_frame = tk.Frame(
            master=self._root,
            bg=WINDOW_COLOR
        )
        centered_frame.grid(row=0, column=0)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        button_open_project = tk.Button(
            centered_frame,
            text="Open project",
            width=30,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=self._open_project
        )
        button_open_project.pack()

        button_new_project = tk.Button(
            centered_frame,
            text="New project",
            width=30,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=self._new_project
        )
        button_new_project.pack(pady=10)

        button_exit = tk.Button(
            centered_frame,
            text="Exit",
            width=30,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            command=self._exit_app
        )
        button_exit.pack()

    def _launch_designer_from_project_document(
        self,
        project_document: ProjectDocument
    ) -> None:
        """Destroy any existing Designer and launch a new one from a ProjectDocument."""
        if self._designer:
            self._designer.top.destroy()
            self._designer = None

        self._designer = Designer(
            parent=self._root,
            project_document=project_document,
            app_event_bus=self._app_event_bus
        )

    def _register_event_handlers(
        self
    ) -> None:
        """Subscribe handlers to project and app events."""
        self._app_event_bus.subscribe("project.new", self._new_project)
        self._app_event_bus.subscribe("project.open", self._open_project)
        self._app_event_bus.subscribe("project.save", self._save_project)
        self._app_event_bus.subscribe("project.save_as", self._save_project_as)
        self._app_event_bus.subscribe("app.exit", self._exit_app)

    def _handle_unsaved_changes(
        self
    ) -> str:
        """Prompt for unsaved changes and return whether the pending operation may proceed."""
        if not self._designer or not self._designer.app_state.is_dirty():
            return "PROCEED"

        choice = messagebox.askyesnocancel(
            "Unsaved changes",
            "There are still unsaved changes.\nDo you want to save them?",
            parent=self._designer.top
        )

        if choice is None:
            return "CANCEL"

        if choice and not self._save_project():
            return "CANCEL"

        return "PROCEED"

    def _dialog_parent(
        self
    ) -> tk.Tk | tk.Toplevel:
        """Return the active window to use as the parent of a dialog."""
        return self._designer.top if self._designer else self._root

    def _cancel_new_project_creation(
        self
    ) -> None:
        """Cancel new project creation and restore the previous window."""
        if self._setup_wizard is None:
            return

        self._setup_wizard.close()
        self._setup_wizard = None

        if self._designer:
            self._designer.top.deiconify()
        else:
            self._root.deiconify()

    def _new_project(
        self
    ) -> None:
        """Create a new project using the SetupWizard, prompting for unsaved changes."""
        if self._handle_unsaved_changes() == "CANCEL":
            return

        if self._designer:
            self._designer.top.withdraw()

        self._root.withdraw()
        self._save_path = None

        self._setup_wizard = SetupWizard(
            parent=self._root,
            on_done_callback=self._launch_designer_from_project_document,
            on_cancel_callback=self._cancel_new_project_creation
        )

    def _open_project(
        self
    ) -> None:
        """Open a .tkui file and launch the Designer, prompting for unsaved changes."""
        if self._handle_unsaved_changes() == "CANCEL":
            return

        file_path = filedialog.askopenfilename(
            parent=self._dialog_parent(),
            filetypes=[("Tk user interface file", "*.tkui")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_contents = json.load(file)

            project_document = ProjectDocument.from_json(file_contents)

            self._root.withdraw()
            self._save_path = file_path
            self._last_directory = os.path.dirname(file_path)
            self._launch_designer_from_project_document(project_document)
        except (ValueError, json.JSONDecodeError) as e:
            messagebox.showerror(
                "File error",
                f"Invalid or corrupted file:\n{e}",
                parent=self._dialog_parent()
            )
        except OSError as e:
            messagebox.showerror(
                "File error",
                f"Could not read file:\n{e}",
                parent=self._dialog_parent()
            )

    def _save_project(
        self
    ) -> bool:
        """Save the project to the last used .tkui file, returning True on success."""
        if not self._designer:
            messagebox.showerror(
                "Error",
                "No project is currently open.",
                parent=self._dialog_parent()
            )
            return False

        if not self._save_path:
            return self._save_project_as()

        try:
            project_data = self._designer.app_state.project.to_json()
            atomic_write_json(self._save_path, project_data)    #prevents file corruption if writing fails
            self._designer.app_state.mark_clean()
        except Exception as e:
            messagebox.showerror(
                "File error",
                f"Could not save file:\n{self._save_path}\n\n{e}",
                parent=self._dialog_parent()
            )
            return False
        return True

    def _save_project_as(
        self
    ) -> bool:
        """Prompt for a save location and save the project as a .tkui file, returning True on success."""
        if not self._designer:
            messagebox.showerror(
                "Error",
                "No project is currently open.",
                parent=self._dialog_parent()
            )
            return False

        save_path = filedialog.asksaveasfilename(
            parent=self._dialog_parent(),
            title="Save as",
            filetypes=[("Tk user interface file", "*.tkui")],
            defaultextension=".tkui",
            initialdir=self._last_directory
        )

        if not save_path:
            return False

        try:
            project_data = self._designer.app_state.project.to_json()
            atomic_write_json(save_path, project_data)  #prevents file corruption if writing fails
            self._save_path = save_path                 #only updates save path after successful write
            self._last_directory = os.path.dirname(save_path)
            self._designer.app_state.mark_clean()
        except Exception as e:
            messagebox.showerror(
                "File error",
                f"Could not save file:\n{save_path}\n\n{e}",
                parent=self._dialog_parent()
            )
            return False
        return True

    def _exit_app(
        self
    ) -> None:
        """Exit the application, prompting for unsaved changes."""
        if self._handle_unsaved_changes() == "CANCEL":
            return

        self._root.destroy()
