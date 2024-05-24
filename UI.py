import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
from tkinter import messagebox
from generator import generate_pan, generate_cvv
from validator import validate_pan, detect_card_brand, validate_expiry_date
from import_export import import_bins, export_pans
import tkinter.filedialog as fd


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

    expiry_label = ttk.Label(mighty, text="Expiry Date (MM/YY):")
    expiry_label.grid(column=0, row=2, sticky='W')

    expiry_date = tk.StringVar()
    expiry_entered = ttk.Entry(mighty, width=20, textvariable=expiry_date)
    expiry_entered.grid(column=1, row=2, sticky='W')

    action_validate_expiry = ttk.Button(mighty, text="Validate Expiry",
                                        command=lambda: validate_expiry_action(expiry_date.get(), scr))
    action_validate_expiry.grid(column=2, row=2)

    # adding  entries for count and CVV generation
    count_label = ttk.Label(mighty, text="Count:")
    count_label.grid(column=0, row=4, sticky='W')

    count = tk.IntVar(value=1)
    count_entered = ttk.Entry(mighty, width=20, textvariable=count)
    count_entered.grid(column=1, row=4, sticky='W')

    cvv_label = ttk.Label(mighty, text="CVV:")
    cvv_label.grid(column=0, row=5, sticky='W')

    cvv = tk.StringVar()
    cvv_generated = ttk.Entry(mighty, width=20, textvariable=cvv, state='readonly')
    cvv_generated.grid(column=1, row=5, sticky='W')

    action_generate_cvv = ttk.Button(mighty, text="Generate CVV", command=lambda: cvv.set(generate_cvv()))
    action_generate_cvv.grid(column=2, row=5)



   # including import / export functions in the UI

    import_button = ttk.Button(mighty, text="Import BINs", command=lambda: import_bins(scr))
    import_button.grid(column=0, row=6, sticky='W')

    export_button = ttk.Button(mighty, text="Export PANs", command=lambda: export_pans(scr))
    export_button.grid(column=1, row=6, sticky='W')


def generate_action(name, scr, brand, count):
    bin_input = name.get()
    card_brand = brand.get()
    pan_count = count.get()
    pans = generate_pan(bin_input, count=pan_count, brand=card_brand)
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

def import_bins_action(scr):
    file_path = fd.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        bins = import_bins(file_path)
        scr.delete(1.0, tk.END)
        for bin in bins:
            scr.insert(tk.END, bin + '\n')
def export_pans_action(scr):
    file_path = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        pans = scr.get(1.0, tk.END).strip().split('\n')
        export_pans(file_path, pans)

def _quit():
    win.quit()
    win.destroy()
    exit()
