import csv

def import_bins(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        bins = [row[0] for row in reader]
    return bins

def export_pans(file_path, pans):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        for pan in pans:
            writer.writerow([pan])
