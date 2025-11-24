import os.path
import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
import ctypes

#Define standard colors
TITLE_BAR_COLOR ="#202020"
BACKGROUND_COLOR = "#404040"
BUTTON_COLOR = "#505050"
ENTRY_COLOR = "#606060"
TEXT_COLOR = "#FFFFFF"

#Stores the attribute of the GUI window and the widgets
class GUIWindow:
    def __init__(self, title, width, height, bg_color):
        self.title = title
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.widgets = []
        self.selected_widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

#Stores the attributes for the label widgets
class LabelWidget:
    id_counter = 1

    def __init__(self, x, y, text, bg, fg, anchor):
        self.id = None
        self.x = x
        self.y = y
        self.text = text
        self.bg = bg
        self.fg = fg
        self.anchor = anchor

    def create_id(self):
        self.id = "label" + str(LabelWidget.id_counter)
        LabelWidget.id_counter += 1

#Stores the attributes for the entry widgets
class EntryWidget:
    id_counter = 1

    def __init__(self, x, y, bg, fg, anchor):
        self.id = None
        self.x = x
        self.y = y
        self.bg = bg
        self.fg = fg
        self.anchor = anchor

    def create_id(self):
        self.id = "entry" + str(EntryWidget.id_counter)
        EntryWidget.id_counter += 1

#Stores the attributes for the button widgets
class ButtonWidget:
    id_counter = 1

    def __init__(self, x, y, text, bg, fg, anchor):
        self.id = None
        self.x = x
        self.y = y
        self.bg = bg
        self.fg = fg
        self.anchor = anchor

    def create_id(self):
        self.id = "button" + str(ButtonWidget.id_counter)
        ButtonWidget.id_counter += 1

class GUIBuilder:
    def __init__(self, root):
        self.root = root
        self.root.config(bg=BACKGROUND_COLOR)
        self.root.title("Tkinter GUI Builder Setup")
        self.gui_window = None
        self.canvas = None

        #Store mouse position at the time of the left click
        self.click_x = None
        self.click_y = None

        #Define icon
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.root.iconbitmap(self.icon_path)

        #Force dark mode for title bar
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.windll.user32.GetParent(self.root.winfo_id()),
            20,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int(1))
        )

        #GUI for window title
        self.label_window_title = tk.Label(root, text="Window Title:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_window_title.grid(row=0, column=0, padx=5, sticky="E")
        self.entry_window_title = tk.Entry(root, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_title.grid(row=0, column=1, columnspan=3, pady=3, sticky="EW")

        #GUI for window width
        self.label_window_width = tk.Label(root, text="Window Width:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_window_width.grid(row=1, column=0, padx=5, sticky="E")
        self.entry_window_width = tk.Entry(root, width=15, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_width.insert(0, 800)
        self.entry_window_width.grid(row=1, column=1, pady=3, sticky="EW")

        #GUI for window height
        self.label_window_height = tk.Label(root, text="Height:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_window_height.grid(row=1, column=2, padx=5, sticky="E")
        self.entry_window_height = tk.Entry(root, width=15, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_window_height.insert(0, 600)
        self.entry_window_height.grid(row=1, column=3, pady=3, sticky="EW")

        #GUI for background color
        self.label_background_color = tk.Label(root, text="Background Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_background_color.grid(row=2, column=0, padx=5, sticky="E")
        self.label_example_background = tk.Label(root, bg=BACKGROUND_COLOR)
        self.label_example_background.grid(row=2, column=1, columnspan=2, padx=1, sticky="EW")
        self.button_select_background_color = tk.Button(root, text="Select", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("background", "bg"))
        self.button_select_background_color.grid(row=2, column=3, padx=5, pady=2, sticky="EW")

        #GUI for label color
        self.label_label_color = tk.Label(root, text="Label Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_label_color.grid(row=3, column=0, padx=5, sticky="E")
        self.label_example_label = tk.Label(root, text="Example", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        self.label_example_label.grid(row=3, column=1, columnspan=2, padx=1, sticky="EW")
        self.button_select_label_background_color = tk.Button(root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("label", "bg"))
        self.button_select_label_background_color.grid(row=3, column=3, padx=5, pady=2, sticky="EW")
        self.button_select_label_text_color = tk.Button(root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("label", "fg"))
        self.button_select_label_text_color.grid(row=3, column=4, padx=5, pady=2, sticky="EW")

        #GUI for entry color
        self.label_entry_color = tk.Label(root, text="Entry Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_entry_color.grid(row=4, column=0, padx=5, sticky="E")
        self.entry_example_entry = tk.Entry(root, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.entry_example_entry.insert(0, "Example")
        self.entry_example_entry.grid(row=4, column=1, columnspan=2, sticky="EW")
        self.button_select_entry_background_color = tk.Button(root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("entry", "bg"))
        self.button_select_entry_background_color.grid(row=4, column=3, padx=5, pady=2, sticky="EW")
        self.button_select_entry_text_color = tk.Button(root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("entry", "fg"))
        self.button_select_entry_text_color.grid(row=4, column=4, padx=5, pady=2, sticky="EW")

        #GUI for button color
        self.label_button_color = tk.Label(root, text="Button Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.label_button_color.grid(row=5, column=0, padx=5, sticky="E")
        self.button_example_button_color = tk.Button(root, text="Example", bg=BUTTON_COLOR, fg=TEXT_COLOR)
        self.button_example_button_color.grid(row=5, column=1, columnspan=2, sticky="EW")
        self.button_button_background_color = tk.Button(root, text="Background", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("button", "bg"))
        self.button_button_background_color.grid(row=5, column=3, padx=5, pady=2, sticky="EW")
        self.button_button_text_color = tk.Button(root, text="Text", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=lambda: self.choose_color("button", "fg"))
        self.button_button_text_color.grid(row=5, column=4, padx=5, pady=2, sticky="EW")

        #Dictionary with selected colors
        self.colors = {
            "background": {"bg": BACKGROUND_COLOR},
            "label": {"bg": BACKGROUND_COLOR, "fg": TEXT_COLOR},
            "entry": {"bg": ENTRY_COLOR, "fg": TEXT_COLOR},
            "button": {"bg": BUTTON_COLOR, "fg": TEXT_COLOR}
        }

        #Dictionary mapping element types to example widgets
        self.example_widgets = {
            "background": self.label_example_background,
            "label": self.label_example_label,
            "entry": self.entry_example_entry,
            "button": self.button_example_button_color
        }

        #GUI for button to create new GUI window
        self.button_create_gui_window = tk.Button(root, text="Create GUI Window", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.create_gui_window)
        self.button_create_gui_window.grid(row=6, column=0, padx=5, pady=10)

    def choose_color(self, element_type, attribute):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[element_type][attribute] = color
            widget = self.example_widgets[element_type]
            widget.config({attribute: color})

    def create_gui_window(self):
        width = self.entry_window_width.get()
        height = self.entry_window_height.get()

        if not width.isdigit() or not height.isdigit():
            tk.messagebox.showerror("Input Error", "Enter an integer value for window width and height!")
            return

        title = self.entry_window_title.get()
        self.root.withdraw()

        gui_window = tk.Toplevel(self.root)
        gui_window.title(title)
        gui_window.geometry(f"{width}x{height}")

        canvas = tk.Canvas(gui_window, bg=self.colors["background"]["bg"])
        canvas.pack(fill="both", expand=True)

        #Store window data for code generation
        self.gui_window = GUIWindow(title, width, height, self.colors["background"]["bg"])
        self.canvas = canvas

        #Right click menu
        menu = tk.Menu(gui_window, tearoff=0)
        menu.add_command(label="Add Label", command=lambda: self.add_label(canvas))
        menu.add_command(label="Add Entry", command=lambda: self.add_entry(canvas))
        menu.add_command(label="Add Button", command=lambda: self.add_button(canvas))

        def show_menu(event):
            #Store mouse position at the time of left click
            self.click_x = event.x
            self.click_y = event.y
            menu.post(event.x_root, event.y_root)

        canvas.bind("<Button-3>", show_menu)

    def add_label(self, canvas):
        text = simpledialog.askstring("Label Text", "Enter label text:")
        if text:
            #Render the widget in the GUI builder
            label = tk.Label(canvas, text=text, bg=self.colors["label"]["bg"], fg=self.colors["label"]["fg"])
            canvas.create_window(self.click_x, self.click_y, window=label, anchor="sw")

            #Store widget data for code generation
            label_data = LabelWidget(self.click_x, self.click_y, text, self.colors["label"]["bg"], self.colors["label"]["fg"], "sw")
            label_data.create_id()
            self.gui_window.add_widget(label_data)

    def add_entry(self, canvas):
        #Render the widget in the GUI builder
        entry = tk.Entry(canvas, bg=self.colors["entry"]["bg"], fg=self.colors["entry"]["fg"])
        canvas.create_window(self.click_x, self.click_y, window=entry, anchor="sw")

        #Store widget data for code generation
        entry_data = EntryWidget(self.click_x, self.click_y, self.colors["entry"]["bg"], self.colors["entry"]["fg"], "sw")
        entry_data.create_id()
        self.gui_window.add_widget(entry_data)

    def add_button(self, canvas):
        text = simpledialog.askstring("Button Text", "Enter button text:")
        if text:
            #Render the widget in the GUI builder
            button = tk.Button(canvas, text=text, bg=self.colors["button"]["bg"], fg=self.colors["button"]["fg"])
            canvas.create_window(self.click_x, self.click_y, window=button, anchor="sw")

            #Store widget data for code generation
            button_data = ButtonWidget(self.click_x, self.click_y, text, self.colors["button"]["bg"], self.colors["button"]["fg"], "sw")
            button_data.create_id()
            self.gui_window.add_widget(button_data)

if __name__ == "__main__":
    root = tk.Tk()
    GUI_Builder_Menu = GUIBuilder(root)
    root.mainloop()