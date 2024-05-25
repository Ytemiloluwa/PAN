import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
from tkinter.font import Font
from UI import setup_ui
from configuration import setup_logging

# Create instance


if __name__ == "__main__":
    win = tk.Tk()
    win.title("PAN Generator App")
    setup_ui(win)
    win.mainloop()
