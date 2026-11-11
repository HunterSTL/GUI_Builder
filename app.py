import tkinter as tk

from app_controller import AppController

def main():
    root = tk.Tk()
    root.withdraw()     #prevents flashing from applying the dark title bar by starting out withdrawn
    AppController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
