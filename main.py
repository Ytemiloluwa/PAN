import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
from tkinter.font import Font
from UI import setup_ui
from configuration import setup_logging

# Create instance
win = tk.Tk()
win.title("PAN GENERATOR")
win.iconbitmap("/Users/temi/Downloads")

# Setup UI components

#initialize logging:
setup_logging()
# Start the GUI
win.mainloop()
