import tkinter as tk
from Theme import USER_THEME, PROGRAM_THEME, CONSTANTS
from StartupWindow import StartupWindow

def main():
    root = tk.Tk()
    StartupWindow(root, USER_THEME, PROGRAM_THEME, CONSTANTS)
    root.mainloop()

if __name__ == "__main__":
    main()