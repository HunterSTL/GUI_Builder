import os.path
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from model import ProjectDocument
from utility import screen_offset_to_center_window, CustomTitlebar
from Theme import USER_THEME, PROGRAM_THEME, CONSTANTS
from SetupWizard import SetupWizard
from Designer import Designer
from EventBus import EventBus

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

        #EventBus: functions subscribe to an event (e.g. function Designer._move() subscribes to the event "widget.move")
        self.event_bus = EventBus()
        self._subscribe_functions_to_events()

        #copy user theme from Theme.py to prevent mutation
        self._user_theme = {key: value.copy() for key, value in USER_THEME.items()}

        #app state
        self._save_path = None
        self._last_directory = None
        self._win_x = None
        self._win_y = None
        self._drag_start_x = None
        self._drag_start_y = None

        #build startup UI
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
        """build the startup UI with New/Open/Exit actions"""
        #set bg color and enforce minimum window size
        self.root.config(bg=self.program_theme["background"]["color"])
        self.root.wm_minsize(200, 100)

        #create title bar
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

        #open project button
        button_open_project = tk.Button(
            self.root,
            text="Open project",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=self.open_project
        )
        button_open_project.pack()

        #new project button
        button_new_project = tk.Button(
            self.root,
            text="New project",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=self.new_project
        )
        button_new_project.pack()

        #exit button
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

    def _fresh_user_theme(self):
        """return a shallow copy of the user theme"""
        return {key: value.copy() for key, value in self._user_theme.items()}

    def _launch_designer_from_project_document(self, project_document):
        """destroy any existing Designer and launch a new one from a ProjectDocument"""
        #destroy old designer
        if self.designer:
            self.designer.top.destroy()
            self.designer = None

        #launch new designer
        self.designer = Designer(
            parent=self.root,
            project_document=project_document,
            program_theme=self.program_theme,
            constants=self.constants,
            event_bus=self.event_bus
        )

    def _subscribe_functions_to_events(self):
        """subscribe all functions, that should be called when an event is emitted, to the corresponding event"""
        #project events
        self.event_bus.subscribe("project.new", self.new_project)
        self.event_bus.subscribe("project.open", self.open_project)
        self.event_bus.subscribe("project.save", self.save_project)
        self.event_bus.subscribe("project.save_as", self.save_project_as)

        #app events
        self.event_bus.subscribe("app.exit", self.exit_app)

    def prompt_unsaved_changes(self):
        """prompt the user when unsaved changes exist and return SAVE / DISCARD / CANCEL"""
        if not self.designer or not self.designer.is_dirty():
            return "DISCARD"

        choice = messagebox.askyesnocancel("Unsaved changes", "There are still unsaved changes.\nDo you want to save them?")
        if choice is None:
            return "CANCEL"

        if choice:
            return "SAVE"
        else:
            return "DISCARD"

    def new_project(self):
        """start a new project using the SetupWizard, prompting for unsaved changes if needed"""
        #prompt user intent
        user_intent = self.prompt_unsaved_changes()

        if user_intent == "CANCEL":
            return

        if user_intent == "SAVE":
            self.save_project()

        #destroy existing designer window
        if self.designer:
            self.designer.top.destroy()
            self.designer = None

        #hide startup window
        self.root.withdraw()

        #create the setup wizard as a child
        setup_window = tk.Toplevel(self.root)
        SetupWizard(
            root=setup_window,
            user_theme=self._fresh_user_theme(),
            program_theme=self.program_theme,
            constants=self.constants,
            on_done_callback=self._launch_designer_from_project_document,
            exit_callback=self.exit_app
        )

    def open_project(self):
        """open an existing .tkui project file and launch the Designer, prompting for unsaved changes if needed"""
        #prompt user intent
        user_intent = self.prompt_unsaved_changes()

        if user_intent == "CANCEL":
            return

        if user_intent == "SAVE":
            self.save_project()

        #let user choose .tkui file
        file_path = filedialog.askopenfilename(filetypes=[("Tk user interface file", "*.tkui")])

        if not file_path:
            return

        #read file contents
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = json.load(file)

        #build a ProjectDocument from file_contents
        project_document = ProjectDocument.from_json(file_contents)

        #hide startup window
        self.root.withdraw()

        #let AppController keep track of save path and last directory
        self._save_path = file_path
        self._last_directory = os.path.dirname(self._save_path)

        #launch designer
        self._launch_designer_from_project_document(project_document)

    def save_project(self):
        """save the current project to the last used file path"""
        #use save_project_as() if save path is empty
        if not self._save_path:
            self.save_project_as()
            return

        #open .tkui file in write mode and write project_document json
        with open(self._save_path, "w", encoding="utf-8") as file:
            json.dump(self.designer.app_state.project.to_json(), file, ensure_ascii=False, indent=2)

        #set app state to clean
        self.designer.set_clean()

    def save_project_as(self):
        """prompt for a save location and save the project as a .tkui file"""
        #create .tkui file
        file = filedialog.asksaveasfile(
            title="Save as",
            mode="w",
            filetypes=[("Tk user interface file", "*.tkui")],
            defaultextension=".tkui",
            initialdir=self._last_directory
        )

        #abort if user pressed cancel
        if file is None:
            return

        #open .tkui file in write mode and write project_document json
        with open(file.name, "w", encoding="utf-8") as file:
            json.dump(self.designer.app_state.project.to_json(), file, ensure_ascii=False, indent=2)

        #let AppController keep track of save path and last directory
        self._save_path = file.name
        self._last_directory = os.path.dirname(self._save_path)

        #set app state to clean
        self.designer.set_clean()

    def exit_app(self):
        """exit application, prompting for unsaved changes if needed"""
        #prompt user intent
        user_intent = self.prompt_unsaved_changes()

        if user_intent == "CANCEL":
            return

        if user_intent == "SAVE":
            self.save_project()

        #destroy startup window
        self.root.destroy()