import json
import os.path
import tkinter as tk
from tkinter import messagebox, filedialog

from events import EventBus
from model import ProjectDocument
from utility import screen_offset_to_center_window, CustomTitlebar, atomic_write_json, CONSTANTS

from Designer import Designer
from SetupWizard import SetupWizard
from Theme import USER_THEME, PROGRAM_THEME


class AppController:
    """Manages application startup and exit, project files and Designer instances."""
    def __init__(
        self,
        root: tk.Tk
    ) -> None:
        self._root: tk.Tk = root

        self._program_theme: dict[str, dict[str, str]] = PROGRAM_THEME
        self._user_theme: dict[str, dict[str, str]] = { #prevents mutation of the global theme
            key: value.copy()
            for key, value in USER_THEME.items()
        }

        self._app_event_bus: EventBus = EventBus()      #persists across Designer instances
        self._register_event_handlers()

        self._save_path: str | None = None
        self._last_directory: str | None = None
        self._designer: Designer | None = None
        self._setup_wizard: SetupWizard | None = None

        self._build_startup_ui()

    def _center_window(
        self
    ) -> None:
        """Center the startup window on the screen."""
        self._root.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self._root.winfo_screenwidth(),
            self._root.winfo_screenheight(),
            self._root.winfo_width(),
            self._root.winfo_height()
        )
        self._root.geometry(f"+{x_offset}+{y_offset}")

    def _build_startup_ui(
        self
    ) -> None:
        """Build the startup UI with [New], [Open] and [Exit] buttons."""
        self._root.config(bg=self._program_theme["background"]["color"])
        self._root.wm_minsize(200, 100)

        titlebar = CustomTitlebar(
            parent=self._root,
            title="Tkinter GUI Builder – Startup",
            height=CONSTANTS["titlebar_height"],
            bg_color=self._program_theme["titlebar"]["bg"],
            fg_color=self._program_theme["titlebar"]["fg"],
            icon_path=None,
            on_close=self._exit_app
        )
        titlebar.frame.pack(fill="x")

        button_open_project = tk.Button(
            self._root,
            text="Open project",
            width=10,
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=self._open_project
        )
        button_open_project.pack()

        button_new_project = tk.Button(
            self._root,
            text="New project",
            width=10,
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=self._new_project
        )
        button_new_project.pack()

        button_exit = tk.Button(
            self._root,
            text="Exit",
            width=10,
            bg=self._program_theme["button"]["bg"],
            fg=self._program_theme["button"]["fg"],
            command=self._exit_app
        )
        button_exit.pack()

        self._center_window()

    def _copy_user_theme(
        self
    ) -> dict[str, dict[str, str]]:
        """Return a copy of the user theme and its nested mappings."""
        return {key: value.copy() for key, value in self._user_theme.items()}

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
            program_theme=self._program_theme,
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
            user_theme=self._copy_user_theme(),
            program_theme=self._program_theme,
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
