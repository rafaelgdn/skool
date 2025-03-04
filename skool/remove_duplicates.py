from collections import OrderedDict
import os
import csv


def remove_duplicates(input_file, output_file):
    unique_rows = OrderedDict()

    with open(input_file, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)

        header = next(reader, None)

        for row in reader:
            row_tuple = tuple(row)

            if row_tuple not in unique_rows:
                unique_rows[row_tuple] = None

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if header:
            writer.writerow(header)
        for row in unique_rows.keys():
            writer.writerow(row)

    print(f"Arquivo CSV sem duplicatas salvo como '{output_file}'")


current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir_abspath = os.path.abspath(current_dir)
input_file = os.path.join(current_dir_abspath, "timyoon_members_followers.csv")
output_file = os.path.join(current_dir_abspath, "timyoon_members_followers2.csv")
remove_duplicates(input_file, output_file)
