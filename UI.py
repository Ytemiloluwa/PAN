import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
from tkinter import messagebox
from generator import generate_cvv, generate_pan, update_card_brand_display
from validator import validate_pan, validate_expiry_date
from import_export import import_bins, export_pans
import tkinter.filedialog as fd
from PIL import Image, ImageTk

def setup_ui(win):
    win.geometry('800x600')  # Setting the initial size of the window
    win.resizable(True, True)  # Allow the window to be resizable
    win.configure(bg='#f0f0f0')

    tabControl = ttk.Notebook(win)
    tab1 = ttk.Frame(tabControl)
    tabControl.add(tab1, text='PANS')
    tabControl.pack(expand=1, fill="both")

    mighty = ttk.LabelFrame(tab1, text=' Generate PAN(s)')
    mighty.grid(column=0, row=0, padx=8, pady=4, sticky='NSEW')

    # Configuring grid for expanding
    tab1.grid_columnconfigure(0, weight=1)
    tab1.grid_rowconfigure(0, weight=1)
    mighty.grid_columnconfigure(0, weight=1)
    mighty.grid_columnconfigure(1, weight=1)
    mighty.grid_columnconfigure(2, weight=1)
    mighty.grid_columnconfigure(3, weight=1)
    mighty.grid_rowconfigure(7, weight=1)

    # Row 0: Input BIN Label and Entry
    ttk.Label(mighty, text="Input BIN, use '?' to complete the unknown number(s):").grid(column=0, row=0, sticky='W', padx=5, pady=5, columnspan=2)
    name = tk.StringVar()
    name_entered = ttk.Entry(mighty, width=50, textvariable=name)
    name_entered.grid(column=0, row=1, sticky='W', padx=5, pady=5, columnspan=2)

    # Card brand images and checkboxes
    card_images = {
        'Visa': ImageTk.PhotoImage(Image.open('/Users/temi/Downloads/Visa.jpeg').resize((50, 50))),
        'Mastercard': ImageTk.PhotoImage(Image.open('/Users/temi/Downloads/mastercard.jpeg').resize((50, 50))),
        'American Express': ImageTk.PhotoImage(Image.open('/Users/temi/Downloads/Amex.jpeg').resize((50, 50)))
    }

    card_vars = {brand: tk.IntVar(value=0) for brand in card_images}
    card_checkboxes = {}
    for idx, (brand, image) in enumerate(card_images.items()):
        card_checkboxes[brand] = ttk.Checkbutton(mighty, text=brand, image=image, compound='left',
                                                 variable=card_vars[brand])
        card_checkboxes[brand].image = image  # Keeping a reference to the image
        card_checkboxes[brand].grid(column=idx, row=2, padx=5, pady=5, sticky='W')

    name_entered.bind('<KeyRelease>', lambda event: update_card_brand_display(name_entered, card_vars))

    # Row 1: Generate and Validate Buttons
    action_generate = ttk.Button(mighty, text="Generate", command=lambda: generate_action(name, scr, count_var))
    action_generate.grid(column=2, row=1, padx=5, pady=5)

    action_validate = ttk.Button(mighty, text="Validate", command=lambda: validate_action(name, scr))
    action_validate.grid(column=3, row=1, padx=5, pady=5)

    # Row 2: Expiry Date Label and Entry
    expiry_label = ttk.Label(mighty, text="Expiry Date (MM/YY):")
    expiry_label.grid(column=0, row=3, sticky='W', padx=5, pady=5)
    expiry_date = tk.StringVar()
    expiry_entered = ttk.Entry(mighty, width=20, textvariable=expiry_date)
    expiry_entered.grid(column=1, row=3, sticky='W', padx=5, pady=5)

    # Row 3: Validate Expiry Button
    action_validate_expiry = ttk.Button(mighty, text="Validate Expiry", command=lambda: validate_expiry_action(expiry_date.get(), scr))
    action_validate_expiry.grid(column=2, row=3, padx=5, pady=5)

    # Row 4: Count Label and Entry
    count_label = ttk.Label(mighty, text="Total PANS Generated:")
    count_label.grid(column=0, row=4, sticky='W', padx=5, pady=5)
    count = tk.IntVar(value=1)
    count_var = tk.StringVar()
    count_entered = ttk.Entry(mighty, width=20, textvariable=count_var, state='readonly')
    count_entered.grid(column=1, row=4, sticky='W', padx=5, pady=5)

    # Row 5: CVV Label and Entry
    cvv_label = ttk.Label(mighty, text="CVV:")
    cvv_label.grid(column=0, row=5, sticky='W', padx=5, pady=5)
    cvv = tk.StringVar()
    cvv_generated = ttk.Entry(mighty, width=20, textvariable=cvv)
    cvv_generated.grid(column=1, row=5, sticky='W', padx=5, pady=5)

    # Row 6: Generate CVV Button
    action_generate_cvv = ttk.Button(mighty, text="Generate CVV", command=lambda: cvv.set(generate_cvv()))
    action_generate_cvv.grid(column=2, row=5, padx=5, pady=5)

    # Row 7: Import and Export Buttons
    import_button = ttk.Button(mighty, text="Import BIN", command=lambda: import_bins(scr))
    import_button.grid(column=0, row=6, sticky='W', padx=5, pady=5)
    export_button = ttk.Button(mighty, text="Export PANs", command=lambda: export_pans(scr))
    export_button.grid(column=1, row=6, sticky='W', padx=5, pady=5)

    # Row 8: ScrolledText
    scrol_w = 80
    scrol_h = 20
    scr = scrolledtext.ScrolledText(mighty, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Helvetica", 15))
    scr.grid(column=0, row=7, sticky='NSEW', columnspan=4, padx=5, pady=5)

    # Menu bar setup
    menu_bar = Menu(win)
    win.config(menu=menu_bar)
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    help_menu = Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "PAN Generator App v1.0"))
    menu_bar.add_cascade(label="Help", menu=help_menu)

def generate_action(name, scr, count_var):
    bin_input = name.get()
    if bin_input:
        scr.delete(1.0, tk.END)
        pans = generate_pan(bin_input)
        for pan in pans:
            scr.insert(tk.END, pan + '\n')
        count_var.set('{:,}'.format(len(pans)))

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

def insert_pans_into_db(pans):
    conn = sqlite3.connect('pans.db')
    cursor = conn.cursor()
    for pan in pans:
        cursor.execute('INSERT INTO pans (pan) VALUES (?)', (pan,))
    conn.commit()
    conn.close()