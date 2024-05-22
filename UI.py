import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
from tkinter import messagebox
from generator import generate_pan, generate_cvv
from validator import validate_pan, detect_card_brand, validate_expiry_date

win = tk.Tk()
def setup_ui(win):
    tabControl = ttk.Notebook(win)
    tab1 = ttk.Frame(tabControl)
    tabControl.add(tab1, text='PANS')
    tabControl.pack(expand=1, fill="both")

    mighty = ttk.LabelFrame(tab1, text=' Generate PAN(s)')
    mighty.grid(column=0, row=0, padx=8, pady=4)

    ttk.Label(mighty, text="Input BIN, use '?' to complete the unknown number(s):").grid(column=0, row=0, sticky='W')

    name = tk.StringVar()
    name_entered = ttk.Entry(mighty, width=80, textvariable=name)
    name_entered.grid(column=0, row=1, sticky='W')

    action_generate = ttk.Button(mighty, text="Generate", command=lambda: generate_action(name, scr))
    action_generate.grid(column=2, row=1)

    action_validate = ttk.Button(mighty, text="Validate", command=lambda: validate_action(name, scr))
    action_validate.grid(column=1, row=1)

    scrol_w = 80
    scrol_h = 20
    scr = scrolledtext.ScrolledText(mighty, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Helvetica", 15))
    scr.grid(column=0, row=5, sticky='WE', columnspan=3)

    menu_bar = Menu(win)
    win.config(menu=menu_bar)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Exit", command=_quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    help_menu = Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "PAN Generator App v1.0"))
    menu_bar.add_cascade(label="Help", menu=help_menu)

    # Inside setup_ui function in ui.py
    expiry_label = ttk.Label(mighty, text="Expiry Date (MM/YY):")
    expiry_label.grid(column=0, row=2, sticky='W')

    expiry_date = tk.StringVar()
    expiry_entered = ttk.Entry(mighty, width=20, textvariable=expiry_date)
    expiry_entered.grid(column=1, row=2, sticky='W')

    action_validate_expiry = ttk.Button(mighty, text="Validate Expiry",
                                        command=lambda: validate_expiry_action(expiry_date.get(), scr))
    action_validate_expiry.grid(column=2, row=2)


def generate_action(name, scr):
    bin_input = name.get()
    pans = generate_pan(bin_input)
    scr.delete(1.0, tk.END)
    for pan in pans:
        scr.insert(tk.END, pan + '\n')

def validate_action(name, scr):
    pan_input = name.get()
    is_valid, message = validate_pan(pan_input)
    scr.delete(1.0, tk.END)
    scr.insert(tk.END, message)

def validate_expiry_action(expiry_date, scr):
    is_valid, message = validate_expiry_date(expiry_date)
    scr.delete(1.0, tk.END)
    scr.insert(tk.END, message)


def _quit():
    win.quit()
    win.destroy()
