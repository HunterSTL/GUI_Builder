import os.path
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from model import ProjectDocument
from events import EventBus
from utility import screen_offset_to_center_window, CustomTitlebar, atomic_write_json
from Theme import USER_THEME, PROGRAM_THEME, CONSTANTS
from SetupWizard import SetupWizard
from Designer import Designer

class AppController:
    def __init__(
        self,
        root: tk.Tk
    ):
        """initialize the main application controller"""
        self.root = root
        self.program_theme = PROGRAM_THEME
        self.constants = CONSTANTS
        self.designer = None

        self.app_event_bus = EventBus() #owns project and application events and persists across multiple Designer instances
        self._register_event_handlers()

        self._user_theme = {            #prevents mutation
            key: value.copy()
            for key, value in USER_THEME.items()
        }

        self._save_path = None
        self._last_directory = None

        self._setup_wizard_window = None
        self._build_startup_ui()

    def _center_window(self):
        """center the startup window on the screen"""
        self.root.update_idletasks()
        x_offset, y_offset = screen_offset_to_center_window(
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
            self.root.winfo_width(),
            self.root.winfo_height()
        )
        self.root.geometry(f"+{x_offset}+{y_offset}")

    def _build_startup_ui(self):
        """build the startup UI with [New], [Open] and [Exit] buttons"""
        self.root.config(bg=self.program_theme["background"]["color"])
        self.root.wm_minsize(200, 100)

        titlebar = CustomTitlebar(
            parent=self.root,
            title="Tkinter GUI Builder – Startup",
            height=self.constants["titlebar_height"],
            bg_color=self.program_theme["titlebar"]["bg"],
            fg_color=self.program_theme["titlebar"]["fg"],
            icon_path=None,
            on_close=self.exit_app
        )
        titlebar.frame.pack(fill="x")

        button_open_project = tk.Button(
            self.root,
            text="Open project",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=self.open_project
        )
        button_open_project.pack()

        button_new_project = tk.Button(
            self.root,
            text="New project",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=self.new_project
        )
        button_new_project.pack()

        button_exit = tk.Button(
            self.root,
            text="Exit",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=self.exit_app
        )
        button_exit.pack()

        self._center_window()

    def _copy_user_theme(self):
        """return a copy of the user theme"""
        return {key: value.copy() for key, value in self._user_theme.items()}

    def _launch_designer_from_project_document(self, project_document):
        """destroy any existing Designer and launch a new one from a ProjectDocument"""
        if self.designer:
            self.designer.top.destroy()
            self.designer = None

        self.designer = Designer(
            parent=self.root,
            project_document=project_document,
            program_theme=self.program_theme,
            constants=self.constants,
            app_event_bus=self.app_event_bus
        )

    def _register_event_handlers(self):
        """subscribe handlers to project and app events"""
        self.app_event_bus.subscribe("project.new", self.new_project)
        self.app_event_bus.subscribe("project.open", self.open_project)
        self.app_event_bus.subscribe("project.save", self.save_project)
        self.app_event_bus.subscribe("project.save_as", self.save_project_as)
        self.app_event_bus.subscribe("app.exit", self.exit_app)

    def _handle_unsaved_changes(self) -> str:
        """prompt the user to save, discard or cancel if unsaved changes exist, returning PROCEED or CANCEL"""
        if not self.designer or not self.designer.app_state.is_dirty():
            return "PROCEED"        #no unsaved changes exist

        choice = messagebox.askyesnocancel(
            "Unsaved changes",
            "There are still unsaved changes.\nDo you want to save them?",
            parent=self.designer.top
        )

        if choice is None:          #user pressed cancel
            return "CANCEL"
        elif choice:                #user pressed save
            if self.save_project(): #save successful
                return "PROCEED"
            else:                   #save failed or aborted
                return "CANCEL"
        else:                       #user pressed discard
            return "PROCEED"

    def _dialog_parent(self):
        """return the designer window if open, otherwise the startup window, for use as a dialog parent"""
        return self.designer.top if self.designer else self.root

    def _cancel_new_project_creation(self) -> None:
        """cancel new project creation and restore the previous window"""
        self._setup_wizard_window.destroy()
        self._setup_wizard_window = None

        if self.designer:
            self.designer.top.deiconify()
        else:
            self.root.deiconify()

    def new_project(self):
        """start a new project using the SetupWizard, prompting for intent when unsaved changes exist"""
        if self._handle_unsaved_changes() == "CANCEL":
            return

        if self.designer:
            self.designer.top.withdraw()

        self.root.withdraw()
        self._save_path = None

        self._setup_wizard_window = tk.Toplevel(self.root)
        SetupWizard(
            root=self._setup_wizard_window,
            user_theme=self._copy_user_theme(),
            program_theme=self.program_theme,
            constants=self.constants,
            on_done_callback=self._launch_designer_from_project_document,
            exit_callback=self._cancel_new_project_creation
        )

    def open_project(self):
        """open an existing .tkui file and launch the Designer, prompting for intent when unsaved changes exist"""
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

            self.root.withdraw()
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

    def save_project(self) -> bool:
        """save the project to the last used .tkui file, returning True on success"""
        if not self.designer:
            messagebox.showerror(
                "Error",
                "No project is currently open.",
                parent=self._dialog_parent()
            )
            return False

        if not self._save_path:
            return self.save_project_as()

        try:
            project_data = self.designer.app_state.project.to_json()
            atomic_write_json(self._save_path, project_data)    #atomic prevents corruption on error
            self.designer.app_state.mark_clean()
        except Exception as e:
            messagebox.showerror(
                "File error",
                f"Could not save file:\n{self._save_path}\n\n{e}",
                parent=self._dialog_parent()
            )
            return False
        return True

    def save_project_as(self) -> bool:
        """prompt for a save location and save the project as a .tkui file, returning True on success"""
        if not self.designer:
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

        if not save_path:   #user pressed cancel
            return False

        try:
            project_data = self.designer.app_state.project.to_json()
            atomic_write_json(save_path, project_data)  #atomic prevents corruption on error
            self._save_path = save_path                 #only update save path after successful write
            self._last_directory = os.path.dirname(save_path)
            self.designer.app_state.mark_clean()
        except Exception as e:
            messagebox.showerror(
                "File error",
                f"Could not save file:\n{save_path}\n\n{e}",
                parent=self._dialog_parent()
            )
            return False
        return True

    def exit_app(self):
        """exit application, prompting for intent when unsaved changes exist"""
        if self._handle_unsaved_changes() == "CANCEL":
            return

        self.root.destroy()
