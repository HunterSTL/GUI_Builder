import tkinter as tk
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

    #build startup UI
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

    def _project_callbacks(self):
        return {
            "new": self.new_project,
            "open": self.open_project,
            "save": self.save_project,
            "save_as": self.save_project_as,
            "export_json": self.export_json,
            "exit_app": self.exit_app
        }

    def _fresh_user_theme(self):
        #shallow copy works fine for dicts with 1 level; switch to deepcopy for nested structures
        return {key: value.copy() for key, value in self._user_theme.items()}

    def _launch_designer_from_project_document(self, project_document, icon):
        if self.designer:
            self.designer.top.destroy()
            self.designer = None
        self._save_path = None
        self.designer = Designer(
            parent=self.root,
            project_document=project_document,
            program_theme=self.program_theme,
            constants=self.constants,
            icon=icon,
            project_callbacks=self._project_callbacks()
        )

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


    def new_project(self):
        #prompt user intent
        user_intent = self.prompt_unsaved_changes()

        if user_intent == "CANCEL":
            return

        if user_intent == "SAVE":
            self.save_project()

        #destroy designer window
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
        print("open")

    def save_project(self):
        #use save_project_as() if save path is empty
        if not self._save_path:
            self.save_project_as()
            return

        #open .tkui file in write mode
        with open(self._save_path, "w") as file:
            file.write(str(self.designer.project_document.to_json()))

        #set app state to clean
        self.designer.set_clean()

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

        #write the contents of the ProjectDocument into the created file and close it
        file.write(str(self.designer.project_document.to_json()))
        file.close()

        #let AppController keep track of save path and last directory
        self._save_path = file.name
        last_slash_index = self._save_path.rindex("/")
        self._last_directory = self._save_path[:last_slash_index]

        #set app state to clean
        self.designer.set_clean()

    def export_json(self):
        print("export_json")

    def exit_app(self):
        #prompt user intent
        user_intent = self.prompt_unsaved_changes()

        if user_intent == "CANCEL":
            return

        if user_intent == "SAVE":
            self.save_project()

        #destroy designer window
        if self.designer:
            self.designer.top.destroy()
            self.designer = None

        #destroy startup window
        self.root.destroy()