import os.path
import tkinter as tk
import json
from ProjectDocument import ProjectDocument
from tkinter import messagebox, filedialog
from Theme import USER_THEME, PROGRAM_THEME, CONSTANTS
from SetupWizard import SetupWizard
from Designer import Designer

class AppController:
    def __init__(
        self,
        root: tk.Tk
    ):
        self.root = root
        self.program_theme = PROGRAM_THEME
        self.constants = CONSTANTS
        self.designer = None

        #copy user theme from Theme.py to prevent mutation
        self._user_theme = {key: value.copy() for key, value in USER_THEME.items()}

        #app state
        self._save_path = None
        self._last_directory = None
        self._win_x = None
        self._win_y = None
        self._drag_start_x = None
        self._drag_start_y = None

        #set title and bg color
        self.root.config(bg=self.program_theme["background"]["color"])
        self.root.title("Tkinter GUI Builder – Startup")

        #build startup UI
        self._create_title_bar()
        self._build_startup_ui()

    #creates a custom draggable title bar with a close button
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
        title_bar = tk.Frame(self.root, bg=self.program_theme["titlebar"]["bg"])
        title_bar.pack()
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        #add title
        title_label = tk.Label(title_bar, text="Tkinter GUI Builder – Startup", bg=self.program_theme["titlebar"]["bg"], fg=self.program_theme["titlebar"]["fg"])
        title_label.pack(side="left")
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<B1-Motion>", do_move)

        #add close button
        close_button = tk.Button(
            title_bar,
            text=" X ",
            bg=self.program_theme["titlebar"]["bg"],
            fg=self.program_theme["titlebar"]["fg"],
            relief="flat",
            command=self.exit_app
        )
        close_button.pack(side="right")

    #builds the startup UI with New/Open/Exit actions
    def _build_startup_ui(self):
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

    #returns a dict of project callbacks
    def _project_callbacks(self):
        return {
            "new": self.new_project,
            "open": self.open_project,
            "save": self.save_project,
            "save_as": self.save_project_as,
            "export_json": self.export_json,
            "exit_app": self.exit_app
        }

    #return a shallow copy of the user them; works fine for dicts with 1 level (currently)
    def _fresh_user_theme(self):
        return {key: value.copy() for key, value in self._user_theme.items()}

    #destroys any existing Designer and launches a new one from a ProjectDocument
    def _launch_designer_from_project_document(self, project_document, icon):
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
            icon=icon,
            project_callbacks=self._project_callbacks()
        )

    #prompts to handle unsaved changes
    def prompt_unsaved_changes(self):
        if not self.designer or not self.designer.is_dirty():
            return "DISCARD"

        choice = messagebox.askyesnocancel("Unsaved changes", "There are still unsaved changes.\nDo you want to save them?")
        if choice is None:
            return "CANCEL"

        if choice:
            return "SAVE"
        else:
            return "DISCARD"

    #starts a new project by opening the SetupWizard for theme configuration
    def new_project(self):
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

    #opens a .tkui file and launches Designer with its ProjectDocument
    def open_project(self):
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
        self._launch_designer_from_project_document(project_document, None)

    #saves the current ProjectDocument to the last used path
    def save_project(self):
        #use save_project_as() if save path is empty
        if not self._save_path:
            self.save_project_as()
            return

        #open .tkui file in write mode and write project_document json
        with open(self._save_path, "w", encoding="utf-8") as file:
            json.dump(self.designer.project_document.to_json(), file, ensure_ascii=False, indent=2)

        #set app state to clean
        self.designer.set_clean()

    #prompts user for a path and saves the current ProjectDocument as a .tkui file
    def save_project_as(self):
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
            json.dump(self.designer.project_document.to_json(), file, ensure_ascii=False, indent=2)

        #let AppController keep track of save path and last directory
        self._save_path = file.name
        self._last_directory = os.path.dirname(self._save_path)

        #set app state to clean
        self.designer.set_clean()

    #placeholder
    def export_json(self):
        print("export_json")

    #exits the app
    def exit_app(self):
        #prompt user intent
        user_intent = self.prompt_unsaved_changes()

        if user_intent == "CANCEL":
            return

        if user_intent == "SAVE":
            self.save_project()

        #destroy startup window
        self.root.destroy()