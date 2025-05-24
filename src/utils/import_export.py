import csv
import tkinter.filedialog as fd
import tkinter as tk

def import_bins(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        bins = [row[0] for row in reader]
    return bins

def import_bins_action(scr):
    file_path = fd.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        bins = import_bins(file_path)
        scr.delete(1.0, tk.END)
        for bin in bins:
            scr.insert(tk.END, bin + '\n')

def export_pans_action(tree):
    file_path = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, 'w') as file:
            for row_id in tree.get_children():
                pan = tree.item(row_id, 'values')[0]
                file.write(pan + '\n')