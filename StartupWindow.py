import tkinter as tk
from SetupWizard import SetupWizard

class StartupWindow:
    def __init__(
            self,
            root: tk.Tk,
            user_theme: dict,
            program_theme: dict,
            constants: dict
        ):
        self.root = root
        self.user_theme = user_theme
        self.program_theme = program_theme
        self.constants = constants
        self.root.config(bg=self.program_theme["background"]["color"])
        self.root.title("Tkinter GUI Builder – Startup")

        self._win_x = None
        self._win_y = None
        self._drag_start_x = None
        self._drag_start_y = None

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
            command=lambda: self.root.destroy()
        )
        close_button.pack(side="right")

    #build setup UI
    def _build_setup_ui(self):
        #open project button
        button_open_project = tk.Button(
            self.root,
            text="Open project",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=lambda: self._open_project_document()
        )
        button_open_project.pack()

        #new project button
        button_new_project = tk.Button(
            self.root,
            text="New project",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=lambda: self._new_project_document()
        )
        button_new_project.pack()

        #exit button
        button_exit = tk.Button(
            self.root,
            text="Exit",
            width=10,
            bg=self.program_theme["button"]["bg"],
            fg=self.program_theme["button"]["fg"],
            command=lambda: self._exit()
        )
        button_exit.pack()

    def _open_project_document(self):
        pass

    def _new_project_document(self):
        self.root.withdraw()                    #hide startup window
        setup_window = tk.Toplevel(self.root)   #create the setup wizard as a child
        SetupWizard(setup_window, self.user_theme, self.program_theme, self.constants)

    def _exit(self):
        self.root.destroy()