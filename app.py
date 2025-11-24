import tkinter as tk
from setup import SetupWizard

def main():
    root = tk.Tk()
    SetupWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()